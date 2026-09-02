#!/usr/bin/env python3
"""Deterministic graders for the sprint-digest evals.

Pure functions over (produced HTML, MCP call trace, answer key). No model calls,
no filesystem beyond what is passed in — so `test_graders.py` can exercise every
failure mode for free, and a bad grader gets caught before it burns a run.

Each grader returns a Result: a 0..1 score, a weight, and a note explaining the
score in terms a human can act on. `hard=True` means a failure is a fabrication
or contract breach serious enough that the run should not be called a pass no
matter what the other graders say.

Structural graders read the HTML shape defined in the skill's digest-contract.md.
If you change that contract, update these alongside it — that coupling is
deliberate, it is what stops the contract from silently rotting.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

KEY_RE = re.compile(r"\bAE-\d+\b")
# "lead" is what real digests tend to call the headline section; both map to the
# same bucket, so which one matches first does not matter.
SECTION_WORDS = ("headline", "lead", "increment", "watch", "appendix", "omission",
                 "context", "method", "coverage", "source")


@dataclass
class Result:
    name: str
    score: float          # 0..1
    weight: float = 1.0
    note: str = ""
    hard: bool = False    # a zero here fails the run outright

    def as_dict(self) -> dict:
        return {"name": self.name, "score": round(self.score, 3),
                "weight": self.weight, "note": self.note, "hard": self.hard}


# --- HTML structure ----------------------------------------------------------

@dataclass
class Block:
    """One <section> or <article>, tagged with whatever contract word its
    class/id suggests, plus the text and issue keys inside it."""
    tag: str
    label: str
    text: str = ""
    keys: list = field(default_factory=list)
    depth: int = 0
    ancestors: list = field(default_factory=list)   # enclosing labels, outermost first


class _Segmenter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self.stack: list[Block] = []
        self._skip = 0  # inside <script>/<style>

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
            return
        if tag not in ("section", "article", "div", "aside"):
            return
        a = dict(attrs)
        hint = " ".join([a.get("class", ""), a.get("id", ""),
                         a.get("data-bucket", "")]).lower()
        label = next((w for w in SECTION_WORDS if w in hint), "")
        if not label and tag == "div":
            return  # untagged divs are noise, not structure
        b = Block(tag=tag, label=label, depth=len(self.stack),
                  ancestors=[a.label for a in self.stack if a.label])
        self.blocks.append(b)
        self.stack.append(b)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
            return
        if tag in ("section", "article", "div", "aside") and self.stack:
            if self.stack[-1].tag == tag:
                self.stack.pop()

    def handle_data(self, data):
        if self._skip:
            return
        for b in self.stack:
            b.text += data
        for b in self.stack:
            b.keys.extend(k for k in KEY_RE.findall(data) if k not in b.keys)


def segment(html: str) -> list[Block]:
    p = _Segmenter()
    p.feed(html)
    return p.blocks


def visible_text(html: str) -> str:
    """HTML with script/style bodies and tags removed."""
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


# Strongest signal first. "omit" is weakest because the appendix lists everything,
# including work that was also (wrongly) promoted into the lead — and that promotion
# is the thing worth reporting.
BUCKET_PRECEDENCE = ("watch", "headline", "increment", "omit")
LABEL_TO_BUCKET = {
    "watch": "watch", "headline": "headline", "lead": "headline",
    "increment": "increment", "context": "increment",
    "omission": "omit", "appendix": "omit", "coverage": "omit",
    "source": "omit", "method": "omit",
}


def bucket_of(blocks: list[Block], key: str) -> str:
    """Which contract section a key lands in, resolved over every enclosing block."""
    labels = set()
    for b in blocks:
        if key in b.keys:
            labels.update(b.ancestors)
            if b.label:
                labels.add(b.label)
    buckets = {LABEL_TO_BUCKET[l] for l in labels if l in LABEL_TO_BUCKET}
    for bucket in BUCKET_PRECEDENCE:
        if bucket in buckets:
            return bucket
    return "absent"


# --- graders -----------------------------------------------------------------

# Naming a metric in order to say it is unavailable is the behaviour we want, not
# the behaviour we are hunting. Without this, the gate punishes exactly the
# fail-closed disclaimer the contract asks for — and iteration would learn to drop it.
NEGATION_CUES = re.compile(
    r"\b(not|no|never|without|absent|unavailable|missing|lack\w*|cannot|can't|"
    r"isn't|aren't|weren't|wasn't|don't|doesn't|didn't|unsupported|unverified|"
    r"n/a|omitted|excluded|declined|unable)\b")


SENTENCE_BREAK = re.compile(r"[.!?;\n]")


def _is_disclaimed(text: str, start: int, end: int) -> bool:
    """Negation only counts inside the match's own sentence. A fixed character
    window leaks across boundaries: an appendix disclaimer ending '...no fetched
    series supports one.' would otherwise excuse the very next sentence asserting
    a story-point count."""
    lo = max(0, start - 200)
    breaks = [m.end() for m in SENTENCE_BREAK.finditer(text, lo, start)]
    sent_start = breaks[-1] if breaks else lo
    after = SENTENCE_BREAK.search(text, end, min(len(text), end + 200))
    sent_end = after.start() if after else min(len(text), end + 200)
    return bool(NEGATION_CUES.search(text[sent_start:sent_end]))


def g_no_invention(html: str, key: dict) -> Result:
    """Hard gate. The fixtures carry no story points, capacity, or money, so an
    asserted claim about any of them was fabricated, not merely unsupported."""
    text = visible_text(html).lower()
    asserted, disclaimed = [], []
    for pat in key["invention_bait"]["forbidden_patterns"]:
        # Every occurrence has to be checked: a disclaimer in the appendix must not
        # excuse the same term asserted in the lead.
        hits = list(re.finditer(pat, text))
        if not hits:
            continue
        if all(_is_disclaimed(text, m.start(), m.end()) for m in hits):
            disclaimed.append(pat)
        else:
            asserted.append(pat)
    if asserted:
        return Result("no_invention", 0.0, 3.0, hard=True,
                      note="fabricated claim asserted: %s" % ", ".join(sorted(set(asserted))))
    if disclaimed:
        return Result("no_invention", 1.0, 3.0,
                      note="absent fields named only to disclaim them (%s) — correct"
                           % ", ".join(sorted(set(disclaimed))))
    return Result("no_invention", 1.0, 3.0, note="no fabricated metric vocabulary")


def g_counts_reconcile(html: str, key: dict) -> Result:
    """The appendix has to account for every issue in the sprint."""
    blocks = [b for b in segment(html)
              if b.label in ("appendix", "coverage", "method", "source")]
    hay = (" ".join(b.text for b in blocks) or visible_text(html))
    nums = set(re.findall(r"\b\d+\b", hay))
    want_total = str(key["total_issues"])
    missing = []
    if want_total not in nums:
        missing.append("total=%s" % want_total)
    for status, n in key["status_counts"].items():
        if str(n) not in nums:
            missing.append("%s=%d" % (status, n))
    if missing:
        return Result("counts_reconcile", 0.0, 2.0,
                      note="appendix does not reconcile; missing %s" % ", ".join(missing))
    return Result("counts_reconcile", 1.0, 2.0,
                  note="total and per-status counts all present in the appendix")


def g_cluster_unity(html: str, key: dict) -> Result:
    """Related keys with one outcome must land in one increment, not one row each."""
    blocks = segment(html)
    scored, notes = [], []
    for c in key["clusters"]:
        if not c.get("must_be_one_increment") or len(c["keys"]) < 2:
            continue
        containers = [b for b in blocks if b.tag == "article"]
        if not containers:  # no <article>; fall back to labelled leaf blocks
            containers = [b for b in blocks
                          if b.label in ("increment", "headline") and b.depth > 0]
        best = max((len(set(c["keys"]) & set(b.keys)) for b in containers), default=0)
        scored.append(best / len(c["keys"]))
        notes.append("%s: %d/%d keys share one block" % (c["id"], best, len(c["keys"])))
    if not scored:
        return Result("cluster_unity", 1.0, 0.0, note="no multi-key cluster in this key")
    avg = sum(scored) / len(scored)
    return Result("cluster_unity", avg, 2.0, note="; ".join(notes))


def g_bucket_placement(html: str, key: dict) -> Result:
    """Each planted increment has to land in the bucket the evidence supports."""
    blocks = segment(html)
    hits, notes = 0, []
    for c in key["clusters"]:
        want = [c["expect_bucket"]] + c.get("also_acceptable", [])
        got = bucket_of(blocks, c["keys"][0])
        ok = got in want or (got == "increment" and
                             {"headline", "supporting"} & set(want))
        hits += bool(ok)
        notes.append("%s: %s (want %s)%s" % (c["id"], got, "/".join(want),
                                             "" if ok else "  <-- MISS"))
    return Result("bucket_placement", hits / len(key["clusters"]), 2.0,
                  note="; ".join(notes))


def g_omit_discipline(html: str, key: dict) -> Result:
    """Routine delivery must not be dressed up as an increment."""
    blocks = segment(html)
    promoted = []
    for o in key["omit_expected"]:
        for k in o["keys"]:
            if bucket_of(blocks, k) in ("increment", "headline"):
                promoted.append(k)
    total = sum(len(o["keys"]) for o in key["omit_expected"])
    score = 1.0 - (len(promoted) / total)
    note = ("routine work promoted to an increment: %s" % ", ".join(promoted)
            if promoted else "routine delivery kept out of the lead")
    return Result("omit_discipline", score, 2.0, note=note)


def g_claim_labels(html: str, key: dict) -> Result:
    """Every increment shows its claim strength; genuinely open items say so."""
    text = visible_text(html).lower()
    present = [w for w in ("observed", "synthesis", "unresolved") if w in text]
    score = len(present) / 3.0 if len(present) < 2 else (0.7 + 0.3 * (len(present) == 3))
    notes = ["labels used: %s" % (", ".join(present) or "none")]

    needs = [c for c in key["clusters"] if c.get("requires_unresolved_label")]
    if needs:
        blocks = segment(html)
        ok = 0
        for c in needs:
            owner = [b for b in blocks if c["keys"][0] in b.keys]
            if any("unresolved" in b.text.lower() for b in owner) or \
               bucket_of(blocks, c["keys"][0]) in ("watch", "omit", "absent"):
                ok += 1
            else:
                notes.append("%s asserted without an unresolved label" % c["id"])
        score = (score + ok / len(needs)) / 2
    return Result("claim_labels", score, 1.5, note="; ".join(notes))


def g_evidence_links(html: str, key: dict) -> Result:
    """Keys cited as claims should be clickable back to the evidence."""
    linked = set(re.findall(r"href=\"[^\"]*?/browse/(AE-\d+)", html))
    cited = set()
    for c in key["clusters"]:
        if c["expect_bucket"] in ("headline", "supporting", "watch"):
            cited.update(c["keys"])
    if not cited:
        return Result("evidence_links", 1.0, 1.0, note="nothing to link")
    hit = len(cited & linked)
    return Result("evidence_links", hit / len(cited), 1.0,
                  note="%d/%d story-bearing keys link to /browse/" % (hit, len(cited)))


def g_conclusion_titles(html: str, _key: dict) -> Result:
    """h1/h2 must be conclusions, not labels. 'Sprint digest' is the failure."""
    heads = [re.sub(r"<[^>]+>", "", h).strip()
             for h in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, flags=re.S | re.I)]
    if not heads:
        return Result("conclusion_titles", 0.0, 1.5, note="no h1/h2 found")
    label_re = re.compile(
        r"^(sprint\s+digest|digest|increments?|summary|overview|watch|appendix|"
        r"chart\s*\d*|sprint\s+\S+|results?|highlights?)\W*$", re.I)
    bad = [h for h in heads if label_re.match(h)]
    # Section wrappers are allowed to be labels; increment/page titles are not.
    scoreable = [h for h in heads if h.lower().strip(" :") not in
                 ("watch", "appendix", "increments", "increment", "context")]
    bad = [h for h in bad if h in scoreable]
    if not scoreable:
        return Result("conclusion_titles", 0.0, 1.5, note="no titles carrying a claim")
    score = 1.0 - len(bad) / len(scoreable)
    note = ("label-style titles: %s" % "; ".join(bad[:3]) if bad
            else "titles read as conclusions (e.g. %r)" % scoreable[0][:70])
    return Result("conclusion_titles", score, 1.5, note=note)


def g_lead_is_not_a_dump(html: str, _key: dict) -> Result:
    """The lead should open on what became true, not on how many tickets closed."""
    blocks = segment(html)
    lead = next((b.text for b in blocks if b.label in ("headline", "lead")), "")
    if not lead:
        lead = visible_text(html)[:1200]
    lead = " ".join(lead.split())[:1200]
    # Every branch requires a work noun. "closed 2026-08-24" is a sprint end date,
    # not a throughput brag, and matching it was sending the score the wrong way.
    work = r"(?:issues?|tickets?|stories|items?|story|points?)"
    dumpy = re.findall(
        r"\b\d+\s+%s\b|"
        r"\b(?:completed|closed|delivered|resolved|shipped)\s+\d+\s+%s\b|"
        r"\b\d+\s*(?:of|/|out of)\s*\d+\s+%s\b" % (work, work, work),
        lead, flags=re.I)
    if dumpy:
        return Result("lead_is_not_a_dump", 0.0, 1.5,
                      note="lead counts tickets: %s" % "; ".join(dumpy[:3]))
    return Result("lead_is_not_a_dump", 1.0, 1.5, note="lead leads with an outcome")


def g_increment_count(html: str, _key: dict) -> Result:
    """Contract caps the digest at 3-5 increments; more means it is a list again."""
    blocks = segment(html)
    lead = [b for b in blocks
            if (b.tag == "article" or (b.label == "increment" and b.depth > 0))
            and not ({"watch", "appendix", "omission"} & set(b.ancestors))]
    n = len(lead)
    if n == 0:
        return Result("increment_count", 0.0, 1.0, note="no increment blocks found")
    if 3 <= n <= 5:
        return Result("increment_count", 1.0, 1.0, note="%d increments" % n)
    if n in (2, 6):
        return Result("increment_count", 0.6, 1.0, note="%d increments (contract: 3-5)" % n)
    return Result("increment_count", 0.2, 1.0, note="%d increments (contract: 3-5)" % n)


# --- trace graders -----------------------------------------------------------

def g_pagination(trace: list, key: dict) -> Result:
    """Wide sprints need more than one page; the mock caps a call at 50."""
    if not key.get("requires_pagination"):
        return Result("pagination", 1.0, 0.0, note="not required for this sprint")
    starts = {int(c["args"].get("startAt", c["args"].get("start_at", 0)) or 0)
              for c in trace if c["tool"] == "jira_get_sprint_issues"}
    seen = min(len(starts) * 50, key["total_issues"])
    if len(starts) >= 2:
        return Result("pagination", 1.0, 2.0,
                      note="paginated: startAt %s" % sorted(starts))
    return Result("pagination", 0.0, 2.0, hard=True,
                  note="single page — saw at most %d of %d issues"
                       % (seen, key["total_issues"]))


def g_evidence_targeting(trace: list, key: dict) -> Result:
    """Step 2 says fetch detail for candidates, not for every ticket. Full fan-out
    is not wrong output, but it is the expensive habit worth watching."""
    fetched = {c["args"].get("issue_key") for c in trace if c["tool"] == "jira_get_issue"}
    fetched.discard(None)
    total = key["total_issues"]
    if not fetched:
        return Result("evidence_targeting", 0.0, 1.0, hard=True,
                      note="no jira_get_issue calls — comments were never read")
    story = {k for c in key["clusters"] for k in c["keys"]}
    covered = len(story & fetched) / len(story)
    ratio = len(fetched) / total
    waste = 1.0 if ratio <= 0.6 else max(0.0, 1.0 - (ratio - 0.6) / 0.4)
    return Result("evidence_targeting", 0.7 * covered + 0.3 * waste, 1.0,
                  note="detail fetched for %d/%d issues; %d/%d story-bearing keys covered"
                       % (len(fetched), total, len(story & fetched), len(story)))


HTML_GRADERS = [g_no_invention, g_counts_reconcile, g_cluster_unity,
                g_bucket_placement, g_omit_discipline, g_claim_labels,
                g_evidence_links, g_conclusion_titles, g_lead_is_not_a_dump,
                g_increment_count]
TRACE_GRADERS = [g_pagination, g_evidence_targeting]


def grade(html: str, trace: list, key: dict) -> dict:
    results = [g(html, key) for g in HTML_GRADERS]
    results += [g(trace, key) for g in TRACE_GRADERS]
    weighted = sum(r.score * r.weight for r in results)
    total_w = sum(r.weight for r in results) or 1.0
    hard_fail = [r.name for r in results if r.hard and r.score == 0.0]
    return {
        "score": round(weighted / total_w, 3),
        "hard_fail": hard_fail,
        "results": [r.as_dict() for r in results],
    }


if __name__ == "__main__":
    import sys
    html = open(sys.argv[1]).read()
    key = json.load(open(sys.argv[2]))
    trace = [json.loads(l) for l in open(sys.argv[3])] if len(sys.argv) > 3 else []
    print(json.dumps(grade(html, trace, key), indent=2))
