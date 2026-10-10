"""Resolve a username or a known-kind numeric ID using an existing native session."""

import argparse
import asyncio
import json
import sys

from fncbale import Client, PeerKind


async def main(args):
    target = int(args.target) if args.target.lstrip("-").isdigit() else args.target
    if isinstance(target, int) and args.kind is None:
        raise ValueError(
            "Numeric IDs require --kind user, group, or channel; browser UIDs are not canonical IDs"
        )
    async with Client(args.session, data_dir=args.data_dir) as client:
        peer = await client.resolve_peer(target, kind=args.kind)
        print(
            json.dumps(
                {"chat_id": peer.id, "kind": peer.kind.value, "username": peer.username, "title": peer.title},
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", help="An existing native session file")
    parser.add_argument("target", help="Exact @username or a verified numeric ID")
    parser.add_argument("--kind", choices=[kind.value for kind in PeerKind])
    parser.add_argument("--data-dir", default=".fncbale/chat-id")
    asyncio.run(main(parser.parse_args()))
