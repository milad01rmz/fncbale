"""Consume at least once with explicit ACK; no message text/token is printed."""

import argparse
import asyncio

from fncbale import Client


async def main(session_path):
    async with Client(session_path) as client:
        async for event in client.events():
            # Commit application processing/idempotency by event.event_id before ACK.
            print(event.event_id, event.kind)
            await event.ack()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session")
    asyncio.run(main(parser.parse_args().session))
