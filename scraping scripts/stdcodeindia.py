from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from scrapy.selector import Selector
from pprint import pprint
import threading
import time
import json
import requests

def main(state_link,std_final_data,lock):
     
    std_temp=[]

    if ' ' in state_link:
        state_link.replace(' ','%20')
    if '&' in state_link:
        state_link.replace('&','%26')


    driver.get(f"https://stdcodes.bharatiyamobile.com/Indian-STD-Codes-Statewise.php?state={state_link}")

    while True:
        try:
            table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//td[h2[contains(text(),' STD codes in ')]]//table")))

            html_data = driver.page_source
            parsed_html= Selector(text=html_data)

            std_list=parsed_html.xpath("//td[h2[contains(text(),' STD codes in ')]]//table/tbody/tr[position() !=1]")

            for std_id,std in enumerate(std_list):

                std_city=std.xpath("td[1]/text()").extract_first()
                std_code=std.xpath("td[2]/a/text()").extract_first()

                std_temp.append({"code":std_code,"area":std_city})

                
            next_button = driver.find_element(By.XPATH, "//a[span[text()='>']]")

            next_button.click()

        except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
            print("No more pages to load for ",state_link)
            break
    
    with lock:
        std_final_data[state_link]=std_temp


base_link="https://stdcodes.bharatiyamobile.com"

statecount_list=[]
statename_list=[]

response = requests.get(base_link)

if response.status_code == 200:
    html_data = response.text

parsed_html= Selector(text=html_data)

js_data = parsed_html.xpath("//script[contains(text(),'statename')]/text()").extract_first()
if 'scount[' and 'statename[' in js_data:
        for line in js_data.split(';'):
            if 'scount[' in line:
                statecount = line.split('=')[1].strip().strip("'")
                statecount_list.append(statecount)
            if 'statename[' in line:
                state = line.split('=')[1].strip().strip("'")
                statename_list.append(state)

statedata=dict(zip(statename_list,statecount_list))



options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

## THESE OPTIONS TO ARE USED TO ENABLE HEADLESS MODE (NO GUI) ##
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)



print("State Data obtained: ")

pprint(statedata)

print(f"Total number of STD codes found (Including Duplicates): {sum(int(value) for value in statedata.values())}")

std_final_data={}
threads_list=[]
lock = threading.Lock()


for state_link in statedata.keys():
    t=threading.Thread(target=main,args=[state_link,std_final_data,lock])
    t.start()
    threads_list.append(t)

for thread in threads_list:
    thread.join()

    


with open('std_data.json', 'w') as outfile:
    json.dump(std_final_data,outfile,indent=4)
    
driver.quit()
