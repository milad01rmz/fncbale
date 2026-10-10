# Changelog

## 0.1.35 — account-safe media admission and public documentation

- Reject account changes during asynchronous media preparation before admission;
  clean unaccepted spool files and keep already committed operations bound to their
  original account. Do not attach progress callbacks to a different account.
- Report a missing late album sibling explicitly in the channel-chain history
  probe instead of silently skipping it when its first sibling is already mapped.
- Add a chat-ID CLI example and bilingual HTML documentation with local search,
  dark/light modes, responsive navigation, and copyable examples.
- Prepare the public GitHub package, installation instructions, provenance,
  contribution guide, offline CI, and static documentation deployment.
- Full offline suites: Windows384 passes+one host symlink skip; Linux385 passes.
  No broader real-account or experimental-RPC acceptance is inferred.

## 0.1.34 — mixed peer search hydration and read-only upstream chain

- Fix LoadUsers hydration to use the typed request's peers field when exact
  username search includes user references alongside group/channel results.
  Matching and nonmatching reference regression tests pass.
- Add channel_chain example: one Client, read-only news source, two independent
  send mirrors, persistent prior downstream mappings, five recent logical-post
  seed and10-second bounded history reconciliation. Mutation destination fence
  uses each RPC's channel enum and is initialized before outbox recovery starts.
- User's news→test1→test2 worker is active; source writes/forwards are prohibited.
  Original local pre-transport guard failures and same-operation repairs remain
  documented.24 focused checks pass; new wheel matches runtime source. Current
  deployment is source runtime; final multi-OS installed acceptance remains separate.

## 0.1.33 — independent existing-content copy and durable channel mirror alpha

- Add copy_message/copy_album and durable enqueue variants, source identity/group
  validation, frozen typed content/unknown fields and existing file references.
  Independent SendMessage/SendMultiMediaMessage writes retain new stable IDs,
  explicit target reply and normal conservative uncertainty/reconciliation rules.
- Add reusable channel_mirror with persistent source→target mappings, operation
  recovery, historical backfill and live reply/edit/delete handling. No forwarding
  or reupload. Fix complete current album lookup and aggregate grouped ACK binding;
  late album expansion is explicit instead of silently ignoring new source items.
- Native19-step source-only fixture passes with40 historical items, five media
  kinds,3mixed/10-item albums,18 downloaded hashes and offline new/edit/delete
  recovery. Prior7-item clipping failure and limited owned repair remain recorded.
  Current installed wheel worker continues same ledger. Five new tests/24 focused;
  full Windows369+host symlink skip/Linux370 pass. Grouped forwarding stays experimental.

## 0.1.32 — explicit grouped forward API alpha

- Add `enqueue_forward_album` / `forward_album` for explicit source-album snapshots.
  Validate 2..10 distinct photo/video items from one source album before admission;
  persist fresh item RIDs and a grouped ID in the existing durable ForwardMessages
  request. Historical proof must match the grouped ID before returning exact refs.
  Normal forward behavior and its existing idempotency intent remain unchanged.
- Four offline boundary tests and full OS suites pass. This new API is experimental:
  its live mutation was not exercised after the user requested independent sends.
- Retained user showcase uses ordinary send methods on installed0.1.31:26 direct
  target items/14 cases/23 independently downloaded file hashes pass; old forwarded
  samples belonging to that run were removed. Web displays an album-level caption
  only if exactly one item has caption text; per-item captions remain supported.

## 0.1.31 — empty outbox transaction probes alpha

- Empty dispatch selections share their result only inside the current writer
  batch. A separate indexed guard excludes pending timed/rate/peer-blocked work;
  those probes always reevaluate readiness. Every non-probe mutation clears hints,
  positive claims remain unique/atomic and no hint survives COMMIT. Idle workers
  avoid repeated ready-selection/savepoint SQL without a retained account cache.
- Clear outbox wake before the claim so an enqueue racing with an empty result
  cannot have its signal erased before waiting. FIFO, rate gates, attempt budgets,
  accepted payloads/RIDs and conservative uncertain-write handling are unchanged.

## 0.1.30 — committed inbox notifications alpha

