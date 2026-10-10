# Third-party notices

The curated protobuf definitions in `src/fncbale/proto` are adapted from
BaleNova 0.3.1 (PyPI wheel SHA-256
`e55272d0abae0a4f01f5c7d1833a3769498837ebcf75bdf05d5225bcd3811b1a`).
Copyright (c) 2026 Bale Async contributors. MIT license: `licenses/BaleNova-MIT.txt`.
Original schema hashes are recorded in `docs/protocol-provenance.json`.
Namespaces and update envelope types are adapted; contracts are verified against
the independent current-web research fixtures. No Bale SDK is a runtime dependency.
Imported search/history/delete, independently described SetRestriction and verified
public-join/invite URL/member-count wire facts and cached asset hashes are recorded in
`docs/web-protocol-patches.json`; the isolated generator applies those corrections.

AioBale and Balethon were studied for behavior and API design; their runtime code
is not included. No proprietary SDK code is incorporated.

The HTML documentation ships local Vazirmatn and Manrope font files, each under
the SIL Open Font License 1.1. Their original license notices and source URLs are
included in `docs/site/assets`. These documentation assets are not SDK runtime
dependencies and are not included in the Python wheel.
