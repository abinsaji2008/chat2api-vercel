from curl_cffi.requests import AsyncSession

class Client:
    def __init__(self, proxy=None, timeout=15, verify=True, impersonate='chrome131', cookies=None):
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        self.cookies = cookies or {}
        self.session = AsyncSession(proxies=proxies, timeout=timeout, impersonate=impersonate, verify=verify)
        self.session2 = AsyncSession(proxies=proxies, timeout=timeout, impersonate=impersonate, verify=verify)
        if self.cookies:
            self.session.cookies.update(self.cookies)
            self.session2.cookies.update(self.cookies)

    async def post(self, *args, **kwargs):
        return await self.session.post(*args, **kwargs)

    async def post_stream(self, *args, headers=None, cookies=None, **kwargs):
        return await self.session2.post(*args, headers=headers, cookies=cookies if cookies is not None else self.cookies, **kwargs)

    async def get(self, *args, **kwargs):
        return await self.session.get(*args, **kwargs)

    async def request(self, *args, **kwargs):
        return await self.session.request(*args, **kwargs)

    async def put(self, *args, **kwargs):
        return await self.session.put(*args, **kwargs)

    async def close(self):
        for name in ('session', 'session2'):
            session = getattr(self, name, None)
            if session is not None:
                try:
                    await session.close()
                except Exception:
                    pass
                setattr(self, name, None)
