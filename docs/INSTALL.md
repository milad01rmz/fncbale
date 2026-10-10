# Install and use fncbale

Python 3.12 or newer is required on Windows and Linux. From this checkout:

The bilingual HTML guides are published at
https://milad01rmz.github.io/fncbale/. Release wheels are available at
https://github.com/milad01rmz/fncbale/releases. This release is an alpha.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install .
```

On Linux, use `.venv/bin/python` after `python3 -m venv .venv`.
To use the reviewed standalone artifact, install
`dist/fncbale-0.1.36-py3-none-any.whl` with pip. No Bale SDK is required. Generic
dependencies provide HTTP/2, WebSocket, protobuf, Pillow and PyAV. No separately
installed FFmpeg CLI is needed for the current metadata path. The repository dev
extra (`pip install '.[dev]'`) adds testing/build tools; it is not a runtime requirement.
No source regeneration is needed to install or use the wheel. The development
generator's pinned schema source and licenses are documented in the provenance files.

Version 0.1.8 upgrades the local database to schema 3 on first use, atomically outside
the event loop. It recovers missing album-item mutations from retained old inbox
records; already purged records cannot be recovered. Older SDK versions reject
the upgraded database. Keep the new SDK with that data directory.

Create a native session interactively:

```powershell
python examples/login.py account.session
```

The callback receives the typed auth challenge; the example reads code/password
off the event loop and does not print them. Fresh native OTP validation, session
save/restart and installed Windows/Linux reads have single-account acceptance.
Real second-factor password login remains a separate untested scope because this
account did not require it; see CAPABILITY_MATRIX.md. Existing research `.bale` authentication
responses can be imported explicitly with `Session.import_aiobale(path)` and saved
using `await SessionFile("account.session").save(session)` without the original SDK.
Session and data paths should be kept private and excluded from source control.
For delayed UI code entry or correcting a rejected code, use `start_login` followed
by `complete_login` on the same Client; see API.md. PasswordRequired carries the
same challenge for `complete_password_login`. This sends no extra code delivery automatically.

`examples/basic.py` sends/edits and sends a mixed album: replace its destination and
media files with yours. `examples/receive.py` demonstrates router callbacks for new,
edit and delete events. `examples/manual_events.py account.session` uses explicit ACK after
application processing. Process idempotency belongs to your application; persist
event_id with your application side effects before ACK to tolerate redelivery.

Inspect quarantined handler events with
`python examples/failed_events.py account.session --data-dir .fncbale --limit 100`.
It prints only event ID, kind and committed failure count. Use `--replay EVENT_ID`
to reset its retry budget; the application consumer processes it on its next run.
Use `--discard EVENT_ID` for explicit ACK of a found quarantined event. Discard
searches only the requested limit; increase it if needed. All these examples connect
the account, which also resumes previously admitted durable outbox operations.

```python
handle = await client.enqueue_message(peer, "سلام", idempotency_key="order-123")
# Save operation_id with the application order before waiting for its delivery.
operation_id = handle.operation_id
message = await handle.wait()
edit = await client.enqueue_edit_message(message, "ویرایش", idempotency_key="order-123-edit")
await edit.wait()
```

After restart, reconnect with the same session, data directory and protocol profile.
`get_operation(operation_id)` reads status; `wait_operation(operation_id)` returns
the committed result. `iter_operations` discovers unrecorded IDs with bounded pages.
`DeliveryUncertain` means delivery could have happened; reconcile the same operation
before deciding what to do. `MessageReferencesUnavailable` means delivery is confirmed
but exact batch item references could not yet be read; wait again without resending.
`retry_operation` does not bypass the conservative uncertain-write policy.
Cancellation of wait is separate from `handle.cancel()` for eligible unsent work.

```powershell
python examples/operations.py account.session --data-dir .fncbale --status uncertain --status failed
python examples/pool.py account1.session account2.session --peer @codextest1
```

The inspection example connects and therefore resumes already accepted outbox work;
it does not create or explicitly retry new mutations. Pool sessions must be distinct
accounts. Each pool client uses its own spool/cache while sharing a bounded store
writer and global RPC/upload/metadata resources. A single account cannot run twice
concurrently, even in separate processes. Preserve the same pool name/data layout
on restart. A pool store is separate from a standalone client's state.sqlite3.

No compatibility with AioBale/Balethon/Nova APIs is promised. Convert destinations to
`Peer` or resolve exact usernames; browser UIDs and raw untyped integers are not
interchangeable with canonical channel peers. Durations in MediaInfo are seconds;
the adapter performs the wire's per-kind unit conversion. Files are spooled before
durable media admission; budget disk space for unresolved operations. Album inputs
are 2–10 photos/videos and are validated before uploading. No automatic split or
transcoding occurs. Use the capability matrix for individual endpoint acceptance.

This is a usable alpha. Local real WSL/Linux tests are distinct from unexecuted
remote CI; one live account is distinct from the 100 simulated-account fault model.
Publishing to PyPI and a stable release are separate steps.
