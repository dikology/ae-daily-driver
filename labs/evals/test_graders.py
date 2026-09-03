"""Tests for graders.py.

A grader that cannot fail is worse than no grader — it turns every run green and
hides the regression you built the harness to catch. So each grader gets both a
digest that should satisfy it and a mutant that should trip it.

The fixtures are the real HOSPA sprint (labs/evals/fixtures/, gitignored); run
`python3 confidential/build_hospa_fixture.py` if keys/hospa-26-09-04.json is missing.

    python3 -m pytest labs/evals/test_graders.py -q
"""

import json
from pathlib import Path

import pytest

from graders import (
    bucket_of, grade, segment, visible_text,
    g_bucket_placement, g_claim_labels, g_cluster_unity, g_conclusion_titles,
    g_counts_reconcile, g_evidence_links, g_evidence_targeting, g_increment_count,
    g_lead_is_not_a_dump, g_no_invention, g_omit_discipline, g_pagination,
)

KEYS = Path(__file__).parent / "fixtures" / "keys"
BROWSE = "https://tasks.sberdevices.ru/browse"


@pytest.fixture
def key():
    return json.loads((KEYS / "hospa-26-09-04.json").read_text())


def browse(k):
    return f'<a href="{BROWSE}/{k}">{k}</a>'


# Story-bearing keys, grouped by the increment they belong in.
MIGRATION = ("HOSPA-1634", "HOSPA-1635", "HOSPA-1636")
BUBBLE = "HOSPA-1454"
SENSORS = "HOSPA-1609"
PRIME = ("HOSPA-1682", "HOSPA-1704")
DAG = "HOSPA-1744"
DEVDEV = ("HOSPA-1666", "HOSPA-1667", "HOSPA-1699", "HOSPA-1700")
VISITS = "HOSPA-1725"

GOOD = """
<h1>Прогнозные и отельные витрины умного дома переехали в sandbox_homeos без простоя у потребителей</h1>
<section class="headline">
  <p>Песочница аналитики умного дома сменила схему: история пролита и сверена,
  пайплайны в Airflow и источники двенадцати дашбордов Metabase переключены за один
  спринт. MAU/MAR, интенты виртуального ассистента и воронки витрин продолжают
  считаться, потребителям ничего править вручную не пришлось.</p>
</section>
<section class="increments">
  <article class="increment">
    <h2>Витрины умного дома переехали в sandbox_homeos, дашборды не заметили</h2>
    <p class="claim-meta">observed</p>
    <div class="what-changed">Проливка глубины, переключение DAG в Airflow и смена источника у 12 чартов Metabase — один переезд.</div>
    <div class="evidence">{m0} {m1} {m2} — сверка с sandbox сошлась, расхождение менее одной десятой процента</div>
    <p class="why-it-matters">Потребители аналитики отелей и умного дома продолжают работать без ручных правок.</p>
  </article>
  <article class="increment">
    <h2>A/B шторки ассистента закрыт: раскатка на всех пользователей согласована</h2>
    <p class="claim-meta">observed</p>
    <div class="evidence">{bubble} — закрытие assistant_dsha.close_response_bubble снизилось значимо, guardrail-метрики не выросли</div>
    <p class="why-it-matters">Продуктовая команда ассистента уходит в полную раскатку на основании статзначимого эксперимента.</p>
  </article>
  <article class="increment">
    <h2>Датчики протечки и дыма теперь считаются активными, когда просто на связи</h2>
    <p class="claim-meta">synthesis</p>
    <div class="evidence">{sensors} — дока в Confluence обновлена, MR в dbt-smarthome готов</div>
    <p class="why-it-matters">Меняется базовая метрика активных устройств умного дома.</p>
  </article>
  <article class="increment">
    <h2>Контроль отключения рекламы в Прайме сведён к Лончеру и готов к поставке в Банк</h2>
    <p class="claim-meta">synthesis</p>
    <div class="evidence">{p0} {p1} — скоуп сужен до Лончера и события BrainServiceStarted, витрина в существующей поставке</div>
    <p class="why-it-matters">У регуляторной отчётности перед Банком появился реализуемый путь.</p>
  </article>
</section>
<section class="watch">
  <h2>На контроле</h2>
  <article class="increment">
    <h2>DAG-и dbt smarthome и dbt clickhouse не запускаются — риск дыр в данных</h2>
    <p class="claim-meta">observed</p>
    <div class="evidence">{dag}</div>
    <p class="ask">Нужен человек: починить запуск и вручную сверить пропуски за дни падения.</p>
  </article>
  <article class="increment">
    <h2>Витрина активаций device-device готова, но бэкфилл заморожен на сверке CH и DWS</h2>
    <p class="claim-meta">observed</p>
    <div class="evidence">{d0} {d1} {d2} {d3} — дневная витрина dbt_ch_homeos_daily крутится, остальное в Need Info</div>
    <p class="ask">Нужно решение по расхождению CH и DWS за 2026-08-18.</p>
  </article>
  <article class="increment">
    <h2>Массивы watch_ids/goals_id ждут восстановления схемы из OpenMetadata</h2>
    <p class="claim-meta">unresolved</p>
    <div class="evidence">{visits}</div>
    <p class="ask">Ручную таблицу нужно поднять в ch_dbt из OpenMetadata.</p>
  </article>
</section>
<section class="appendix">
  <h2>Приложение</h2>
  <p>Охват: 83 задачи — 32 Done, 16 In Review, 15 In Progress, 12 Backlog, 5 Open, 3 Need Info.
  Выгружено постранично (startAt 0 и 50). Полей story points и стоимости в спринте нет.</p>
  <table class="omissions">
    <tr><td>HOSPA-1747</td><td>omit</td><td>Рутинный фикс order_by.</td></tr>
    <tr><td>HOSPA-1714</td><td>omit</td><td>Еженедельная ручная выгрузка DG в DWS.</td></tr>
    <tr><td>HOSPA-1685</td><td>omit</td><td>Еженедельная ручная выгрузка DG в DWS.</td></tr>
    <tr><td>HOSPA-1562</td><td>omit</td><td>Наведение порядка в своих задачах.</td></tr>
    <tr><td>HOSPA-1743</td><td>omit</td><td>Разовая выгрузка для конкретного заказчика.</td></tr>
  </table>
</section>
""".format(m0=browse(MIGRATION[0]), m1=browse(MIGRATION[1]), m2=browse(MIGRATION[2]),
           bubble=browse(BUBBLE), sensors=browse(SENSORS),
           p0=browse(PRIME[0]), p1=browse(PRIME[1]), dag=browse(DAG),
           d0=browse(DEVDEV[0]), d1=browse(DEVDEV[1]), d2=browse(DEVDEV[2]), d3=browse(DEVDEV[3]),
           visits=browse(VISITS))

