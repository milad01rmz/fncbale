# Public API and operational behavior

- Lifecycle: `connect`, reconnectable `disconnect`, permanent `close`, async context manager.
- Targets: `resolve_peer`, `get_full_group`, `get_full_user`; account-local 15-minute cache.
- Messages: send text/photo/video/audio/voice/document, reply, forward, edit text/caption,
  single/batch delete, paginated history/search and streamed hash-verified download.
- Albums: 2–10 photo/video items, stable item RIDs and groupedId; `iter_albums` groups
  a bounded history window, `get_album` reads the latest durable received snapshot.
  Received snapshots may be partial: the wire does not announce an authoritative item total.

The [channel_chain example](../examples/channel_chain.py) composes two mirrors in
one Client, preserves the existing downstream mapping namespace, seeds five recent
logical upstream posts and adds a10-second read-only history reconciliation probe.
Its destination fence permits only message mutations to two resolved test channels;
the upstream remains read-only. Destination identities are resolved before starting
outbox recovery. Polling reconciles visible new/edited content, never infers deletion
from absence in a bounded window. Native source deletion still uses actual events.

The current Bale web gallery displays an album-level caption only when exactly one
item has a nonempty caption. Multiple item captions remain present in server history;
they are not lost. For a visible shared caption, set it on the first Media item and
leave the other captions empty. Plain text supports Bale's single-asterisk bold and
underscore italic rendering; backtick inline-code rendering is not claimed.

`copy_message(peer, message, reply_to=None, idempotency_key=None)` and
`copy_album(peer, album, ...)` independently send existing source content through
SendMessage/SendMultiMediaMessage; they do not call ForwardMessages. The matching
enqueue_copy_message/enqueue_copy_album methods return durable OperationHandle.
Text formatting, document metadata/captions/unknown fields and existing file
references survive; target RIDs and album groupedId are newly generated once and
persisted before the first write. No download/reupload is needed for reusable files.
Server file permissions still apply; a rejected reference never triggers blind
upload or forwarding fallback. The normal conservative uncertain-write policy applies.

