"""Inspect quarantine without printing contents; connecting also resumes the outbox."""

import argparse
import asyncio
import json

from fncbale import Client, Session


async def main(args):
    session = Session.import_aiobale(args.session) if args.import_aiobale else args.session
    async with Client(session, data_dir=args.data_dir) as client:
        if args.replay:
            changed = await client.replay_event(args.replay)
            print(json.dumps({"event_id": args.replay, "replayed": changed}))
            # The application's router or explicit consumer will handle it on reconnect.
            return
        async for event in client.iter_failed_events(limit=args.limit):
            if args.discard:
                if event.event_id == args.discard:
                    await event.ack()
                    print(json.dumps({"event_id": event.event_id, "discarded": True}))
                    return
            else:
                print(
                    json.dumps(
                        {
                            "event_id": event.event_id,
                            "kind": event.kind,
                            "handler_failures": event.handler_failures,
                        }
                    )
                )
        if args.discard:
            print(
                json.dumps(
                    {
                        "event_id": args.discard,
                        "discarded": False,
                        "reason": "Not found in this account's limited quarantine scan",
                    }
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session")
    parser.add_argument("--data-dir", default=".fncbale")
    parser.add_argument("--import-aiobale", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--replay", metavar="EVENT_ID")
    action.add_argument("--discard", metavar="EVENT_ID")
    asyncio.run(main(parser.parse_args()))
