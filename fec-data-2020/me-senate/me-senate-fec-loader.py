#!/usr/bin/env python
# coding: utf-8

# ## Maine Senate overview script
# 
# This file pulls in individual contributions to all Senate committees as well as independent expenditures to support or oppose the candidates _and_ party-coordinated expenditures to support or oppose the candidates.
# 
# The data fuels a dashboard that contains an overview of the race so far. It also provides the information to reconcile itemized contribution data with campaign totals available from the FEC.
# 
# For Susan Collins, there is potentially significant variance between these sources and the cause is not yet clear.
# 
# *Question*: What to make of the amended status? Test what's getting pulled out by dropping duplicates on transaction ID. Are the wrong records being retained?

# In[10]:


import numpy as np
import pandas as pd
import requests
import config
import os
import datadotworld as dw
from pandas.io.json import json_normalize

##Schedule_a API guide: https://api.open.fec.gov/developers/#/receipts/get_schedules_schedule_a_˜


# In[11]:


### INDIVIDUAL DONATIONS TO MAINE SENATE CAMPAIGNS ###
## SENATE COMMITTEE SEARCH ##
#Set search for all 2020 (two-year transaction period) Maine Senate candidates
cand_state = 'ME'
period='2020'
parameters = {'election_year':period
            ,'state':cand_state
            ,'office':'S'
            ,'api_key':config.api_key}

#Requests candidate info
r_cands = requests.get('https://api.open.fec.gov/v1/candidates/search',params=parameters).json()

#Locates and sets Committee ID from 'principal_committees' sub-array
#Output list of IDs
comm_ids=json_normalize(data=r_cands['results'],record_path='principal_committees')['committee_id'].tolist()


# In[12]:


replace_dict = {
    '<td>':''
    ,'</td>':''
   ,r'\[|\]':''
   ,r'\\n|\\t':''
   ,r"\'":''
}
## Create and publish candidate id - committee id table
lkup = json_normalize(data=r_cands['results'])[['candidate_id','name','party_full']]
lkup2 = json_normalize(data=r_cands['results'],record_path='principal_committees')[['candidate_ids','committee_id','name']].astype(str)
#Eliminate <td> tags
lkup2.replace(replace_dict,regex=True,inplace=True)
lkup = lkup.merge(lkup2,left_on='candidate_id',right_on='candidate_ids')

colnm = {
    'name_x':'candidate_name'
    ,'name_y':'committee_name'
}
lkup.rename(columns=colnm,inplace=True)
lkup.drop(columns='candidate_ids',inplace=True)

#Write out files to data.world
with dw.open_remote_file('darrenfishell/2020-election-repo','candidate_committee_lookup.csv') as w:
    lkup.to_csv(w,index=False)


# In[14]:


## FOR LOOP TO COLLECT CONTRIBUTION RECORDS ##
#Initialize dataframe collector for itemized contribs
cycle='2020'
idfs=[]
udfs=[]
commid=0

#Initialize query dictionary
itemdict = {
    'per_page':'100'
    ,'sort':'contribution_receipt_date'
    ,'api_key':config.api_key
    ,'is_individual':'true'
    ,'two_year_transaction_period':cycle
    ,'last_index':[]
    ,'last_contribution_receipt_date':[]
    ,'committee_id':comm_ids[commid]
}

#Dict for unitemized contributions
unitemdict = {
'api_key':config.api_key
,'cycle':cycle
,'per_page':'100'
,'committee_id':comm_ids[commid]
}

#Page through results for each committee id
for x in comm_ids:
    
    u_r = requests.get('https://api.open.fec.gov/v1/committee/'+comm_ids[commid]+'/totals',params=unitemdict).json()
    udf = json_normalize(u_r['results'])
    udfs.append(udf)
    
    #Get first itemized payload for a candidate
    itemr = requests.get('https://api.open.fec.gov/v1/schedules/schedule_a/',params=itemdict).json()
    
    #Print itemdict to validate
    print(itemdict)
    
    #Last page variables
    while itemr['pagination']['last_indexes'] is not None:
        
        #Store results of payload
        idf = json_normalize(itemr['results'])
        idfs.append(idf)
                
        #Assign last_index and date values, update itemdict
        last_index=pd.to_numeric(itemr['pagination']['last_indexes']['last_index'])
        last_date=itemr['pagination']['last_indexes']['last_contribution_receipt_date']
        #Update dictionary with new indices
        itemdict.update([('last_index',last_index)
                        ,('last_contribution_receipt_date',last_date)])

        #Get next payload with updated dict
        itemr = requests.get('https://api.open.fec.gov/v1/schedules/schedule_a/',params=itemdict).json()
    
    commid+=1
    
    #Update dictionary with next candidate in list and reset last indices
    itemdict.update([('committee_id',comm_ids[commid])
                     ,('last_index',[])
                     ,('last_contribution_receipt_date',[])])
    
    unitemdict.update([('committee_id',comm_ids[commid])])


# In[21]:


# Concatenate all dfs
itemdf=pd.concat(idfs,sort=False,ignore_index=True)
itemdf=itemdf.drop_duplicates(subset='transaction_id')
udf=pd.concat(udfs,sort=False,ignore_index=True)
udf=udf.drop_duplicates()

#ITEMIZED DATA CLEANING#
itemdf['contributor_zip'] = itemdf['contributor_zip'].str[:5]

#Create DataFrame with columns to match itemized table
cols=itemdf.columns.values.tolist()
unitemdf=[]
unitemdf = pd.DataFrame(columns=cols)

