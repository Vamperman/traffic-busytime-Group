import pandas as pd
import sys
from playwright.sync_api import sync_playwright, expect
from dataclasses import dataclass, asdict, field

file_path = sys.argv[1]
city = sys.argv[2].capitalize()
outname = sys.argv[3]
if len(sys.argv) >= 5:
    keyword = sys.argv[4]
else:
    keyword = ''
#keywords is from below review


df = pd.read_csv(file_path)
df = df.dropna(subset=df.iloc[:, 6:].columns, how='all')
if len(keyword) > 0:
    df = df[df['category'].str.contains(keyword)]
df = df[df['address'].str.contains(city)].reset_index(drop=True)

#add latitude and longitude
with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-US")

        i = 0
        for search in df['address']:
            url = 'https://www.google.com/maps/@21z?entry=ttu'
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
            #inspecter mode: see the id of input
            page.locator('//input[@id="searchboxinput"]').fill(search)
            page.wait_for_timeout(300)
            page.keyboard.press("Enter")
            page.wait_for_timeout(3000)
            page.reload()
            page.wait_for_timeout(3000)
            page.locator('button.yra0jd').first.click()            

        # Click the button
            zoom_button = page.locator('button[aria-label="Zoom in"]').first
            
            expect(zoom_button).to_be_enabled()

            viewport = page.viewport_size
            page.mouse.click(viewport["width"] / 2, viewport["height"] /2,button="right")

            page.wait_for_timeout(3000)
            coordinate_xpath = '//div[@class="mLuXec"]'
            coordinatelabel = page.locator(coordinate_xpath).first
            
            coor =coordinatelabel.text_content()
            latitude, longitude = coor.split(', ')
            df.loc[i, 'latitude'] = float(latitude)
            df.loc[i, 'longitude'] = float(longitude)
            i += 1
           
df.to_csv(f"cleanoutput/{outname}.csv", index=False)