- Durable consumers wake on account-scoped inbox commits/quarantine replay instead
  of scanning empty SQLite inboxes every50ms. The writer notifies after COMMIT even
  when the record caller cancels; rolled-back records never notify. ACK/failure
  completion wakes delivery capacity. Clear-before-read preserves commits racing
  with an empty scan; a500ms safety scan covers changes outside supported writers.
  Consumer ownership releases its subscription on cancellation/disconnect/close;
  an old iterator cannot unregister a replacement owner. No delivery/ACK/retry
  semantics change and no new retained account cache.

## 0.1.29 — WebSocket control write deadlines alpha

- The web handshake and application heartbeat send/lock waits obey `rpc_timeout`.
  A failed/stalled heartbeat retires only its own socket, signals reconnect and
  releases pending RPCs with conservative transport uncertainty. A heartbeat
  waiting for send capacity rechecks identity before touching an obsolete socket.
  Caller cancellation during handshake remains cancellation and closes the socket.
  No ambiguous-write retry policy or RID change.

## 0.1.28 — public pagination account lifecycle alpha

- History, grouped albums, members, views and both search iterators retain their
  starting account and end at permanent close or identity change between items/pages.
  Old buffered rows never mix with another account's results. A stale view iterator
  also stops before consuming the next application input batch. An identity change
  during an active RPC still raises the existing explicit account error.

## 0.1.27 — queued RPC lifecycle and identity alpha

- RPCs recheck permanent close and account identity after rate/capacity waits,
  before choosing transport. Typed/raw read retries stay on their original account;
  late typed results cannot populate another identity's cache. Late rate-limit
  replies update the originating account while open; after shutdown their RPC
  error is preserved without writing a closed ledger. Already validated responses are not
  discarded solely because close began, and raw writes still have no blind retry.

## 0.1.26 — durable operation account ownership alpha

- Durable handles retain the account used for admission, including delayed commit
  results. Using one after Client identity changes raises an explicit account error.
  Operation reads/waits/retries and album reference/reconciliation reads stop when
  identity changes; they never continue with the new account ledger. Buffered
  operation and quarantined event inspection also end at that boundary. Accepted
  payloads, RIDs and original terminal/uncertain states remain available on the
  original account. No new resend or fallback policy.

## 0.1.25 — application auth callback lifecycle alpha

- Code/password callbacks no longer hold the Client lifecycle lock. Close can
  finish while input is pending, including close called from the callback itself.
  Actual auth requests and session commits stay serialized. A late answer after
  close or after a newer transaction cannot validate or replace the session.

## 0.1.24 — permanent shutdown coalescing alpha

- Disconnect during or after permanent close joins that same cleanup and preserves
  its original error. It never starts new network cleanup after resources close.
  An earlier queued disconnect also checks permanent closure before proceeding.
  Cancelled joined callers cannot leave cleanup behind after Client/AccountPool close.

## 0.1.23 — cancellation-safe disconnect alpha

- Run disconnect in one shielded cleanup task. Calling it from a handler no longer
  waits cyclically on that handler's dispatcher cancellation. Cancelling an external
  waiter does not abandon worker/socket cleanup; concurrent waiters join that task.
  Reconnect waits for an in-progress disconnect. Unacknowledged events still replay.

## 0.1.22 — direct handler shutdown lifecycle alpha

- Directly awaiting `run_handlers()` uses the tracked dispatcher child. Disconnect
  and close wait for its asynchronous worker cleanup before releasing ownership or
  closing storage. Cancelling the caller cancels and joins the child; internal
  dispatcher exceptions still reach the awaiting caller. Unacknowledged records
  retain their IDs for replay.

## 0.1.21 — durable event consumer ownership alpha

- Reserve handler ownership synchronously; explicit iterators cannot overtake a
  scheduled handler. Ownership remains until worker cancellation cleanup completes.
  Pre-step cancellation/task creation failure releases its own reservation safely.
- Explicit disconnect ends old iterator ownership; late cleanup cannot clear a
  new consumer's leases. Old batches stop when the Client account changes.
- Bind ACK to the original inbox account and avoid using another account's peer
  cache for enrichment. Late local ACK remains scoped to the original record.
  Closed Clients reject new handler tasks; journal/replay semantics stay intact.

## 0.1.20 — compact member counts with conservative fallback alpha

- Curate the independently typed GetGroupMembersCount read contract; default
  `member_count` uses its compact positive count response instead of full metadata.
  Native WS/HTTP/current full-group equivalence is recorded on both test channels.
- Preserve absent-versus-zero semantics: scalar zero requires presence-aware full
  state. Only UNIMPLEMENTED12 changes methods; permission/auth/validation/negative
  counts and exhausted read budgets propagate. `source="full"` retains the old path.
