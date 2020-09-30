import asyncio

import aiodns
from nats.aio.client import Client
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

EXIT = False


async def message_handler(msg):
    global EXIT
    subject = msg.subject
    reply = msg.reply
    data = msg.data.decode()
    print(
        "Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data
        )
    )
    if subject == "nslookup":
        result = await resolve(data)
        nc = Client()
        await nc.connect("localhost:4222", loop=loop)
        await nc.publish(reply, f"{result}".encode())
        await nc.close()

    if data == "quit":
        EXIT = True


async def resolve(domain):
    loop = asyncio.get_event_loop()
    resolver = aiodns.DNSResolver(loop=loop)
    result = await resolver.query("google.com", "A")
    return result


async def run(loop):
    nc = Client()
    await nc.connect("localhost:4222", loop=loop)

    sid = await nc.subscribe(">", cb=message_handler)

    while not EXIT:
        await asyncio.sleep(1.0)

    print("Exiting...")
    # Remove interest in subscriptions
    await nc.unsubscribe(sid)
    await nc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
