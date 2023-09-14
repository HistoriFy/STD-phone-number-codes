from scrapy.selector import Selector
import json
import requests
from pprint import pprint
import os

link="https://en.wikipedia.org/wiki/Mobile_telephone_numbering_in_India"

response = requests.get(link)


if response.status_code == 200:
    html_data = response.text

parsed_html= Selector(text=html_data)

code_data={}

#### 9xxx series ####

code_list= parsed_html.xpath("//h2[span[contains(text(),'9xxx series')]]/following-sibling::table[1]//tr[position() !=1]/td[position() mod 4 = 1]").extract()
operator_list = parsed_html.xpath("//h2[span[contains(text(),'9xxx series')]]/following-sibling::table[1]//tr[position() !=1]/td[position() mod 4 = 2]").extract()
state_list= parsed_html.xpath("//h2[span[contains(text(),'9xxx series')]]/following-sibling::table[1]//tr[position() !=1]/td[position() mod 4 = 3]").extract()

code_list=[s.replace('<td>', '').replace('</td>', '').replace('\n','') for s in code_list]
operator_list=[s.replace('<td>', '').replace('</td>', '').replace('\n','') for s in operator_list]
state_list=[s.replace('<td>', '').replace('</td>', '').replace('\n','') for s in state_list]


op_state_data=[{'Operator': op, 'Circle': circ} for op, circ in zip(operator_list,state_list)]

#code_data = dict(zip(code_list, operator_list))
code_data = {key:value for key,value in zip(code_list,op_state_data) if value['Operator'] !='' and value['Circle'] !=''}



#### other series ####

code_list= parsed_html.xpath("//h2[span[contains(text(),'series')][not(contains(text(),'9xxx'))]]/following-sibling::table//tr/td[position() mod 3 = 1]").extract()
operator_list = parsed_html.xpath("//h2[span[contains(text(),'series')][not(contains(text(),'9xxx'))]]/following-sibling::table//tr/td[position() mod 3 = 2]").extract()
state_list = parsed_html.xpath("//h2[span[contains(text(),'series')][not(contains(text(),'9xxx'))]]/following-sibling::table//tr/td[position() mod 3 = 3]").extract()

code_list=[s.replace('<td>', '').replace('</td>', '') for s in code_list]
operator_list=[s.replace('<td>', '').replace('</td>', '') for s in operator_list]
state_list=[s.replace('<td>', '').replace('</td>', '') for s in state_list]

op_state_data=[{'Operator': op, 'Circle': circ} for op, circ in zip(operator_list,state_list)]

code_data.update({key:value for key,value in zip(code_list,op_state_data) if value['Operator'] !='' and value['Circle'] !=''})


#pprint (code_data)

with open('indian_no_data.json', 'w') as outfile:
    json.dump(code_data,outfile,indent=4)