- Validate full-group identity before adopting cache metadata or its fallback count;
  missing/zero/foreign identities invalidate the requested cache entry and raise.

## 0.1.19 — distinct public membership and invite reads alpha

- Add independently curated JoinPublicGroup and GetGroupInviteURL contracts,
  `join_public_group(peer)` and `get_group_invite_url(peer)`. Public joining uses
  a short peer; private `join_group(token)` stays separate. No wire nonce is invented
  for either join. Durable group order/local replay and uncertainty policy apply.
- Reject a foreign group acknowledgement before caching it and reject malformed
  private tokens before admission. Invite values remain caller-private; native
  acceptance and single-account/orphan fixture limits are documented separately.
- Validate creation/join group identity before durable confirmation. Missing or
  foreign acknowledgements leave one tracked uncertain operation with no blind
  resend, including after restart/local idempotency-key reuse.

## 0.1.18 — bounded identity cache and long-lived pool memory alpha

- Bound account-local peer cache to configurable1024 canonical identities by default,
  with one username alias per identity and LRU eviction. Replacement, invalidation,
  expiry and eviction remove aliases together; renamed/reassigned aliases cannot
  retain old hashes. Numeric untyped resolution checks two wire namespaces directly.
- Apply TTL to optional event enrichment; expiration/eviction does not alter raw
  journal/inbox data or immutable outbox peers. Caller-held typed Peer remains usable.
- Clear caches on permanent Client.close; late metadata extraction cannot refill a
  closed cache. Existing metadata capacity512 and network/durable policy remain.

## 0.1.17 — explicit group/channel visibility and public creation alpha

- Add independently typed SetRestriction from captured official wire facts and
  `set_group_visibility(peer, public=..., username=...)` for explicit privacy changes.
  Preserve wrapped empty nickname, unknown fields and absence of a server nonce;
  ambiguous results never trigger blind retries. GroupOutPeer uses the group FIFO.
- Creation with a nonempty username selects public restriction; unnamed/empty-name
  creation retains private mode and explicit empty wrapper presence. Nickname editing
  alone never promotes a private channel. Native private/public/private transitions,
  channel nickname edit/search and verified cleanup pass on an owned fixture.

## 0.1.16 — known-unsent HTTP acquisition failures alpha

- Classify HTTPX ConnectTimeout and PoolTimeout with ConnectError as failures before
  application request headers. Safe operations can use the existing bounded retry
  budget instead of being stranded as uncertain. Read/write/protocol failures and
  the unclassified whole-attempt deadline remain possibly sent.
- Verify a real local single-connection pool admits no second wire request on
  timeout; durable outbox exhaustion remains failed and explicit retry preserves
  the original operation ID, idempotency key, RID and serialized payload.

## 0.1.15 — bounded RPC deadlines and conservative HTTP acknowledgements alpha

- Apply the WS RPC deadline to send-lock wait, send and response together. A
  timeout before transmission stays safely unsent; a failed/cancelled partial send
  closes only its own connection generation. Pending futures are always cleaned.
- Bound the entire HTTP RPC including header wait and streamed body, independently
  of an injected client's per-I/O timeout. Disable redirects per request and accept
  final unary HTTP 200 only; asynchronous/partial/redirect responses stay ambiguous.
- Exercise actual transports with durable outbox faults: one immutable operation
  remains inspectably uncertain without another write when history cannot prove it.
- Accept one installed native transmission with an injected stalled send await:
  history reconciliation confirms the original message without a second send,
  reconnect/edit/delete/event delivery pass and the owned message is removed.

## 0.1.14 — safe admission cancellation, bounded config and native auth acceptance alpha

- Invalidate self identity aliases for both raw typed and convenience profile
  operations after admission, and conservatively when cancellation cannot prove
  nonacceptance. Committed work/IDs remain discoverable; rejected intent preserves cache.
- Require positive integer counts and finite timing values before resources are
  created; fractional/NaN semaphore limits previously bypassed concurrency caps.
  Snapshot caller retry method collections into frozenset to prevent later mutation.
- Accept one real fresh native StartPhoneAuth/ValidateCode transaction and saved SDK
  session restart, plus installed Windows messaging/events and Linux session reads.
  No SDK dependency, old OTP reuse or second-factor/second-account claim.
