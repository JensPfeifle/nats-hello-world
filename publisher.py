import asyncio
from nats.aio.client import Client
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


async def run(loop):
    nc = Client()

    await nc.connect("localhost:4222", loop=loop)

    # publish some messages
    await nc.publish("foo", b"Hello")
    await asyncio.sleep(1.0)
    await nc.publish("foo", b"World")
    await asyncio.sleep(1.0)
    await nc.publish("foo", b"!!!!!")
    await asyncio.sleep(1.0)

    # Send a request and expect a single response
    # and trigger timeout if not faster than 1 second.
    try:
        response = await nc.request("nslookup", b"google.com", timeout=1)
        print("Received response: {message}".format(message=response.data.decode()))
    except ErrTimeout:
        print("Request timed out")

    # await nc.publish("foo", b"quit")
    # await asyncio.sleep(1.0)

    # Terminate connection to NATS.
    await nc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
