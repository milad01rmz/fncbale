# Capability acceptance — 0.1.36 alpha

The bilingual user guide is at [fncbale documentation](https://milad01rmz.github.io/fncbale/#en/support).
This matrix records bounded acceptance, not universal server compatibility.
The public package includes offline tests; private sessions, live traffic exports, and
research receipts are deliberately not distributed. Existing protocol definitions
and provenance remain available.

| RPC | SDK acceptance | Scope / evidence |
|---|---|---|
| SendMessage | Live core | Text, reply, real media, ACK faults; 0.1.15 installed native stalled-send deadline confirms exactly one history match without resend; frozen RID, unresolved ambiguity retained |
| SendMultiMediaMessage | Live core | 2/10 items, mixed photo/video; lost-ACK proof; exact per-item dates for reference/delete |
| UpdateMessage | Live core | Actual text/caption edit; media preserved; recovery events |
| DeleteMessage | Live core | Single/batch, packed dates; offline recovery |
| ForwardMessages | Live core | Nested forwarded content; correct channel OutPeer |
| LoadHistory | Live core | Actual content/hash matches, inclusive date and small-page traversal |
| GetRoutesStates | Live core | 255 routes on existing native session; old checkpoints retained |
| GetDiff | Live core + model pagination | Live disconnect sent/edit/delete; model needMore/all routes/unknown |
| GetNasimFileUploadUrl | Live core + interrupted large transfer | Nasim allocation + bounded full PUT; real 8 MiB partial transfer/SHA; 0.1.13 installed 1 MiB transfer proves both owned spool handles close after interruption/retry without QA wrapper cleanup |
| GetNasimFileUrl | Live core | Stream download, actual hashes; bounded retry/expiry faults |
| GetNasimFileUrls | Live album batch + local partial/fault recovery | SDK downloads 10 owned album items with one allocation; hashes and transfer limits verified; earlier raw WS/HTTP acceptance retained |
| GetFullGroup | Live core | Exact test-channel identity/access hash, member count |
| GetGroupMembersCount | Live two-target WS/HTTP read | Positive compact count equals current full-group count; scalar zero uses presence-aware full fallback, UNIMPLEMENTED12 alone changes methods. Payload2 vs400–401 bytes on small targets; no network-speed/SLA claim |
| GetGroupInviteURL | Live owned current invite read | Private owned group, repeated value and installed WS/HTTP equality; values excluded from reports; revoke/rotation and distinct-member permissions not claimed |
| LoadMembers | Live small resumed pages + local pagination | Both targets continue through a binary cursor to terminal page; bounded/limited iterator, overlap and cycles locally; large changing membership is separate |
| GetMessagesViews | Live ordered batched read | increment=False; owned history references, within-batch duplicate and ordered counts; absent/zero/conflicting/negative wrappers locally; increment=True still durable |
| SearchMessages | Live basic + full hydration | Raw projections are indexed text/captions; typed history hydration and real photo download hashes verified |
| SearchMessageMore | Live nonempty continuation + terminal page | Native same-user-peer search returns 20 initial +20 continued +0 terminal, 40 unique references; opaque state/presence preserved, local cycles/exhausted-state checks retained |
| GetContacts | Live basic read | Typed successful RPC; no contact contents included in reports |
| LoadDialogs | Live basic read | Bounded five-dialog response; no dialog contents included in reports |
| GetFullUser | Live basic self read | Existing authorized account; other-user permissions remain unverified |
| SearchPeer | Live target resolution | Exact username hydration for both canonical test channels |
| SearchContacts | Live exact-target reference / experimental general use | Known test-channel query returns its exact canonical reference on WS/HTTP; full group hydration is separate; broad contact search unverified |
| LoadUsers | Live basic self read / experimental general use | Existing authorized self peer loads once on WS/HTTP; arbitrary users/large batches/permission errors unverified |
| GetMyGroups | Live basic read | Default enumeration includes both known targets on WS and HTTP; broad filters/size remain unverified |
| LoadGroups | Live basic read | Both exact target group IDs/access hashes load on WS and HTTP; batch-scale/error coverage unverified |
| StartPhoneAuth | Fresh native SDK login + local lifecycle | One authorized-account transaction; default request selects Bale-only delivery2. No automatic repeat or SMS/registration claim |
| ValidateCode | Fresh native SDK login + local lifecycle | New verified-provider message code, explicit native validation/session save/restart; wrong-code and disk-only commit recovery locally; no second-factor/second-account claim |
| ValidatePassword | Experimental + corrected local flow | Exact official-web RPC discriminator; permission/empty-body rejection, staged and callback acceptance locally; real second-factor pending |
| CreateGroup | Live basic private group/channel + owned public creation | Public channel0.1.17 and public group0.1.19 requested restriction1/nonempty name acknowledged; exact original typed creation response diagnosed without new mutation. Current membership/read/local replay/cleanup verified; broad roles/invitations/partial results remain separate |
| EditChannelNick | Live owned public channel + local durable policy | Public channel nickname set/search/readback, committed local replay; private channel rejected RPC7. No collision/general role or ambiguous dedupe claim |
| SetRestriction | Live owned channel transitions + primary typed wire | Private/public/private state, wrapped nickname clearing and group FIFO; nonce absent, ambiguous retry disabled. Redundant public-to-public rejected RPC7; ordinary groups/arbitrary roles unverified |
| EditGroupAbout | Live basic mutation | Real test-channel about, full state verification and persistent undo |
| EditGroupTitle | Live basic mutation | Real test-channel title, full state verification and persistent undo |
| InviteUser | Experimental durable action | Same conservative mutation policy |
| JoinGroup | Live already-member owned group / experimental fresh membership | Current private token RPC, valid group response and committed local replay; after last-member orphan leave RPC5/one attempt. No distinct real-account enrollment proof |
| JoinPublicGroup | Live installed already-member owned public group / experimental fresh membership | Separate short-peer RPC with no invented nonce; typed response/current membership/local replay and cleanup. Empty/foreign ACK stays durable uncertain; orphan rejoin RPC5. No second-account/role restoration claim |
| KickUser | Experimental durable action | Same conservative mutation policy |
| LeaveGroup | Live basic owned private group/channel | makeOrphan=True, membership absent from MyGroups after leaving; arbitrary roles and server entity deletion unverified |
| EditAbout | Live owned self profile + local faults | Durable profile builder; set/clear, readback and exact original restoration. No arbitrary-account mutation |
| EditName | Live owned self profile + local faults | Durable name builder, real state and committed local replay; exact original name restored |
| EditNickName | Experimental durable profile builder | Typed presence/validation/cache/idempotency locally; live username mutation unverified |

Core send/receive, media, mixed 2/10-item albums, reply/edit/delete, recovery, and
independent copy/mirror behavior have controlled live acceptance. Unknown fields
and events are retained. Missing history or server retention is reported explicitly.

Grouped forward_album remains experimental; offline tests do not establish live
acceptance. A second independently controlled real account, real second-factor
authentication, and large/changing-member permissions require additional fixtures.
The 100-client load model is not 100 authenticated service accounts.

Full offline 0.1.35 suites: Windows384 passes plus one host symlink skip; Linux385
passes. Installed generic-only wheels were checked on both systems. CI repeats the
offline package validation; live tests are never run automatically.

Bot API, calls, and financial operations are outside this release.