- Accept a nonempty native search continuation: 20+20 results and an empty terminal
  page, opaque states retained and 40 distinct same-peer references; private text/code
  contents are excluded from reports. Schema and protocol/API signatures unchanged.

## 0.1.13 — interrupted upload cleanup and combined pool QA alpha

- Always close the caller-owned upload byte iterator when HTTP returns or raises,
  before retry, allocation adoption or cancellation releases transfer slots. This
  closes spool read handles even if the transport retains its partially read request.
- Add concurrent pool QA with independent text/album lanes, real bounded streamed
  file transfers/hashes, receive/handler faults and accepted-unsent restart recovery.
  Model traffic is explicitly separate from authenticated real-account performance.
- Add interrupted and cancelled body-ownership regressions and installed-wheel
  acceptance. No protocol, API or schema change; runtime dependencies remain generic.
- Coalesce shared-store hourly maintenance under one lock; concurrent account
  supervisors do not repeat the same full journal/spool scan. Failure/cancellation
  releases the lock without advancing the successful-maintenance timestamp.

## 0.1.12 — completed media transfers and durable profile actions alpha

- Reject incomplete/redirect HTTP responses before adopting an upload allocation
  or replacing a downloaded file. PUT accepts completed 200/201/204 responses;
  whole-file GET requires 200. Redirect following is explicitly disabled even if
  an injected HTTP client enables it. Existing bounded URL refresh remains.
- Add enqueue_edit_profile_name/about/username and corresponding edit_profile_*
  conveniences on the durable account outbox. Preserve absent versus empty wrapper
  intent, committed idempotency replay and conservative uncertain-write handling.
- Invalidate cached self identity on durable profile admission, including when the
  caller cancels waiting or an acknowledgement is uncertain. Other peers stay cached.
- Name/about have single-account live readback and persistent restoration evidence;
  username changes remain experimental. No schema change or new runtime dependency.

## 0.1.11 — resumable member pages and bounded view reads alpha

- Add MemberPage/get_member_page with original binary cursor, next cursor, typed
  members and preserved wire data; extend iter_members with cursor/limit and cycle
  detection from the initial resume cursor.
- Add MessageViews/iter_views: 1..100-reference batches, bounded iterable consumption,
  within-batch dedupe, input-order restoration and exact message identity matching.
- Preserve count presence: absent records/wrappers are unknown, explicit zero is
  available. Reject conflicting/negative counts; keep original wire containers.
- Reject absent/negative member count instead of reporting a fabricated zero.
- Detach the previous account's ledger key, FSM and progress callbacks only after
  a successful session switch; same-account token refresh preserves operation context.
- Prevent an HTTP Set-Cookie from implicitly authenticating later RPCs before the
  validated session has been durably adopted; only the explicit SDK token is sent.
- Keep view increment as the existing explicit durable action; new iterator is
  read-only. No cursor persistence, fixed membership snapshot or count freshness
  guarantee is implied. Schema remains 3.

## 0.1.10 — staged native authentication alpha

- Handle the official web RPC discriminator `password needed for login`; generic
  permission errors and empty auth responses never request a password.
- Add client-bound LoginChallenge, start_login, complete_login and
  complete_password_login. Wrong-code/password errors leave the same transaction
  available for an explicit retry; starting a new login supersedes it.
- Isolate callback protobuf mutation from the transaction submitted to the server.
- Retain validated credentials in memory after session-save failure so another
  completion retries only persistence, without repeating server validation.
- Share account/pool RPC limits during authentication, clear unfinished auth on
  close, validate phone/code/password inputs before the corresponding request.
- Keep schema 3 and all conservative messaging retry policies unchanged. Fresh
  real OTP/password acceptance remains a separate gate from modeled auth flows.

## 0.1.9 — bounded batch downloads and session commit alpha

- Add download_many/download_album, URL allocations in batches of up to 10 unique
  file IDs, bounded workers and shared per-account/pool download limits (4/16).
- Refresh expired/interrupted transfers through the singular allocator. Unsupported
  batch methods and missing/ambiguous URLs use the singular path; auth errors stop.
- Validate all destinations/hashes/identities before allocation, preserve input
  order and existing targets, stream/hash every file and serialize indexed progress.
- Report partial file results with BatchDownloadError/DownloadResult; cancellation
  drains workers and temporary files without claiming whole-batch atomicity.
- Adopt login identity only after durable session save. Shield session commit through
  cancellation while holding lifecycle serialization; drain direct file-save syscalls.
