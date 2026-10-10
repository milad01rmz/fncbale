# Contributing

Use Python 3.12+ and an isolated virtual environment. Install `.[dev]`, then run
the offline tests, Ruff checks, and a wheel build as described in the README.
Run `python tools/validate_docs.py` after changing documentation; it needs Node.js
and checks both translations, internal routes, and Python example signatures.

Keep a change focused and explain its observable behavior. Add a regression test
for a reproduced correctness bug. Do not enable ambiguous-write retries without
service-specific evidence for fixed identifiers across the involved routes.

Default tests use local models and fixtures. Do not add automatic live login,
code requests, channel mutations, or secrets to CI. Live examples require your
own account and explicitly authorized destinations.

Never commit session files, tokens, codes, signed URLs, private message exports,
or HAR captures. An issue should include the version, OS, method, error type,
and a small example with private information removed.

The HTML guides are in `docs/site`. Preserve complete Persian and English text,
RTL/LTR behavior, keyboard access, and both themes. Font files include their OFL
licenses. Protocol provenance and the adapted MIT notice must remain intact.

Generated protobuf code is included in the package. Regeneration is a developer
operation using the separately acquired pinned BaleNova schema source and
documented web-contract patches; it is not needed to install or run fncbale.
