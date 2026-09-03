# 04: Apply the portability contract across the canonical surface

**What to build:** Every skill on the canonical surface conforms to ADR-0004. This is one edit per
skill, not two passes across all of them: adding a skill's declarations and removing its relative
links to Library documents are the same change, and doing them separately leaves each skill
half-converted in between.

Three skills link the context gate with a depth that resolves above the repo root. They stop
linking it and instead declare it: what the document is, where it is expected, and what to do when
it is absent. The gate itself stays single-sourced — it is not copied into the skills, which is
what its own opening line forbids and what would guarantee three copies drifting apart.

Five skills make path claims that resolve only in a consuming repo. Those become declared
expectations rather than assertions about a directory that is not there.

`sprint-digest`'s boundary table names three siblings; none is on the canonical surface, and two
exist only in work repos. Under the contract that is legitimate — but it has to be declared as an
expectation rather than read as a broken reference.

One coupling to respect: ADR-0003 keeps `labs/sprint-digest` as a candidate copy of the stable
skill, and the candidate carries the same defects. It moves in step, or the next eval run compares
two arms that differ by more than the change under test.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] Each of the six canonical skills has a "Requires from the consuming repo" section, in the
      shape ADR-0004 specifies
- [ ] No skill links a Library document by relative path; each names the document, its expected
      location, and the behaviour when it is missing
- [ ] `docs/agents/context-gate.md` remains the single source for the gate and is not duplicated
      into any skill
- [ ] `sprint-digest`'s boundary-table siblings are declared as consuming-repo expectations
- [ ] The `labs/sprint-digest` candidate copy receives the same changes in the same increment, so
      the two arms still differ only where iteration intends
- [ ] The validator reports zero R4.3 findings and zero R8.6 findings over the canonical surface
- [ ] No skill's behaviour changes: these are structural edits under the tier rule, and no rung-2
      or rung-3 run is required to land them