- Restrict the Windows temporary session file before atomic replacement, keeping
  the previous file if permission setup or replacement fails. Schema remains 3.

## 0.1.8 — late album metadata reconciliation alpha

- Persist edits/deletion tombstones that arrive before an album item's metadata,
  keyed by account, peer and RID; later full/compact metadata consumes them atomically
  with inbox, snapshot and route checkpoint. Keep original raw events unchanged.
- Preserve full metadata, unknown fields, item order and permanent snapshot tombstones;
  a later edit or stale new replay does not resurrect a deleted item.
- Retain unresolved early mutations independently of event ACK/retention, compacted
  to one last observed edit and one deletion bit per RID. Remove them only after
  a durable album snapshot incorporates them; do not guess missing group identity.
- Migrate schema 1/2 to 3 with retained missing-item mutations. Existing snapshots
  are not rewritten by older retained edits. Older clients reject schema 3.
- Cover composed envelopes, account/peer isolation, checkpoint rollback, retention,
  migration and real process kills after pending commit/inside materialization.
- Verify native server mutations/history through a restarted observer with delayed
  metadata, stable caption/media/references, stale replay and owned message cleanup.

## 0.1.7 — durable dispatcher recovery alpha

- Retry transient inbox reads, ACK commits and handler-failure commits with the
  current delivery lease. A failed automatic ACK does not reinvoke successful user code.
- Preserve the committed handler failure budget across restarts and use a guarded
  counter update for committed-but-unobserved results. Never revive an acknowledged
  event after an application exception; lowering the limit preserves prior counts.
- Treat an application-awaited cancelled future as a bounded handler failure;
  actual dispatcher cancellation still stops/drains workers normally.
- Drain the fixed worker group on an unexpected worker error and let the recovery
  supervisor restart it with stable durable event IDs and bounded task count.
- Expose account-local `iter_failed_events` with bounded pages and
  `Event.handler_failures`, alongside explicit quarantine replay/discard.
- Index inbox status in rowid delivery order, avoiding a full pending backlog sort.
- Verify native sent/edit/delete delivery with ACK/counter storage faults and
  same-ID quarantine replay, sustained restart/handler QA and 100 model accounts.
- Verify existing self LoadUsers, exact target SearchContacts reference and two-file
  GetNasimFileUrls with independent hashes on WS/HTTP, retaining scoped acceptance.

## 0.1.6 — bounded parallel album uploads alpha

- Upload album items concurrently within per-account/pool limits, retaining input
  order and stable RIDs/groupedId. Bound worker count instead of creating one task
  per item across every album.
- Merge completed upload IDs per item in SQLite, avoiding stale sibling snapshots;
  retry commit failures without uploading successful files again. Reuse committed
  items after cancellation or real process-kill recovery.
- Cancel/drain sibling workers on item failure; emit no partial album payload/send.
  Serialize progress callback invocations within an operation; values remain per file.
- Guard preparation commits by account/status/in-flight state and immutable file hash.
- Verify live fresh mixed 10-item uploads, actual concurrent PUTs, every download
  hash, exact references and deletion. Include bounded pool concurrency benchmark
  and additional item-commit/mid-transaction crash stages.
- Verify default GetMyGroups and exact LoadGroups typed reads on both WS/HTTP,
  without expanding their basic acceptance to broad filters or batch scale.
- Verify owned private group/channel creation, committed local replay, metadata
  edits and leave, with membership absence and no pending cleanup. No server
  duplicate-RID or entity-deletion assertion is inferred.

## 0.1.5 — durable mutation API and exact album references alpha

- Expose committed handles for text/caption editing, forwarding and single/batch
  deletion; preserve existing methods that wait for the same durable operation.
- Inspect account-local operations with status filters, bounded keyset pages,
  proof/attempt summaries and no payload or access hashes in inspection results.
- Fix shared album ACK date being mistaken for every item's creation date. Persist
  exact history RID/date/sequence per item before returning album references;
  multi-message forwards use the same hydration. Lost-ACK reconciliation preserves
  all references atomically. Do not subtract guessed milliseconds.
- A confirmed operation whose exact references are temporarily unavailable raises
  MessageReferencesUnavailable(operation_id); waiting again only reads, never resends.
- Add native login, manual ACK, operation inspection and account-pool examples.
- Live mutation handles/reconnect/reference/delete acceptance and a model that
  rejects incorrect per-item deletion dates cover the fix.

