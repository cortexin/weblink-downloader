import asyncio


def future(result = None):
    f = asyncio.Future()
    f.set_result(result)
    return f
