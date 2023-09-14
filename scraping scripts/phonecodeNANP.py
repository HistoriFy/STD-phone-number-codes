from scrapy.selector import Selector
import json
import requests
from pprint import pprint
import os

link="https://en.wikipedia.org/wiki/List_of_North_American_Numbering_Plan_area_codes"

response = requests.get(link)


if response.status_code == 200:
    html_data = response.text

parsed_html= Selector(text=html_data)

code_data={}

# 200-299 on the website contains the hyphen as a Unicode character
# hence searching for the hyphen in the xpath can give erronous results sometimes
code_list=['200','300','400','500','600','700','800','900']

for code in code_list:
    code_table=parsed_html.xpath(f"//h3[span[contains(text(),{code})]]/following-sibling::table[1]/tbody/tr[position() != 1]")

    for row in code_table:
        code_no=row.xpath("td[1]//text()").extract_first()
        state_name=row.xpath("td[2]/descendant-or-self::*//text()").extract()
        state_sen=[s.replace('\n','') for s in state_name]
        state_sen=''.join(filter(None, state_sen))

        if "not in use;" not in state_sen:
            code_data.update({code_no:state_sen})



with open('nanp_no_data.json', 'w') as outfile:
    json.dump(code_data,outfile,indent=4)
