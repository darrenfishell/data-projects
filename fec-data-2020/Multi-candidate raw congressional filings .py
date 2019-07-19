
# coding: utf-8

# In[12]:

import numpy as np
import pandas as pd
import requests
import config
import os
import json
from pandas.io.json import json_normalize
#import pygsheets

##Schedule_a API guide: https://api.open.fec.gov/developers/#/receipts/get_schedules_schedule_a_


# In[13]:


### MULTI-CANDIDATE SEARCH ###
#Set search for all 2020 (two-year transaction period) Maine Congressional candidates
cand_state = 'ME'
period='2020'
parameters = {'election_year':period
            ,'state':cand_state
            ,'api_key':config.api_key}

#Requests candidate info
r_cands = requests.get('https://api.open.fec.gov/v1/candidates/search',params=parameters).json()

#Locates and sets Committee ID from 'principal_committees' sub-array
#Output list of IDs
comm_ids=json_normalize(data=r_cands['results'],record_path='principal_committees')['committee_id'].tolist()
comm_ids

# In[14]:

#Print committee list to validate
cand_list=json_normalize(data=r_cands['results'],record_path='principal_committees')[['committee_id','name','party']]
print(cand_list)

# In[26]:


#Initialize dataframe collector for itemized contribs
dfs=[]
id=int(0)
p=int(1)
    
#Loop through pages
for x in range(len(comm_ids)):
    
    #Print out candidate
    print(cand_list.iloc[id]['name'])
    
    querydict = {'per_page':'100'
                ,'api_key':config.api_key
                ,'committee_id':comm_ids[id]
                ,'page':p
                ,'sort_nulls_last':'false'
                ,'sort':'-contribution_receipt_date'
                ,'sort_hide_null':'false'
                }
    
    r = requests.get('https://api.open.fec.gov/v1/schedules/schedule_a/efile/',params=querydict).json()
    
    #Loop through pages
    while p <= r['pagination']['pages']:
        
        #print('page: '+str(p)+','+str(r['pagination']['per_page'])+' records')
        
        querydict.update(page=p)
        #Pull new results
        r = requests.get('https://api.open.fec.gov/v1/schedules/schedule_a/efile/',params=querydict).json()
        
        #Add results to dataframe
        df = json_normalize(r['results'])
        dfs.append(df)
        p=p+1
    
    #Reset to page 1
    p=int(1)
    #Increment to next candidate
    id=id+1

print('Job Complete')

# In[27]:

itemall=pd.concat(dfs,sort=False)
itemdf=itemall.drop_duplicates(subset='transaction_id')
itemdf


#Extract desired columns from dataset
itemdf=itemdf[[
                'committee.city'
                ,'committee.committee_id'
                ,'committee.committee_type_full'
                ,'committee.cycle'
                ,'committee.name'
                ,'committee.party_full'
                ,'committee.state_full'
                ,'contribution_receipt_amount'
                ,'contribution_receipt_date'
                ,'contributor_aggregate_ytd'
                ,'contributor_city'
                ,'contributor_employer'
                ,'contributor_first_name'
                ,'contributor_last_name'
                ,'contributor_name'
                ,'cycle'
                ,'contributor_occupation'
                ,'contributor_state'
                ,'contributor_zip'
                ,'entity_type'
                ,'filing.coverage_end_date'
                ,'filing.coverage_start_date'
                ,'filing.filed_date'
                ,'filing.is_amended'
                ,'line_number'
                ,'fec_election_type_desc'
                ,'memo_text'
                ,'filing.pdf_url'
                ,'transaction_id']]
#View deduplicated DataFrame length
len(itemdf.index)

#Write itemized individual results to local CSV
cwd = os.getcwd()
itemdf.to_csv(cwd+'/data/maine-fed-raw-itemized-receipts.csv')

# # In[19]:
# #Write itemized individual raw results to Google Sheet
# cwd = os.getcwd()
#
# #Google Credentials
# gc = pygsheets.authorize(service_file=cwd+'/me-congress-2020-creds.json')
#
# #Select sheet and worksheet
# sh = gc.open('me-congress-2020')
# #sh = gc.open_by_key('1AKrgHT9NLpoddV16B7_M_0PEjJmMQAGtXJUnLCTDHjA')
# wks = sh[3]
#
# #Clear sheet before load
# wks.clear(start='A1',fields='*')
#
# #Write contribs dataframe to sheet
# wks.set_dataframe(itemdf,(1,1))
#