STORY_KEYS = list(MIGRATION) + [BUBBLE, SENSORS] + list(PRIME) + [DAG] + list(DEVDEV) + [VISITS]
GOOD_TRACE = (
    [{"tool": "jira_get_sprint_issues", "args": {"sprint_id": "10286", "startAt": 0}},
     {"tool": "jira_get_sprint_issues", "args": {"sprint_id": "10286", "startAt": 50}}]
    + [{"tool": "jira_get_issue", "args": {"issue_key": k}} for k in STORY_KEYS]
)


# --- the happy path ----------------------------------------------------------

def test_good_digest_scores_high(key):
    out = grade(GOOD, GOOD_TRACE, key)
    assert out["hard_fail"] == [], json.dumps(out, indent=2, ensure_ascii=False)
    assert out["score"] >= 0.9, json.dumps(out, indent=2, ensure_ascii=False)


# --- one mutant per grader ---------------------------------------------------

def test_invented_metrics_hard_fail(key):
    bad = GOOD.replace("<p>Песочница аналитики",
                       "<p>Скорость команды выросла до 34 story points, экономический эффект — 2 млн руб. Песочница аналитики")
    r = g_no_invention(bad, key)
    assert r.score == 0.0 and r.hard
    assert "story" in r.note
    assert "no_invention" in grade(bad, GOOD_TRACE, key)["hard_fail"]


def test_clean_digest_passes_invention_gate(key):
    assert g_no_invention(GOOD, key).score == 1.0


def test_russian_disclaimer_is_not_invention(key):
    """Naming the absent field to say it is absent — in Russian — is correct."""
    html = GOOD + ("<section class='appendix'><p>График velocity не построен: поля "
                   "story points в Jira нет. Денежный эффект не приводим — финансовых "
                   "полей в спринте нет.</p></section>")
    r = g_no_invention(html, key)
    assert r.score == 1.0, r.note
    assert "disclaim" in r.note


