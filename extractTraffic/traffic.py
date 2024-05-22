#! /usr/bin/env python3
from playwright.async_api import async_playwright
import asyncio
import os
import sys

with open(os.path.join(os.path.dirname(__file__),"traffic.js")) as f:
    script = f.read()

async def save(download, file):
    await download.save_as(file)
    print(f"Saved {file}")

async def runBrowser(playwright, lat, long, zoom, out):
    times = []
    for i in range(8,21):
        for j in range(12):
            postfix = "am"
            if i > 10:
                postfix = "pm"
            times.append(f"{i%12+1}-{j*5:02d}{postfix}")
    times.append('10-00pm')
    for i in range(6,9):
        for j in range(12):
            times.append(f"{i}-{j*5:02d}am")
    assert len(times) == 193
    runBrowser = False
    for day in ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'):
        for time in range(0, len(times)):
            if not '00' in times[time]:
                continue
            img_name = f"{out}/{day}-{times[time]}.png"
            if not os.path.isfile(img_name):
                runBrowser = True
                break
        if runBrowser:
            break
    if not runBrowser:
        print(f"already downloaded {out}")
        return
    print(f"downloading {out}")
    chrome = playwright.chromium
    browser = await chrome.launch(channel="chrome",args=['--window-size=2222,2222'])
    context = await browser.new_context(viewport={'width':2222,'height':2222})
    page = await context.new_page()
    page.on("console", lambda msg: print(msg))
    page.on("pageerror", lambda msg: print(msg))
    await page.add_init_script(script=script)
    await page.goto(f"https://www.google.com/maps/@?api=1&map_action=map&center={lat},{long}&zoom={zoom}", timeout=0)
    try:
        async with page.expect_download(timeout=4000) as download_info:
            await page.reload()
        download = await download_info.value
        await save(download, f"{out}/base.png")
    except:
        print(f"failed to load {lat}, {long} check if these coords are in an invalid location", file=sys.stderr)
    await page.goto(f"https://www.google.com/maps/@?api=1&map_action=map&center={lat},{long}&zoom={zoom}&layer=traffic", timeout=0)
    for day in ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'):
        time = 0
        try:
            async with page.expect_download(timeout=6000) as download_info:
                if day == 'Monday':
                    await page.locator(".goog-menu-button-inner-box").filter(has_text='Live traffic').click()
                    await page.locator(".goog-menuitem-content").filter(has_text='Typical traffic').click()
                else:
                    await page.locator(".UGyhhe").locator(f"button[aria-label='{day}']").click()
            download = await download_info.value
            img_name = f"{day}-{times[time]}"
            await save(download, f"{out}/{img_name}.png")
        except:
            print(f"skipping {day}-{times[time]}")
            pass
        for time in range(1, len(times)):
            if not '00' in times[time]:
                continue
            try:
                img_name = f"{day}-{times[time]}"
                if os.path.isfile(f"{out}/{img_name}.png"):
                    print(f"already downloaded {day}-{times[time]}")
                    continue
                async with page.expect_download(timeout=3000) as download_info:
                    box = await page.locator("div[jsaction='layer.timeClicked']").bounding_box()
                    offset = box['x'] + ((36+time)%193) * box['width']//193
                    await page.mouse.click(offset, box['y']+box['height']//2)
                download = await download_info.value
                await save(download, f"{out}/{img_name}.png")
            except:
                print(f"skipping {day}-{times[time]}")
                pass
    await browser.close()

async def main(lat, long, zoom, out):
    async with async_playwright() as playwright:
        await runBrowser(playwright, lat, long, zoom, out)

def download(lat, long, zoom, out):
    if not os.path.exists(out):
        os.mkdir(out)
    asyncio.run(main(lat, long, zoom, out))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f"python sys.argv[0] {latitude} {longitude} {zoom} {out}")
    download(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
