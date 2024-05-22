#-l=int -s="str" start clicking each
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import traceback
from datetime import datetime
#reference https://www.youtube.com/watch?v=tp_B5tpJS3c

@dataclass
class Business:
#     """holds business data"""
    name: str = None
    address: str = None
    category: str = None
    #openhours: str = None
    #website: str = None
    #phone_number: str = None
    latitude: float = None
    longitude: float = None
    #opentime: dict = field(default_factory=dict)
    #closetime: dict = field(default_factory=dict)
    popular_times: dict = field(default_factory=dict)


@dataclass
class BusinessList:
    """holds list of Business objects,
     and save to both excel and csv
     """
    business_list: list[Business] = field(default_factory=list)
    save_at = 'output'

    def dataframe(self):
        """transform business_list to pandas dataframe

         Returns: pandas dataframe
         """
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )
    # def save_to_excel(self, filename):
    #     """saves pandas dataframe to excel (xlsx) file

    #      Args:
    #          filename (str): filename
    #      """

    #     if not os.path.exists(self.save_at):
    #         os.makedirs(self.save_at)
    #     self.dataframe().to_excel(f"output/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """saves pandas dataframe to csv file

         Args:
             filename (str): filename
         """

        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        df = self.dataframe().reset_index()
        df.to_csv(f"output/{filename}.csv", index=False)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    """helper function to extract coordinates from url"""
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])


def main():
    ########
    # input 
    ########
    # read search from arguments
    #vancouver downtown is  -lat=49.2898585 -lon=-123.1257873
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-l", "--total", type=int)
    parser.add_argument("-lat", "--latitude", type=float)
    parser.add_argument("-lon", "--longtitude", type = float)
    args = parser.parse_args()
    
    if args.search:
        search_list = [args.search]
        
    if args.total:
        total = args.total
    else:
        # if no total is passed, we set the value to random big number
        total = 1_000_000
    
    if args.latitude:
        latin = args.latitude
    else:
        latin = 0
    if args.longtitude:
        lonin = args.longtitude
    else:
        lonin = 0

    if not args.search:
        search_list = []
        # read search from input.txt file
        input_file_name = 'input.txt'
        # Get the absolute path of the file in the current working directory
        input_file_path = os.path.join(os.getcwd(), input_file_name)
        # Check if the file exists
        if os.path.exists(input_file_path):
        # Open the file in read mode
            with open(input_file_path, 'r') as file:
            # Read all lines into a list
                search_list = file.readlines()
                
        if len(search_list) == 0:
            print('Error occured: You must either pass the -s search argument, or add searches to input.txt')
            sys.exit()
        
    ###########
    # scraping
    ###########
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-US")
        url = f'https://www.google.com/maps/@{latin},{lonin},15z?entry=ttu'
        #url = f'https://www.google.com/maps/@?api=1&map_action=map&center={latin},{lonin}&zoom=zoom'
        page.goto(url)
        # wait is added for dev phase. can remove it in production
        page.wait_for_load_state('domcontentloaded') #sleep for five seconds
        
        for search_for_index, search_for in enumerate(search_list):
            print(f"-----\n{search_for_index} - {search_for}".strip())
            #inspecter mode: see the id of input
            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(300)

            page.keyboard.press("Enter")
            page.wait_for_timeout(300)
            #now all businessses
            # scrolling
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            # this variable is used to detect if the bot
            # scraped the same number of listings in the previous iteration
            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(1000)

                if (
                    page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).count()
                    >= total
                ):
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    # logic to break from loop to not run infinitely
                    # in case arrived at all available listings
                    if (
                        page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        == previously_counted
                    ):
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()
                        print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                        break
                    else:
                        previously_counted = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        print(
                            f"Currently Scraped: ",
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count(),
                        )

            business_list = BusinessList()

            # scraping
            for listing in listings:
                try:
                    listing.click()
                    page.wait_for_timeout(5000)

                    business = Business()

                    name_xpath = '//h1[@class="DUwDvf lfPIob"]'
                    namelabel = page.locator(name_xpath)

                    #address_xpath = '//div[@class="rogA2c"]' 
                    address_xpath = '//div[@class="Io6YTe fontBodyMedium kR99db "]'
                    #address_xpath = '//div[@class="Io6YTe fontBodyMedium kR99db " and contains(text(), ", BC")]'
                    addresslabel = page.locator(address_xpath).first
                    
                    category_xpath = '//button[@class="DkEaL "]'
                    categorylabel = page.locator(category_xpath)
                    
                    
                    
                    #website_xpath = ''
                    #webistelabel = page.locator()
                    #phone_number_xpath = ''
                    #phone_numberlabel = page.locator()

                    #popxpath = '//div[@class="g2BVhd eoFzo "]'
                    #popxpath = '.g2BVhd' 
                    #popxpath2 ='//div[@class="dpoVLd"]|//div[@class="dpoVLd finExf"]'
                    #popxpath2 = '.dpoVLd'
                    #popchildlabel = poplabel.locator(popxpath2)
                
                    popxpathex = '.g2BVhd .dpoVLd'
                    poplabel = page.locator(popxpathex).all()
                    
                    #openhourslabel = page.locator(address_xpath).nth(1) #class is same as address one                                   
                    
                    if namelabel.text_content() != None:
                        business.name = namelabel.text_content()
                    else:
                        business.name = ""
                    if addresslabel.text_content() != None:
                        business.address = addresslabel.text_content()
                    else:
                        business.address = ""
                    if categorylabel.text_content() != None:
                        business.category = categorylabel.text_content()
                    else:
                        business.category = ""    
                    
                    if len(poplabel) > 0:
                        popular_data = {}
                        today = datetime.today()
                        now = datetime.now()
                        dayofweek = today.weekday()
                        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        i = dayofweek
                        formateddict = {}
                        for day in days:
                            for hour in range(0, 24):
                                if(hour<12):
                                    t = f'{hour} a.m.'
                                else:
                                    t = f'{hour-12} p.m.'
                                key = f'{day} {t}'
                                formateddict[key] = "None"
                                    
                        for label in poplabel:
                            if days[i] not in popular_data:
                                popular_data[days[i]] = []
                            popular_data[days[i]].append(label.get_attribute('aria-label').replace('\u202f', ' '))  
                            #popular_data[days[i]].append(label.get_attribute('aria-label').replace('\u202f', ' '))   
                            i=(i+1) % 7    
                        new_data = {day: popular_data[day] for day in days if day in popular_data}
                        #print(new_data)
                        for day, values in new_data.items():
                            for value in values:
                            # Extracting percentage and time
                                info = value.split()  # Extracting ['66%', 'busy', 'at', '9', 'a.m..']
                                percentage = info[0]
                                if info[0] == 'Currently':
                                    percentage= info[4]  # template: Currently 0% busy, usually 33% busy.
                                    now = now.hour
                                    if now < 12:
                                        time = f'{now} a.m.'
                                    else:
                                        time = f'{now-12} p.m.'
                                else:
                                    percentage = info[0]
                                    time = info[3]
                                    timestr = info[4].replace('..', '.')  # Extracting '9 a.m.'
                                    time = f'{time} {timestr}'
                                key = f'{day} {time}'
                                formateddict[key] = percentage
                        business.popular_times = formateddict
                        
                        

                    else:
                        business.popular_times = ""
                    # if page.locator(website_xpath).count() > 0:
                    #     business.website = page.locator(website_xpath).all()[0].inner_text()
                    # else:
                    #     business.website = ""
                    # if page.locator(phone_number_xpath).count() > 0:
                    #     business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                    # else:
                    #     business.phone_number = ""
                    #if (openhourslabel.text_content() != None):
                    #    business.openhours = openhourslabel.text_content().replace('\u202f', ' ')
                    #else:
                    #    business.openhours = ""

                    
                    
                    business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                    business_list.business_list.append(business)
                    #print(business)
                except Exception as e:
                    print(traceback.format_exc())
                    print(f'Error occured: {e}')
            
            #########
            # output
            #########
            #business_list.save_to_excel(f"google_maps_data_{search_for}".replace(' ', '_'))
            business_list.save_to_csv(f"google_maps_data_{search_for}".replace(' ', '_'))

        browser.close()
        


if __name__ == "__main__":
    main()