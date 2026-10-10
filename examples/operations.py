"""Inspect operation summaries; connecting also resumes the existing durable outbox."""

import argparse
import asyncio
import json

from fncbale import Client, Session


async def main(args):
    session = Session.import_aiobale(args.session) if args.import_aiobale else args.session
    async with Client(session, data_dir=args.data_dir) as client:
        async for operation in client.iter_operations(statuses=args.status or None, limit=args.limit):
            print(
                json.dumps(
                    {
                        "operation_id": operation.operation_id,
                        "status": operation.status,
                        "method": operation.method,
                        "attempts": operation.attempts,
                        "rpc_confirmed": operation.rpc_confirmed,
                        "history_verified": operation.history_verified,
                    }
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", help="Native session file or explicitly imported AioBale auth file")
    parser.add_argument("--data-dir", default=".fncbale")
    parser.add_argument("--import-aiobale", action="store_true")
    parser.add_argument("--status", action="append")
    parser.add_argument("--limit", type=int, default=100)
    asyncio.run(main(parser.parse_args()))
