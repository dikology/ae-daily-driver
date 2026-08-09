# Showcase layout: `skills/` and `mcp/` at repo root

Presentable Library content lives in root-level `skills/` and `mcp/` so the repo reads as a stealable kit. Agent runtimes (e.g. `.cursor/`) get copies as needed. We rejected `.cursor`-only as the showcase surface — that buries the kit — and rejected a shared install runtime (submodule/package) for v1 in favor of per-repo copy/install.