## Select data for unitemized df ##
unitemdf[['committee.name'
        ,'committee.party_full'
        ,'contribution_receipt_amount'
        ,'contribution_receipt_date'
        ,'fec_election_type_desc']] = udf[['committee_name'
                                        ,'party_full'
                                        ,'individual_unitemized_contributions'
                                        ,'coverage_end_date'
                                        ,'last_report_type_full']]

#Label as unitemized
unitemdf['contributor_name'] = 'Unitemized individual contributions'
unitemdf['entity_type'] = 'IND'

#Union Itemized and Unitemized contributions
ind_df = pd.concat([itemdf,unitemdf],sort=False,ignore_index=True)


# In[22]:


## WRITE OUT INDIVIDUAL DONATION FILES ##
#Write full files out to data.world project


#Test if results are longer than current file. If so, write.
results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM individual_senate_contributions')
if len(results.dataframe) > len(itemdf):
    with dw.open_remote_file('darrenfishell/2020-election-repo','individual-senate-contributions.csv') as w:
        itemdf.to_csv(w,index=False)

#Tests if contribution sum is greater than old file. If so, write.        
results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM senate_financial_summary')
if sum(results.dataframe['receipts']) > len(udf['receipts']):
    with dw.open_remote_file('darrenfishell/2020-election-repo','senate_financial_summary.csv') as w:
        udf.to_csv(w,index=False)
    

# #QA - compare itemized values to totals
# qadf = itemdf.groupby(['committee.name']).agg({'contribution_receipt_amount':['sum']})
# qadf

# totaldf = udf[['committee_name'
#              ,'individual_itemized_contributions'
#              ,'individual_unitemized_contributions']]

# qadf = qadf.merge(totaldf, left_on='committee.name',right_on='committee_name')


# In[23]:


### INDEPENDENT EXPENDITURE RETRIEVAL ###
## SENATE CANDIDATE ID SEARCH ##
cand_ids=json_normalize(data=r_cands['results'])['candidate_id'].tolist()

#Declare loop variables
candid=0
iedict = {
    'per_page':'100'
    ,'api_key':config.api_key
    ,'two_year_transaction_period':cycle
    ,'last_index':[]
    ,'last_expenditure_date':[]
    ,'candidate_id':cand_ids[candid]
}
edfs = []

#Page through results for each committee id
for x in range(0,len(cand_ids)-1):
    
    #Get first itemized payload for a candidate
    ier = requests.get('https://api.open.fec.gov/v1/schedules/schedule_e/',params=iedict).json()
    
    #Print itemdict to validate
    print(iedict)
    
    #Last page variables
    while ier['pagination']['last_indexes'] is not None:
        
        #Store results of payload
        edf = json_normalize(ier['results'])
        edfs.append(edf)
                
        #Assign last_index and date values, update itemdict
        last_index=ier['pagination']['last_indexes']['last_index']
        last_date=ier['pagination']['last_indexes']['last_expenditure_date']
        #Update dictionary with new indices
        iedict.update([('last_index',last_index)
                        ,('last_expenditure_date',last_date)])

        #Get next payload with updated dict
        ier = requests.get('https://api.open.fec.gov/v1/schedules/schedule_e/',params=iedict).json()
    
    candid+=1
    
    #Update dictionary with next candidate in list and reset last indices
    iedict.update([('candidate_id',cand_ids[candid])
                    ,('last_index',[])
                    ,('last_expenditure_date',[])])

edf=pd.concat(edfs,sort=False,ignore_index=True)
edf=edf.drop_duplicates(subset='transaction_id')

#Clean up ZIP codes
edf['committee.zip'] = edf['committee.zip'].str[:5]

#Write out files to data.world

results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM senate_independent_expenditures')
if len(results.dataframe) > len(edf):
    with dw.open_remote_file('darrenfishell/2020-election-repo','senate-independent-expenditures.csv') as w:
        edf.to_csv(w,index=False)


# In[24]:


## COORDINATED POLITICAL SPENDING RETRIEVAL ## 
#Declare loop variables
candid=0
i=1
pdict = {
    'per_page':'100'
    ,'api_key':config.api_key
    ,'two_year_transaction_period':cycle
    ,'page':i
    ,'candidate_id':cand_ids[candid]
}
pdfs = []

#Page through results for each committee id
for x in range(0,len(cand_ids)-1):
    
    #Get first itemized payload for a candidate
    p_r = requests.get('https://api.open.fec.gov/v1/schedules/schedule_f/',params=pdict).json()
    
    #Print itemdict to validate
    print(pdict)
    
    #Last page variables
    while p_r['pagination']['page']<=p_r['pagination']['pages']:
        
        #Store results of payload
        pdf = json_normalize(p_r['results'])
        pdfs.append(pdf)
                
        #Increment and update page
        i+=1
        pdict.update([('page',i)])

        #Get next payload with updated dict
        p_r = requests.get('https://api.open.fec.gov/v1/schedules/schedule_f/',params=pdict).json()
    
    candid+=1
    
    #Update dictionary with next candidate in list and reset last indices
    pdict.update([('candidate_id',cand_ids[candid])
                    ,('page',1)])

pdf=pd.concat(pdfs,sort=False,ignore_index=True)
pdf=pdf.drop_duplicates(subset='transaction_id')
pdf['committee.zip'] = pdf['committee.zip'].str[:5]

#Write out file to data.world
results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM senate_party_coordinated_expenditures')

if len(results.dataframe) > len(itemdf):
    with dw.open_remote_file('darrenfishell/2020-election-repo','senate-party-coordinated-expenditures.csv') as w:
        pdf.to_csv(w,index=False)

