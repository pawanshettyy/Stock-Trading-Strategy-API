from prisma import Prisma
import contextlib
from typing import AsyncGenerator

# Create a generator function for Prisma client to use as a dependency
async def get_prisma() -> AsyncGenerator[Prisma, None]:
    prisma = Prisma()
    await prisma.connect()
    try:
        yield prisma
    finally:
        await prisma.disconnect()

# Context manager for Prisma client
@contextlib.asynccontextmanager
async def get_prisma_client():
    prisma = Prisma()
    await prisma.connect()
    try:
        yield prisma
    finally:
        await prisma.disconnect()