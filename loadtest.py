"""
Load / overload test tool.
Đích: https://cruel.toys/maze/

Cần: pip install aiohttp
Chạy:  python loadtest.py
"""

import asyncio
import random
import socket
import time
from urllib.parse import urlparse

import aiohttp

# ------------------- CONFIG -------------------
TARGET       = "HTTP..." 
DURATION     = 60                     # giây
CONCURRENCY  = 100                    # số coroutine song song (tăng để overload)
RAMP_UP      = 10                     # giây tăng dần lên đủ CONCURRENCY (0 = full ngay)
TIMEOUT      = 10                     # timeout mỗi request (giây)
JITTER       = (0.0, 0.05)           # nghỉ ngẫu nhiên giữa các request (giây)
# ----------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile Safari/604.1",
]

stats = {"total": 0, "success": 0, "errors": 0, "status": {}}


def make_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Connection": "keep-alive",
    }


async def worker(session, stop_at, delay_start=0.0):
    if delay_start:
        await asyncio.sleep(delay_start)   # ramp-up: coroutine vào dần
    while time.time() < stop_at:
        try:
            async with session.get(TARGET, headers=make_headers()) as resp:
                await resp.read()
                stats["total"] += 1
                stats["status"][resp.status] = stats["status"].get(resp.status, 0) + 1
                if resp.status == 200:
                    stats["success"] += 1
        except Exception as e:
            stats["total"] += 1
            stats["errors"] += 1
            key = type(e).__name__
            stats["status"][key] = stats["status"].get(key, 0) + 1
        if JITTER != (0.0, 0.0):
            await asyncio.sleep(random.uniform(*JITTER))


async def reporter(stop_at):
    last = 0
    while time.time() < stop_at:
        await asyncio.sleep(1)
        now = stats["total"]
        print(f"[{time.strftime('%H:%M:%S')}] {now - last:>5} req/s  |  tổng: {now}")
        last = now


async def main():
    print(f"[{time.strftime('%H:%M:%S')}] Bắt đầu test -> {TARGET}")
    print(f"    concurrency={CONCURRENCY}, ramp_up={RAMP_UP}s, duration={DURATION}s\n")

    start = time.time()
    stop_at = start + DURATION
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, force_close=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for i in range(CONCURRENCY):
            delay = (RAMP_UP * i / CONCURRENCY) if RAMP_UP else 0.0
            tasks.append(asyncio.create_task(worker(session, stop_at, delay)))
        tasks.append(asyncio.create_task(reporter(stop_at)))
        await asyncio.gather(*tasks)

    elapsed = time.time() - start
    avg = stats["total"] / elapsed if elapsed else 0
    print("\n" + "=" * 40)
    print("KẾT QUẢ")
    print("=" * 40)
    print(f"Thời gian    : {elapsed:.2f} s")
    print(f"Tổng request : {stats['total']}")
    print(f"Thành công   : {stats['success']}")
    print(f"Lỗi          : {stats['errors']}")
    print(f"Trung bình    : {avg:.1f} req/s")
    print("Phân bố status / lỗi:")
    for k, v in sorted(stats["status"].items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Dừng bởi người dùng.")
