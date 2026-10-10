"""Resolve a target with multiple independent sessions using shared bounded resources."""

import argparse
import asyncio

from fncbale import AccountPool


async def main(args):
    async with AccountPool(data_dir=args.data_dir) as pool:
        clients = [
            (f"account-{index}", pool.add(f"account-{index}", path))
            for index, path in enumerate(args.sessions)
        ]

        async def inspect(name, client):
            await client.connect()
            peer = await client.resolve_peer(args.peer)
            print(name, peer.kind, peer.id)

        await asyncio.gather(*(inspect(name, client) for name, client in clients))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sessions", nargs="+")
    parser.add_argument("--peer", default="@codextest1")
    parser.add_argument("--data-dir", default=".fncbale")
    asyncio.run(main(parser.parse_args()))