Sources are Message/MessageRef (Album for grouped copy), validated against an
account-bound history window of at most100 rows around the source date. Missing
snapshots, wrong identities/group, unsupported content and albums outside2..10
ordered photo/video items fail explicitly before admission. An old source missing
from this bounded window is not silently replaced. Pass reply_to as the target
message reference; source replies are not automatically remapped by the generic API.
The reusable [channel_mirror example](../examples/channel_mirror.py) supplies durable
source→target reply/edit/delete mappings, historical backfill and live recovery.
Its prepared raw snapshot helper is private, not an additional public raw-copy API.
See [copy and mirror guide](site/#en/copy).

`forward` is explicit forwarding and may flatten an album. Prefer ordinary `send_*`
or `send_album` when a destination must receive independently sent content.
Experimental `enqueue_forward_album(peer, album)` / `forward_album(peer, album)`
use the wire groupedId field, retain item order and require 2..10 distinct photo/video
Message snapshots from one source Album. The result is an Album with exact new refs,
grouped ID and delivery proofs; forwarded content is nested in server quotations
and should be read through history. Its durable payload/IDs survive restart and
grouped history proof is mandatory. Offline tests pass; live grouped-forward
acceptance remains pending. This API is never a fallback for independent sends.

- Events: new/sent/edit/delete/read/read_by_me/received, unknown and gap; router filters,
  middleware, fixed peer dispatch shards, explicit iterator acknowledgement and quarantine replay.
- Durable FSM: `get`, `set`, atomic `update`; `Conversation` has a scoped bounded queue.
- Pool: independent account sessions and cookies, shared SQLite writer, RPC/upload/metadata limits.
- Secondary: members with opaque byte cursors, counts, views (`increment=False` default),
  contacts, dialogs, full user; curated typed group/profile actions via `account_action`.

`get_member_page(peer, cursor=b"", page_size=100)` returns `MemberPage` with typed
members, input cursor, next_cursor, raw response and complete (= no next cursor).
Cursor bytes must remain opaque. Save them with the current account, peer and page
settings only after your application durably processes the page. Retry a failed
read using the last successful page's next_cursor. The SDK does not persist member
cursors automatically or guarantee that a server cursor survives membership changes.
Raw page bytes retain protobuf unknown fields and wrapper presence. An empty page
with a nonempty next_cursor is followed; it is not an automatic terminal condition.

`iter_members(peer, page_size=100, cursor=b"", limit=None)` deduplicates UIDs during
that iterator run, detects repeated cursors (including the resume cursor), and
supports bounded result counts. limit=0 sends no member request. Its dedupe set grows
with yielded UIDs; get_member_page is the bounded-memory option for a long scan.
Resuming a new iterator does not remember UIDs already processed by your application.
`member_count` raises ProtocolError for an absent/negative count; explicit zero is
a valid count. Live counts and paginated members are not a frozen membership snapshot.
Default `member_count(peer, source="auto")` uses the typed dedicated count RPC for
positive values, avoiding full-group metadata. Its scalar proto3 zero lacks presence,
so zero is checked with the previous full-group wrapper contract. Only RPC12
(UNIMPLEMENTED) permits switching to the full-group method; permission/auth/validation,
negative counts and exhausted network budgets propagate. `source="full"` explicitly
uses the prior full-group path. Each RPC retains its bounded read transport budget;
the zero/unimplemented fallback may require a second, separately bounded read RPC.
The compact path does not refresh full-group metadata. Native payload-size/latency
receipts are scoped to the two small test channels; they are not a service speed SLA.
`get_full_group` rejects missing/zero/foreign identities before caching metadata;
this also protects the count fallback from publishing another group's value.

```python
page = await client.get_member_page(peer, page_size=50)
# Process and durably save page.next_cursor in your application before continuing.
if not page.complete:
    following = await client.get_member_page(peer, cursor=page.next_cursor, page_size=50)

async for item in client.iter_views(peer, message_refs, batch_size=100):
    if item.available:
        print(item.ref.rid, item.count)
```

`iter_views` consumes at most 1..100 references per request batch, validates that
batch before sending, deduplicates its identical references and returns MessageViews
in input order, including duplicate inputs. It always uses increment=False. Count
None means no matching container or no views wrapper; count=0 with a present wrapper
is available. Matching requires RID/date and an explicitly nonzero requested sequence;
seq=0 is unspecified. Unexpected identities do not populate another message's count.
Conflicting or negative counts raise ProtocolError; raw matched wire data is retained.
Validation is streaming: earlier batches can have been yielded before a later batch
fails validation/network processing. Closing/cancelling stops later consumption and
requests. Counts are observations, not read receipts or a permanent cache. The existing
get_views returns the unmodified typed response; increment=True remains an explicit
durable operation and is never enabled by this iterator.
- Advanced: `contract(name)` supplies typed request/response classes and evidence status;
  `invoke_raw` requires `retry_policy='none'` or `'readonly'`.

RPC capacity/rate waits and read fallback stay bound to the account that started
the request. Before entering transport, queued work rechecks permanent close and
identity; it raises `ClientClosed` or an account `BaleError` rather than transmitting
under a different account. Typed late results cannot fill a new identity's caches;
late rate-limit replies refer to the original account. Already validated results
are preserved when close alone begins. Raw writes still require explicit `none`
policy and own their result; no blind retransmission or new RID is introduced.

Early edit/delete events whose original album metadata has not arrived are stored
by account/peer/RID. Later metadata atomically incorporates the last observed edit
and deletion tombstone; the raw new event still describes the received original
bytes. Snapshot repair does not emit invented edit/delete events. A tombstone stays
set even if an edit or stale new replay arrives afterward. Full history metadata,
unknown fields and exact references remain attached to the item.

These are snapshots of observed data, not a claim of authoritative server state.
Without a revision identifier, edits from interleaved live/diff streams cannot be
assigned a proven historical order; the last registered edit wins. Missing grouping
cannot be guessed, so unresolved mutations are not purged by normal event retention.
They are compacted to one edit/tombstone row per account/peer/RID and removed after
an album snapshot incorporates them. Unknown/non-album RIDs may remain unresolved;
this trades disk usage for protection against later album metadata. Storage-full
errors remain explicit. History queries still read actual server state separately.

Database schema 3 backfills missing-item mutations from retained schema 1/2 inbox
events in stored order, without replaying old edits over existing snapshots. Events
already purged before this upgrade cannot be reconstructed. Migration commits
atomically outside the event loop; older SDKs reject the newer schema.

`download_many(jobs, expected_sha256=None, progress=None)` accepts 1–100 explicit
`(Message or MediaInfo, destination)` pairs and returns paths in input order. Hashes
are a same-length iterable of SHA256 strings or None. All paths, hashes and file
identities are validated before allocation; aliased destinations and conflicting
access hashes for one ID are rejected. Unique identities allocate in chunks of 10.
Missing/ambiguous batch entries use GetNasimFileUrl. Batch transport failure or
unsupported codes 12/404/501 fall back to singular allocation; auth/permission and
other RPC errors propagate. Each failed/expired transfer has the existing bounded
singular refresh budget. No signed URL is persisted or included in results/errors.

Single and grouped downloads share Config.download_limit=4 per account and
global_download_limit=16 per Pool. A fixed worker group bounds batch tasks.
`progress(index, done, total)` reports per-file bytes with a zero-based input index;
calls are serialized within the batch. Input order is independent of completion order.
`download_album(album, directory, **kwargs)` uses the same path with index/RID
filenames and a validated extension, never a server-controlled destination path.

Every file commits with atomic replacement after size/hash/fsync. A batch can be
partially successful; all independent jobs run unless the caller cancels. A failed
batch raises BatchDownloadError whose ordered DownloadResult entries expose index,
destination, completed and error_type, preserving successful files. Cancelling
drains workers and file I/O, removes temporary parts and leaves already replaced
files available; it does not roll back a completed file. URL allocation failure
before workers start reports the original RPC/transport error. No durable download
outbox or transfer resume is promised.

Login keeps the previous in-memory identity until session persistence succeeds.
`login(phone, code_callback, password_callback=...)` requests one code and calls the
async code callback with a fresh typed response copy. A password callback runs only
after the server's exact `password needed for login` RPC discriminator. Code 7 by
itself and empty successful auth bodies are not password challenges.
Application callbacks run outside the Client lifecycle lock: close can finish while
input waits, and a callback may close its Client. Close does not cancel application
input; the application owns that task. A late answer raises `ClientClosed` after
close or `AuthenticationError` after a newer login supersedes the challenge, before
any stale validation request or session write. Wire stages and durable session
adoption remain serialized, including cancellation during a commit.

For application-managed input:

```python
from fncbale import PasswordRequired

challenge = await client.start_login(phone)
# Obtain input asynchronously in your UI, without holding the Client lifecycle lock.
try:
    session = await client.complete_login(challenge, code)
except PasswordRequired as required:
    session = await client.complete_password_login(required.challenge, password)
```

Challenges are in-memory handles bound to one Client. Their repr hides transaction
data; do not log `transaction_hash`, response protobufs, codes or passwords. A new
start supersedes the previous challenge; successful persistence consumes it; close
discards it. `client.login_challenge` exposes the current handle after a cancelled
callback or recoverable validation error. Wrong code/password errors propagate with
the same handle available; the caller explicitly retries completion, respecting
server expiration/rate hints. No validation or code-delivery request is automatically retried.
After validated credentials encounter a disk error, another completion on that
handle retries only session persistence. The SDK does not persist challenges,
passwords or OTPs across process restarts. Fresh native OTP/code/session now has
single-account live acceptance; actual second-factor remains a separate scope.

Once a validated session commit starts, caller cancellation waits for file save
and adoption before releasing the lifecycle lock, then raises CancelledError.
The committed new session remains usable. Cancellation before validation does not
commit a session. Direct SessionFile.save also drains an outstanding atomic save;
its completed file may remain after cancellation. Failed pre-replacement writes/
permissions keep the previous file and identity; secrets do not enter logs.
After switching to a different user, a previously bound account ledger key is
rebound to the new identity, and old FSM/progress/cache references are detached.
Stored old-account operations remain intact under their original account key.
Same-account token refresh keeps the existing operation context. Disconnect before
changing authentication; connect again before admitting writes or using the new FSM.
RPC cookies always come from the explicit SDK session token. An incoming Set-Cookie
cannot silently authenticate an otherwise anonymous client before durable adoption.
Delivery flags deliberately distinguish RPC confirmation, historical verification,
and read receipts. `MessageRef` carries peer, RID, date and optional sequence.
`Message.read` defaults to `None` when no read state has been established; unknown
must not be interpreted as unread. Read receipt events remain separately available.
Delivery proof is persisted on operations and returned messages. An actual ACK sets
`rpc_confirmed`; history reconciliation sets `history_verified` independently and
does not fabricate an ACK. History proof for a send recognizes its RID/group identity;
a later edit does not mean that the original send failed. Edit reconciliation also
checks the intended content. Legacy records without proof metadata keep their
confirmed status but expose neither proof flag.
Forwarded content lives in a nested quote; an empty flat text is not failed delivery.

All message mutations have durable admission variants: `enqueue_edit_message`,
`enqueue_edit_caption`, `enqueue_forward`, `enqueue_delete_message` and
`enqueue_delete_messages`. They return only after the request is committed; their
existing waiting variants use the same handle. Caption preparation reads the
original file snapshot before admission. A cancelled wait never cancels admission.
Handles retain the account used for the durable commit. Their `status()`, `wait()`
and `cancel()` raise `BaleError` if their Client has since changed accounts. Keep
the `operation_id` and use a Client authenticated as the original account to inspect
or resume that operation. In-flight waits, retries, reconciliation and album reference
hydration also reject an account change before continuing with another account's
ledger. Accepted commits keep their original account/payload; no fresh RID is issued.
Operation and failed-event inspection iterators stop at an account change, including
buffered rows, and never merge pages from different identities.
History, albums, members, views and both search iterators also retain their starting
account. Between items/pages they end at an account change or permanent close; cached
results are not yielded afterward and a stale view stream does not consume its next
input batch. Identity changes inside an active RPC may instead propagate its explicit
account `BaleError`. These lifecycle endings do not invent server history/gap events.
`iter_operations(statuses=None, limit=None, page_size=100)` discovers account-local
summaries, ordered by creation time and ID with pages capped at 1000. Filters accept
OperationStatus values or strings. Each page reads current status, not a transaction
snapshot across the entire scan; concurrent transitions/inserts can change later
pages. A finite limit bounds the overall scan. No message payload, peer access hash
or idempotency key is exposed. Retention can remove old final rows as documented.

Album ACK dates can be the last item's date; they are not an exact reference for
every item. Before returning an album or multiple forwarded messages, wait reads
a bounded 100-message inclusive history window, at most two reads, and persists
each matching RID's exact date/sequence. Grouped ID must match for albums. A valid
ACK remains confirmed even when hydration fails: MessageReferencesUnavailable
carries operation_id. Repeating wait only attempts reads; no send or new RID occurs.
Known references survive restart and resolve without another read. Lost-ACK history
reconciliation stores these references in its confirmation transaction. RPC proof
and history proof remain independent; valid ACK plus successful hydration has both.

Album upload workers are bounded by Config.upload_limit and share the existing
global upload semaphore. Each completed item's file ID/access hash is merged into
the latest durable context by its immutable index/hash; sibling commits cannot
overwrite one another. Storage commit failures retry storage, not the completed
PUT. A reconnect/crash reuses committed file IDs and reuploads only uncommitted
items. The final RPC payload is committed only after all workers finish, in input
order with the original RIDs/groupedId. One item failure cancels/drains siblings
without a partial album send; successfully committed items remain available for
an explicit eligible retry. Metadata/spool preparation still runs before admission.
Progress(done,total) counts bytes of an individual file; interleaving is possible
across files, but callback invocations are serialized per operation. A progress
callback is local to the current process and is not restored from SQLite.

History is returned newest first. `before` is an inclusive server date anchor;
`limit=0` returns no items. Pagination overlaps timestamp boundaries and retains
only the current page/bucket identities, so a long iterator does not accumulate
every RID. Requests may grow up to 100 to resolve a boundary despite a smaller
`page_size`. The verified contract has no RID/offset cursor: if a full 100-item
page remains on the same timestamp, further completeness cannot be proven.
`HistoryPaginationGap` carries `peer` and `date` after yielding the verified prefix;
callers must handle it explicitly. A requested finite prefix can finish normally
without claiming complete history. No timestamp is silently skipped.

Conversation receive yields new-message Events. Handler dispatch acknowledges
them; the conversation queue is a temporary subscription, not a separate durable
consumer. Scope exit/disconnect closes the subscription and wakes blocked receive
with `ConversationClosed`; an ended scope cannot send. Closing a full scope releases
peer dispatch. Timeout/cancellation cleans up queue waits. Durable replay remains
available through the inbox iterator/router rather than an ended conversation.

Search combines peer/text through explicit AND conditions and preserves the query
with each opaque binary cursor. An empty result page ends iteration, including
the server's nonempty exhausted-state case. Repeated cursors raise an explicit
error. Member UID duplicates are suppressed across pages; member/search cursor
tracking grows with page count to detect longer cycles. Fresh sends may appear in
history before search indexing completes; an empty search is not non-delivery.
`get_views` requires references from the target peer and returns an empty typed
response for an empty input without sending an increment RPC. Group actions with
`groupPeer` use that group's durable ordering key.

`iter_search` exposes raw indexed projections. `iter_search_messages` returns full
Message snapshots: an embedded container is preserved when available; otherwise
it hydrates the indexed RID/date from an inclusive history window capped at 100.
The window is shared between nearby matches, while output keeps search order.
An indexed photo caption represented as plain text is never passed off as a full
photo. Missing/deleted/overflowed matches raise `SearchSnapshotUnavailable(ref)`;
absence from this bounded window does not prove server deletion. Indexing may lag
current edits, so a hydrated message may have newer content than its indexed match.
Metadata includes media, quotes, groupedId, seq, unknown fields and optional
`author_signature` (None for absent; empty string for present-empty).

Bulk updates retain one complete history container per Event.raw; the journal also
keeps the original envelope. A received album snapshot preserves sequence/quotes/
signature and unknown metadata. A duplicate full update can enrich a legacy compact
album snapshot while keeping its later content edits and deletion tombstone. No
second new event is fabricated for that enrichment. Direct new events preserve
absent quote as None. Split/copy work is linear in the number of bulk items.

Group/channel helpers: `create_group`, `create_channel`, `edit_group_title`,
`edit_group_about`, `edit_channel_username`, `set_group_visibility`, `join_group`,
`join_public_group`, `get_group_invite_url`, `leave_group`,
`invite_user`, `kick_user`. Title/about editing, empty private group/channel
creation and the owner's makeOrphan=True leave have current basic live acceptance.
Owned channel private/public/private transitions, public creation and public-channel
username edit/search now have native acceptance. Invitations and broader roles,
collisions, ordinary public groups and account-profile usernames remain experimental.
`account_action` takes a
curated typed request; `enqueue_account_action` returns its durable handle.
Requests are cloned without modifying caller data. Missing rid/randomId is generated
and frozen before dispatch; automatic nonces are excluded from caller intent so
idempotency-key reuse retrieves the committed operation. Ambiguous actions remain
uncertain without blind retry. `GroupCreationIncomplete` exposes the created peer
and rejected member IDs; partial member addition never triggers a second creation.
Helpers return accepted results, not an assertion that independently edited server
metadata is still current; read full group state when that distinction matters.

`join_group(token)` uses the private invitation token, while `join_public_group(peer)`
uses the separate public membership RPC with short wire peer type/id. The latter
validates that the acknowledged group ID matches the requested destination, orders
durable work under that group, and preserves no-nonce uncertainty without blind
resend. Neither method makes private/public visibility changes implicitly. Private
tokens must be strings without whitespace. `get_group_invite_url(peer)` reads the
current invite value with group ID/access hash; treat the returned value as private
and parse the link format required by the caller. It does not invoke a revoke/rotate RPC.
Native join acceptance on an already-member owned group is separate from enrolling
a distinct account. In the tested orphan fixture, leaving the last member with
makeOrphan=True then attempting either rejoin returns RPC5; neither route bypasses
that failure. Committed local replay does not prove server duplicate suppression.
Creation/join acknowledgement identity is validated before durable confirmation;
an empty or foreign public-join identity leaves DeliveryUncertain with its operation
ID, rather than a falsely confirmed ledger row. Explicit generic action requests
use the same check and do not bypass it.

`create_channel(..., username="name")` and creation with a nonempty username request
public restriction explicitly; None or an empty name keeps private creation.
`set_group_visibility(peer, public=True, username="name")` promotes explicitly;
`public=False` removes public visibility/name. It validates the bool and requires a
nonempty public username before any RPC. Editing a username does not promote a
private channel. The captured web contract also restricts username editing to
public channels; server business/permission errors are exposed without changing
transport. A redundant public-to-public SetRestriction was rejected by this server;
the accepted transition is private-to-public, not a guarantee for no-op setters.
Use a committed idempotency key for local replay of the same operation.

SetRestriction uses its own typed groupOutPeer and an optional nickname wrapper.
It has no wire RID/randomId; the library does not invent one. Acceptance is durable,
ordered under the group peer, invalidates aliases and retains ambiguous outcomes
without blind retry. Private mode sends a present empty nickname wrapper. Inspect
full group state for actual restriction/name; returned Peer reflects accepted intent.
Pre0.1.17 creation builders did not set public restriction for nonempty usernames.
Upgrading does not rewrite existing durable payloads: reusing an old idempotency key
with the corrected intent can raise IdempotencyConflict; inspect that original
operation rather than treating it as the corrected public creation.

`Config(peer_cache_size=1024, peer_cache_ttl=900)` bounds each account's identity
cache. Size counts canonical peers; at most one username alias is retained for each.
LRU hits keep an identity resident but do not extend its TTL. Replacement, expiry,
alias reassignment and eviction remove old names and identities together. TTL0
disables retention. Numeric targets without kind need a currently unambiguous cache
entry; eviction/expiry can require an explicit kind or fresh username resolution.
Retain returned typed Peer/MessageRef for destinations across large cache churn.

Cached peer enrichment in events now obeys TTL. Cache misses leave the protocol's
available peer fields; raw inbox/journal data, IDs and frozen outbox peer snapshots
are independent of this optional cache. Permanent close releases peer and media
metadata caches; an already-running metadata extractor cannot refill a closed
cache. Media metadata still has its existing512-entry bound. Process RAM includes
Python/import/allocator/application data beyond these entry-count limits.

SQLite uses WAL and FULL synchronization, one worker thread, bounded group commit.
Inbox/checkpoints commit together before callback delivery. Every returned operation
handle refers to a committed record. An in-flight operation interrupted by a crash
becomes uncertain; a durably recorded rejection/unsent attempt remains safe to retry.
Pre-send preparations return to queued. Uncertain predecessors
block later writes to the same peer until reconciliation or safe explicit retry.

Two primary attempts and one HTTP fallback is a budget. Known validation/auth/
permission failures stop immediately. Ambiguous writes first reconcile recent
history; absence in history is not proof of non-delivery. An unverified ambiguous
operation is retained, never resent with a new RID. Default raw RPC policy does
not grant automatic retries for writes. User handlers are at least once, never
advertised as exactly once.

`rpc_timeout` bounds one transport attempt: WS send-lock wait, send and response,
or the complete HTTP header/body exchange. Queueing for account/pool capacity and
server rate waits are outside that attempt deadline. If WS transmission starts but
does not complete, its connection closes (with the bounded WS close handshake)
before reuse; timing out before send remains safely unsent. A response timeout after
a completed send permits late updates on the healthy connection. HTTP RPCs never
follow redirects and require final HTTP 200 as well as valid gRPC framing/status;
other non-error status codes are ambiguous, not confirmed or blindly resent.

The initial web handshake send and application heartbeat send/lock wait also obey
`rpc_timeout`; heartbeat interval controls spacing, not the send deadline. A failed
control write retires only its socket generation, releases pending ACK waiters with
conservative uncertainty and signals the supervisor to reconnect. A heartbeat
rechecks socket identity after waiting for send capacity. Socket cleanup may take
the separate bounded WebSocket close handshake; no new RID or automatic ambiguous
write retry is introduced by reconnection.

The writer coalesces empty dispatch probes only inside one SQLite transaction and
only when an indexed guard finds no queued/waiting operations. Pending timed,
rate-limited and peer-blocked work always gets a fresh eligibility check. Non-probe
writes invalidate all hints and COMMIT discards them; positive claims remain atomic
and are never reused. This adds no retained account cache. Outbox wake clears before
claim so an enqueue racing with an empty result does not lose its signal. The
existing500ms idle scan, peer FIFO, attempt budgets and uncertain-write rules remain.

HTTPX `ConnectError`, `ConnectTimeout` and `PoolTimeout` prove that the application
request has not started and are classified as unsent. Read/write/remote-protocol
failures remain ambiguous. An SDK whole-attempt deadline has no reliable HTTP phase
proof and stays possibly sent, including when it wins a race with HTTPX's timeout.
Safe attempt exhaustion is retained as failed; `retry_operation(operation_id)` is
an explicit new bounded cycle using the original payload/RIDs, not a new message.

Automatic handlers keep their delivery lease while retrying a failed ACK or
failure-counter commit. Storage failure does not consume a handler attempt or
rerun successful user code within that process. A crash before ACK commit can
still redeliver the same `event_id`; applications should make side effects
idempotent. Committed application failure counts survive restart. The default
three-failure budget ends in durable quarantine; `replay_event(event_id)` resets
that budget and retains the ID. Lowering `handler_attempts` quarantines already
exhausted events without erasing their recorded counts.

Consumers subscribe to account-local inbox commit notifications. Notifications run
after SQLite COMMIT, even when a record caller cancels; rollback never announces
data. ACK and completed failures wake full delivery capacity. The iterator clears
its hint before scanning so a concurrent commit cannot disappear between an empty
read and sleep. A500ms safety scan covers changes outside supported SDK writers.
Subscriptions end with consumer ownership; stale generators cannot unsubscribe a
replacement consumer. These notifications affect scheduling, not durable ACK,
deduplication, checkpoint or at-least-once semantics.

Handler ownership is reserved synchronously by `start_handlers`; an explicit
iterator cannot overtake its task before the first step. Cancellation retains that
reservation until all handler workers finish their asynchronous cleanup. Await the
cancelled task before handing the Client to an iterator. Cancellation before the
first step or failed task creation also releases ownership without losing inbox data.
Directly awaiting `run_handlers()` uses a tracked dispatcher child as well;
`disconnect()` and `close()` wait for its workers before releasing the consumer or
closing storage. Cancelling the awaiting caller also cancels and joins the child.
Do not start another durable consumer while either entry point owns the Client.
`disconnect()` owns a shielded cleanup task. Cancelling its waiter does not retract
shutdown; another call joins the same in-progress task. `connect()` waits for that
task before reconnecting. A handler may call disconnect or close; stopping its
dispatcher cancels that handler, so its `finally` cleanup runs and an unacknowledged
event remains pending. Await shutdown from outside the handler when the caller needs
to observe completion. Cleanup should not await the same shutdown it is blocking.
Disconnect during or after permanent close joins its existing close task and preserves
that task's original result/error. A previously queued disconnect checks closure
before touching network resources; cancelling a joined caller cannot create delayed
cleanup after a Client or AccountPool has closed its store and shared resources.

Explicit `disconnect` ends prior iterator ownership; resume with a new iterator
after reconnect. Late close of the old iterator cannot clear new delivery leases.
A buffered old stream stops if the Client account changes. Each Event ACK is bound
to its original inbox account: a held event may still acknowledge that original local
record after identity changes, while its record/store remain available. It cannot
acknowledge a different account's record or borrow that account's peer metadata.
This is local ledger scoping, not permission to send RPCs as the previous identity.

`iter_failed_events(limit=None, page_size=100)` reads account-local quarantined
Events in stored order with pages capped at 1000. It does not reserve the durable
consumer or lease events. `Event.handler_failures` reports failures committed
before that delivery/snapshot. Use `replay_event(event.event_id)` to retry or
`event.ack()` to explicitly discard a failed event. Pages reflect current status;
concurrent replay/ack can change later pages. Use a finite limit for a bounded scan.
No exception text is stored, since application exceptions may contain credentials.

Fixed handler workers are supervised as a group. An unexpected worker error drains
siblings and releases iterator leases; the Client recovery supervisor restarts a
tracked dispatcher on its next recovery cycle. Directly awaiting `run_handlers()`
also reports the group exception to its caller. A connected Client with registered
handlers retains automatic supervision; disconnect it if recovery should stop.
Awaiting a cancelled future inside user code counts as a failure; cancellation
of the actual dispatcher still propagates and leaves unacknowledged events pending.

`Operation.status == 'waiting'` exposes `retry_at` (Unix seconds) and `cycle_attempts`.
Both the next route slot and deadline survive restart. A rate limit pauses new
durable outbox claims and typed/read/raw RPC dispatch for that account; other
accounts continue. Waiting does not reserve shared RPC slots. Calls already sent
can finish; any later attempt checks the committed account deadline again.
A waiting predecessor preserves its peer FIFO.
After three attempts, a safe operation becomes failed and an unresolved ambiguous
one remains uncertain. `retry_operation()` explicitly starts another three-slot cycle;
`attempts` remains cumulative. Confirmed results cannot be overwritten by a late worker.
`cancel_operation()` can cancel queued/waiting operations with no unresolved delivery
or in-flight write, including a previously rejected attempt. Cancelling only `wait()`
does not retract durable work. An ACK commit failure retries SQLite, not the RPC.
An empty protobuf is valid wire data but is not a usable new-message/album/forward
ACK without a positive date. Invalid ACKs first reconcile, then remain uncertain
if unresolved. No MessageRef(date=0) is fabricated as confirmed delivery. Edit ACK
mutation time does not replace the known original reference date/sequence; caption
edits also retain known grouping, quote and author metadata.

Lifecycle changes are serialized. `close()` is permanent immediately and cleanup
continues if its caller cancels waiting; another `close()` waits for the same cleanup.
The same rule applies to `AccountPool` and its writer. A sibling cleanup failure
does not skip other clients or shared resources; cleanup errors are grouped after
all closers have run. Pool names are portable directory components, unique without
case distinctions; path/device/symlink aliases are rejected before creating clients.
New durable admissions are rejected from the start of closing, even while cached
peer resolution could otherwise succeed; media is rejected before disk preparation.
Download retries are bounded to two full transfers with fresh allocation, without
assuming range resume. Partial data is removed and an existing destination survives.

Recovery retains every route cursor, discovers new routes without replacing old
ones, processes all diff batches, paginates needMore and reports tooLong with a
GapEvent. Live frames enter a durable journal; diff cursors are advanced atomically
with the corresponding inbox. Backpressure disconnects and recovers instead of
discarding queued messages. The server can lose old events beyond its retention;
that loss is reported, not fabricated from current history.
The first session anchors route states over HTTP before opening WS, then diffs
from those anchors. Startup overflow/reconnect cannot replace the pre-connection
checkpoint with a later fresh state and skip the intervening messages.

All timing/limits/endpoints are configurable through `Config` and `ProtocolProfile`.
The research profile defaults to web app version 173855, not a promise of permanent
server compatibility. `research-live` contract evidence predates SDK acceptance;
product live receipts are recorded separately. Experimental APIs can be invoked
but must not be described as live-validated until a receipt exists.

Auth start uses the observed send_code_type=1 default. The captured official web
enum distinguishes default (1), Bale-only (2) and SMS (3); default is not a promise
of SMS delivery. Inspect challenge.sent_code_type or challenge.response() for the
server-selected delivery and expiry information. Other delivery-selection flows
are not separately accepted by this SDK yet.

`enqueue_edit_profile_name(name)`, `enqueue_edit_profile_about(about)` and
`enqueue_edit_profile_username(username)` return durable OperationHandles ordered
on the authenticated self peer. The corresponding `edit_profile_*` methods wait
for the committed typed RPC response (seq/state); read `get_full_user(self_peer)`
to independently verify current state. Name must be a nonempty string. About and
username accept None (absent wrapper) or an explicit empty string (present wrapper).
Username removes one leading @ and rejects whitespace; availability and remaining
server restrictions are validated by the server. About/name live tests restore the
original self values; username mutation remains experimental. The live server
returned no about wrapper for both clear forms; preserving request presence does
not promise that readback distinguishes them.

All six profile APIs accept `idempotency_key`. Reusing the key with the same intent
returns the existing operation; changed intent raises IdempotencyConflict. An
ambiguous write remains uncertain without retransmission. Admission invalidates
only cached self identity, so cancelling a waiting caller cannot preserve an old
name/username cache after accepted work. This does not retract the operation.
Use `enqueue_account_action` for other curated typed account operations.

Media HTTP success requires a completed upload response (200/201/204) and a
whole-file download response (200). Asynchronous acceptance (202), partial GET
(206), redirects and other statuses cannot confirm the file even if body length
matches. This SDK does not issue download ranges or resume transfers. Redirects
are explicitly disabled on both paths; retryable expiry/transport/server failures
retain the existing two-attempt fresh-allocation budget. A failed allocation is
not committed into an album or used for a message RPC. Atomic download size/hash
verification and destination preservation still apply. Only numeric HTTP status
is included in errors; signed URLs and response bodies are not logged.

The SDK owns each PUT body iterator and closes it after HTTP completion/failure,
before starting the next attempt or releasing transfer slots on cancellation.
Transports may retain a request after they stop reading; this must not keep the
SDK's spool file handle open. Shared-pool hourly maintenance is coalesced into one
successful journal/spool scan; failure/cancellation does not advance its schedule.


Configuration counts (RPC/transfer/queue/worker limits, byte sizes and retention days)
require positive Python integers; bool/fractional/nonfinite values are rejected before
resource creation. Timing values accept finite int/float, not bool. RPC/upload/
heartbeat/recovery must be positive; commit_window and peer_cache_ttl may be zero.
`verified_idempotent_methods` accepts a set/frozenset/list/tuple of nonempty method
names and snapshots it to frozenset. Changing the caller's original collection does
not enable new retries. This does not prove server idempotency: the default remains
empty and repeating a send can revert later edits. Explicit arbitrary raw RPC retry
policy remains the caller's responsibility.

Raw typed `enqueue_account_action` profile operations share self-cache invalidation
with convenience builders. Cancellation during admission can happen after commit;
it conservatively evicts self aliases while keeping accepted work. Other peers stay
cached; rejected conflicting intent does not evict cache or retract the existing
operation. Discover the committed ID with iter_operations or the original idempotency
key. Cancelling an admission waiter does not prove that nothing was accepted.

Fresh native login now has real single-account acceptance: one new request, a fresh
verified-provider message/code, native validation, private SDK session save and
independent reload. Installed wheel reads work on Windows/Linux; owned Windows
messages/events also pass. This uses the SDK's default delivery request; it does not
promise SMS, registration, second-factor availability, or automated code reading as
a library API. Applications supply code/password through their own callbacks/UI.
