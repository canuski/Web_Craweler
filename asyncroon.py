import asyncio


async def async_hello():
    await asyncio.sleep(3)
    print('Hello World!')


async def async_fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        await asyncio.sleep(5)
        a, b = b, a + b


async def test_werking():
    await async_hello()

    fib_generator = async_fib(10)

    async for n in fib_generator:
        print(n)

asyncio.run(test_werking())
