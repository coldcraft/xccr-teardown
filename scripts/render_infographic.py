"""Render baseline/infographic.html to PNG with Playwright (use the schizospider venv)."""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent.parent
SRC = (HERE / "baseline/infographic.html").as_uri()
OUT = HERE / "baseline/infographic.png"


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1100, "height": 900}, device_scale_factor=2)
        await pg.goto(SRC)
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=str(OUT), full_page=True)
        await b.close()
    print("wrote", OUT)


asyncio.run(main())