## 0.1.4 — complete message metadata and startup recovery alpha

- Type imported search messageContainer and presence-aware history authorSign;
  preserve full bulk history metadata, quotes, sequence and unknown fields.
- Enrich legacy album snapshots without undoing later edits or deletion; split
  bulk frames with one parent copy rather than copying every item for each item.
- Hydrate indexed caption/text projections through a bounded shared history
  window; report unavailable snapshots instead of losing photo/video references.
- Freeze automatic action nonces on cloned requests; expose durable action handles
  and group/channel helpers, with explicit partial-member creation errors.
- Anchor first-session route state before opening WS so startup overflow recovers
  the messages between that anchor and the later server state.
- Reject unusable new-message ACK dates, reconcile once or retain uncertainty;
  preserve original date/sequence and known metadata through edits.
- Real title/about edit and undo, typed photo search/hash downloads, full received
  album snapshot, fresh startup and invalid-ACK/edit/forward acceptance pass.

## 0.1.3 — history and scoped dispatch alpha

- Page history with inclusive timestamp overlap and bounded retained identities;
  never skip equal-date boundary items silently. Expose HistoryPaginationGap when
  the verified 100-item date-only cursor cannot prove boundary completeness.
- Release blocked conversation producers/receivers on scope exit or disconnect;
  timeout/cancellation cannot leave a getter that steals the next event.
- Reject new durable operations immediately when close begins, including media
  before disk preparation or cached-peer requests before disconnect completes.
- Preserve target-peer FIFO for groupPeer account actions, validate view references
  and full-user targets, and reject cyclic binary member/search cursors.
- Use explicit AND search conditions and stop on an empty result page even when
  the service returns an exhausted cursor. Fresh search indexing is asynchronous.
- Verify history, members, views, contacts, dialogs and self full-user on real
  channels; a separate search run matches all five owned messages after indexing.

## 0.1.2 — pool and account isolation alpha

- Finish every pool/client/store cleanup despite cancelled waiters or a sibling
  cleanup failure; reject new accounts after closing begins.
- Validate portable account directory names and reject escape/symlink/case aliases.
- Apply persisted account cooldown to typed, read and raw RPC dispatch without
  holding shared RPC slots while waiting; update the gate after durable commit
  even when the deadline caller has been cancelled.
- Represent unknown read state as None and expand public media/message annotations.
- Add typed multiaccount model QA: lost text/album ACKs, rate rejection, streaming
  file hashes, paginated all-route recovery, restart and same-RID account isolation.
- Persist distinct RPC/history delivery proof; reconciled lost ACKs no longer
  incorrectly set rpc_confirmed. Legacy records do not invent a proof source.

## 0.1.1 — durability alpha

- Persist retry slots and rate-limit deadlines across restart; observable waiting
  operations, account-scoped throttling and explicit retry cycles with unchanged payloads.
- Retry ACK commits after storage failures without another network write; retain
  uncertainty after unexpected post-dispatch errors and fence confirmed outcomes.
- Migrate schema 1 to 2 atomically; process-kill and SQLite FULL transaction QA.
- Serialize lifecycle operations, finish close despite waiter cancellation and
  release account ownership if lock acquisition is cancelled.
- Journal malformed updates and restart a failed inbox consumer during recovery.
- Wait for pending file I/O before cancellation closes handles; refresh expired
  download URLs, preserve existing destinations and suppress signed URL failures.
- Add real Linux execution, interrupted media tests and live ACK-fault receipts.
- Collect expired orphan SDK spool files while preserving unresolved operations
  and active preparations; use a partial pending-peer index for large outboxes.

## 0.1.0 — initial alpha

- Independent typed wire protocol, WS/HTTP transports, native session import/login.
- Durable inbox/outbox, all-route recovery, bounded dispatch and account pool.
- Text, reply, forward, edits, deletes, media, albums, hash-verified streaming download.
- Router/middleware, conversation/FSM, members/views and curated secondary actions.
- Current-web channel Peer=2 vs OutPeer/ExPeer=3 mapping verified on real channels.
- Bulk channel/album updates normalized into individual received messages.
- No blind retry after possible delivery: server same-RID resend can revert a later edit.
- Product QA receipts, synthetic 100-client benchmark and installable wheel.

Still alpha: Windows and Linux suites run locally; remote CI has not run.
Second real-account QA and long-duration failure/load testing remain separate gates.
