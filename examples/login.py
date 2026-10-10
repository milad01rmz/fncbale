"""Create a native session; phone/code/password are supplied interactively."""

import argparse
import asyncio
import getpass

from fncbale import Client, PasswordRequired
from fncbale.errors import RpcError


async def code_callback(_challenge):
    return await asyncio.to_thread(getpass.getpass, "Login code: ")


async def password_callback():
    return await asyncio.to_thread(getpass.getpass, "Account password: ")


async def main(session_path):
    phone = await asyncio.to_thread(input, "Phone number: ")
    client = Client(session_path)
    try:
        challenge = await client.start_login(phone.strip())
        for attempt in range(3):
            try:
                await client.complete_login(challenge, await code_callback(challenge.response()))
                break
            except PasswordRequired:
                await client.complete_password_login(challenge, await password_callback())
                break
            except RpcError as exc:
                if exc.reason != "PHONE_CODE_INVALID" or attempt == 2:
                    raise
                print("Code rejected; retrying input on the same login request.")
        await client.connect()
        print("Native session saved; connection ready.")
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", help="Destination native session file")
    asyncio.run(main(parser.parse_args().session))