def test_counts_must_reconcile(key):
    bad = GOOD.replace("83 задачи — 32 Done, 16 In Review, 15 In Progress, 12 Backlog, 5 Open, 3 Need Info",
                       "насыщенный спринт по всей команде")
    assert g_counts_reconcile(bad, key).score == 0.0
    assert g_counts_reconcile(GOOD, key).score == 1.0


def test_split_cluster_is_penalised(key):
    """The three migration keys in three separate increments is the fragmentation
    failure this cluster exists to catch."""
    bad = GOOD.replace(
        '<div class="evidence">%s %s %s' % (browse(MIGRATION[0]), browse(MIGRATION[1]), browse(MIGRATION[2])),
        '<div class="evidence">%s' % browse(MIGRATION[0]))
    bad = bad.replace('<section class="watch">', """
  <article class="increment"><h2>Историю пролили</h2>
    <div class="evidence">%s</div></article>
  <article class="increment"><h2>Даг переключили</h2>
    <div class="evidence">%s</div></article>
</section>
<section class="watch">""" % (browse(MIGRATION[1]), browse(MIGRATION[2])), 1)
    assert g_cluster_unity(bad, key).score < g_cluster_unity(GOOD, key).score
    assert g_cluster_unity(GOOD, key).score == 1.0


def test_buried_ab_result_is_penalised(key):
    """HOSPA-1454 dropped to the omissions table is the 'generic title hid the
    product decision' failure."""
    bad = GOOD.replace(
        '  <article class="increment">\n'
        '    <h2>A/B шторки ассистента закрыт: раскатка на всех пользователей согласована</h2>\n'
        '    <p class="claim-meta">observed</p>\n'
        '    <div class="evidence">%s — закрытие assistant_dsha.close_response_bubble снизилось значимо, guardrail-метрики не выросли</div>\n'
        '    <p class="why-it-matters">Продуктовая команда ассистента уходит в полную раскатку на основании статзначимого эксперимента.</p>\n'
        '  </article>\n' % browse(BUBBLE), "")
    bad = bad.replace("<tr><td>HOSPA-1747</td>",
                      "<tr><td>HOSPA-1454</td><td>omit</td><td>Просто посчитали.</td></tr>\n    <tr><td>HOSPA-1747</td>")
    assert g_bucket_placement(bad, key).score < g_bucket_placement(GOOD, key).score


def test_blocked_work_belongs_in_watch(key):
    blocks = segment(GOOD)
    assert bucket_of(blocks, DAG) == "watch"
    assert bucket_of(blocks, MIGRATION[0]) == "increment"
    assert bucket_of(blocks, "HOSPA-1747") == "omit"


def test_routine_work_promoted_is_penalised(key):
    bad = GOOD.replace('<div class="evidence">%s</div>' % browse(DAG),
                       '<div class="evidence">%s %s</div>' % (browse(DAG), browse("HOSPA-1747")))
    bad = bad.replace('<section class="watch">', '<section class="increments">', 1)
    assert g_omit_discipline(bad, key).score < 1.0
    assert g_omit_discipline(GOOD, key).score == 1.0


def test_unlabelled_open_claim_is_penalised(key):
    bad = GOOD.replace('<p class="claim-meta">unresolved</p>',
                       '<p class="claim-meta">observed</p>')
    assert g_claim_labels(bad, key).score < g_claim_labels(GOOD, key).score


def test_missing_browse_links_penalised(key):
    bad = GOOD.replace('href="%s/' % BROWSE, 'href="#')
    assert g_evidence_links(bad, key).score == 0.0
    assert g_evidence_links(GOOD, key).score == 1.0


def test_label_titles_penalised(key):
    bad = GOOD.replace(
        "<h1>Прогнозные и отельные витрины умного дома переехали в sandbox_homeos без простоя у потребителей</h1>",
        "<h1>Дайджест спринта</h1>")
    bad = bad.replace("<h2>Витрины умного дома переехали в sandbox_homeos, дашборды не заметили</h2>",
                      "<h2>Инкремент 1</h2>")
    assert g_conclusion_titles(bad, key).score < g_conclusion_titles(GOOD, key).score
    assert g_conclusion_titles(GOOD, key).score == 1.0


def test_status_dump_lead_is_caught(key):
    bad = GOOD.replace(
        "<p>Песочница аналитики умного дома сменила схему: история пролита и сверена,",
        "<p>За спринт закрыто 32 задачи. Песочница аналитики умного дома сменила схему,")
    assert g_lead_is_not_a_dump(bad, key).score == 0.0
    assert g_lead_is_not_a_dump(GOOD, key).score == 1.0


