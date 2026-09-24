import asyncio
from utils.configs import retry_times
async def async_retry(func,*args,**kwargs):
    last=None
    for _ in range(max(1,retry_times)):
        try:return await func(*args,**kwargs)
        except Exception as e:last=e
    raise last
