from prisma import Client

db = Client()
async def test():
    await db.connect()
    users = await db.user.find_many()  # Replace 'user' with any existing table
    print(users)
    await db.disconnect()

import asyncio
asyncio.run(test())
