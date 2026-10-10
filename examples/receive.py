import asyncio
from fncbale import Client, Router

router = Router()


@router.on("new")
async def on_message(event):
    # Application processing should use event.event_id for its own idempotency.
    print("New message:", event.message.rid)


@router.on("edit")
async def on_edit(event):
    print("Edited message:", event.message.rid)


@router.on("delete")
async def on_delete(event):
    print("Deleted messages:", event.rids)


async def main():
    async with Client("account.session", router=router):
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