def test_too_many_increments_penalised(key):
    extra = "".join('<article class="increment"><h2>Ещё кое-что произошло номер %d</h2>'
                    '<div class="evidence">HOSPA-%d</div></article>' % (i, 900 + i)
                    for i in range(6))
    bad = GOOD.replace('<section class="watch">', extra + '<section class="watch">', 1)
    assert g_increment_count(bad, key).score < g_increment_count(GOOD, key).score


def test_pagination_required_on_this_sprint(key):
    one_page = [{"tool": "jira_get_sprint_issues", "args": {"sprint_id": "10286", "startAt": 0}}]
    two_page = one_page + [{"tool": "jira_get_sprint_issues",
                            "args": {"sprint_id": "10286", "startAt": 50}}]
    assert g_pagination(one_page, key).score == 0.0
    assert g_pagination(one_page, key).hard
    assert g_pagination(two_page, key).score == 1.0
    small = {"requires_pagination": False, "total_issues": 12}
    assert g_pagination(one_page, small).weight == 0.0  # not scored on a one-page sprint


def test_never_reading_comments_hard_fails(key):
    trace = [{"tool": "jira_get_sprint_issues", "args": {"sprint_id": "10286", "startAt": 0}}]
    r = g_evidence_targeting(trace, key)
    assert r.score == 0.0 and r.hard


def test_fanning_out_to_every_ticket_scores_below_targeted(key):
    everything = GOOD_TRACE + [{"tool": "jira_get_issue", "args": {"issue_key": "HOSPA-%d" % k}}
                               for k in range(1500, 1560)]
    assert g_evidence_targeting(everything, key).score < g_evidence_targeting(GOOD_TRACE, key).score


# --- helpers -----------------------------------------------------------------

def test_visible_text_drops_script_and_style():
    html = "<style>.x{color:red}</style><script>var burndown=1;</script><p>hello</p>"
    t = visible_text(html).lower()
    assert "hello" in t and "burndown" not in t and "color" not in t


def test_script_contents_do_not_trip_invention_gate(key):
    """Chart data in a <script> block is data, not a claim."""
    html = GOOD.replace("</section>", "<script>const velocity=[1,2];</script></section>", 1)
    assert g_no_invention(html, key).score == 1.0


# --- regressions: false positives to stay dead -----------------------------------

REAL_DISCLAIMER = (
    "<section class='appendix'><p>Всего в спринте 83. Это статусные счётчики. "
    "Story points, burndown и ёмкость команды не выгружались и не заявляются. "
    "График не приводим — ни одна выгруженная серия его не обосновывает.</p></section>")


def test_disclaiming_absent_metrics_is_not_invention(key):
    r = g_no_invention(GOOD + REAL_DISCLAIMER, key)
    assert r.score == 1.0, r.note
    assert "disclaim" in r.note


def test_asserted_metric_still_fails_next_to_a_disclaimer(key):
    html = (GOOD + REAL_DISCLAIMER +
            "<p>Отдельно: команда сожгла 34 story points против ёмкости в 40.</p>")
    assert g_no_invention(html, key).score == 0.0


def test_sprint_end_date_is_not_a_ticket_count(key):
    html = GOOD.replace(
        '<section class="headline">',
        '<section class="headline"><p>Окно 2026-08-24 — 2026-09-04.</p>')
    assert g_lead_is_not_a_dump(html, key).score == 1.0


def test_lead_class_is_treated_as_headline(key):
    html = GOOD.replace('<section class="headline">', '<section class="lead">')
    assert g_lead_is_not_a_dump(html, key).score == 1.0
    bad = html.replace("<p>Песочница аналитики умного дома сменила схему:",
                       "<p>Мы закрыли 32 задачи. Песочница аналитики умного дома сменила схему,")
    assert g_lead_is_not_a_dump(bad, key).score == 0.0


def test_invention_patterns_are_word_anchored(key):
    """An unanchored 'fte' matches inside 'after'; an unanchored 'roi' inside a
    Russian word. That false positive hard-failed a clean digest once."""
    html = GOOD.replace("<p>Песочница аналитики",
                        "<p>После доработки геройский рефакторинг стал мягче. Песочница аналитики")
    assert g_no_invention(html, key).score == 1.0
