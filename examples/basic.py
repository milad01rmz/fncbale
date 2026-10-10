import asyncio
from fncbale import Client, Media, MediaKind


async def main():
    async with Client("account.session") as client:
        peer = await client.resolve_peer("@your_test_channel")
        message = await client.send_message(peer, "سلام", idempotency_key="example-message-1")
        await client.edit_message(message, "سلام، ویرایش شد")
        await client.send_album(
            peer, [Media("photo.png", MediaKind.PHOTO), Media("video.mp4", MediaKind.VIDEO)]
        )


if __name__ == "__main__":
    asyncio.run(main())
