# fncbale

An independent, typed, async Python SDK for **Bale user accounts**.

کتابخانهٔ مستقل Python برای حساب کاربری بله؛ ارسال و دریافت، مدیا و آلبوم،
رویدادهای ویرایش و حذف، و عملیات پایدار قابل‌پیگیری.

[فارسی](https://milad01rmz.github.io/fncbale/#fa/overview) ·
[English documentation](https://milad01rmz.github.io/fncbale/#en/overview) ·
[Releases](https://github.com/milad01rmz/fncbale/releases) ·
[API reference](docs/API.md)

**0.1.36 is an alpha.** Python 3.12+; Windows and Linux. No other Bale SDK is a
runtime dependency. Bot API, calls, and financial operations are outside this version.

## Install

With Git installed:

```sh
python -m pip install "fncbale @ git+https://github.com/milad01rmz/fncbale.git@v0.1.36"
```

Or download the wheel from [Releases](https://github.com/milad01rmz/fncbale/releases)
and install it without Git:

```sh
python -m pip install ./fncbale-0.1.36-py3-none-any.whl
```

This release is distributed on GitHub; a PyPI publication is not claimed.

## Create a session

From a repository checkout:

```sh
git clone https://github.com/milad01rmz/fncbale.git
cd fncbale
python -m pip install .
python examples/login.py account.session
```

The example asks for your own phone number and login code. Keep session files and
local data private. Reuse the same session and data directory after restart.
See [login guide](https://milad01rmz.github.io/fncbale/#en/authentication) for a standalone
callback example, staged UI login, and explicit session import.

## Send a message and an album

```python
import asyncio
from fncbale import Client, Media, MediaKind

async def main():
    async with Client("account.session", data_dir=".fncbale/app") as client:
        peer = await client.resolve_peer("@yourchannel")
        message = await client.send_message(peer, "Hello · *bold* · _italic_")
        await client.send_message(peer, "A reply", reply_to=message)
        await client.send_album(peer, [
            Media("photo.jpg", MediaKind.PHOTO, caption="Album caption"),
            Media("clip.mp4", MediaKind.VIDEO),
        ])

asyncio.run(main())
```

Albums accept 2–10 photos/videos. Metadata is extracted from real files; no automatic
transcoding or album splitting. Independent `copy_message` / `copy_album` preserve
existing content and reusable file references without forwarding.

## Find a chat ID / گرفتن چت‌آیدی

```sh
python examples/chat_id.py account.session @yourchannel
```

```python
peer = await client.resolve_peer("@yourchannel")
print(peer.id, peer.kind.value)
```

Use the resolved `Peer` for requests. A browser URL's `uid` is not necessarily the
canonical channel ID. Numeric IDs require a verified peer kind.

[راهنمای چت‌آیدی](https://milad01rmz.github.io/fncbale/#fa/chat-id) ·
[Chat ID guide](https://milad01rmz.github.io/fncbale/#en/chat-id)

## Receive events

```python
import asyncio
from fncbale import Client, Router

router = Router()

@router.on("new")
async def on_message(event):
    if event.message:
        print(event.message.text)

@router.on("edit")
async def on_edit(event):
    print("Edited:", event.message.rid)

@router.on("delete")
async def on_delete(event):
    print("Deleted:", event.rids)

async def main():
    async with Client("account.session", router=router, data_dir=".fncbale/app"):
        await asyncio.Event().wait()

asyncio.run(main())
```

Successful handlers ACK automatically. For application-controlled ACKs, use
`client.events()` instead. Unacknowledged events may be redelivered with a stable
`event_id`; make application side effects idempotent. Failed handlers have durable
quarantine and explicit replay.

## Delivery and recovery

- SQLite WAL/FULL commits durable outbox, inbox, and all-route recovery checkpoints.
- `enqueue_*` returns an operation handle after commit; cancelling a wait does not retract accepted work.
- WebSocket is primary; equivalent RPCs can use bounded HTTP fallback.
- Ambiguous writes reconcile with fixed IDs and stay `uncertain` if delivery cannot be proven.
- Cross-route ambiguous-write retry requires method-specific evidence; it is disabled by default.
- RPC confirmation, history verification, and read receipts are distinct.
- Server-retention gaps are reported explicitly; unavailable events are not fabricated.

See [durability guide](https://milad01rmz.github.io/fncbale/#en/reliability) and
[support matrix](docs/CAPABILITY_MATRIX.md). Exactly-once application side effects
or zero loss under every external condition are not promised.

## Develop

```sh
python -m pip install ".[dev]"
python -m pytest -q
ruff check src tests examples tools
ruff format --check src tests examples tools
python -m build --wheel
```

Default tests are offline. The reviewed 0.1.35 regression baseline passed 384 tests on Windows
(one host symlink skip) and 385 on Linux. The 100-client load/fault coverage is a
local model, not 100 authenticated accounts or a service throughput guarantee.
CI runs the offline suite on Windows and Linux.

The documentation is plain HTML/CSS/JavaScript with local fonts, Persian/English,
RTL/LTR, light/dark mode, local search, and copyable code. Preview it with:

```sh
python -m http.server 8765 --directory docs/site
```

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md).
License: [MIT](LICENSE); adapted protocol definitions and font attribution:
[third-party notices](THIRD_PARTY_NOTICES.md).
