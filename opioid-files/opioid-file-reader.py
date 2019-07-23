import pandas as pd
import numpy as np
import os
cwd=os.getcwd()

df = pd.read_csv('arcos-me-statewide-itemized.tsv', delimiter='\t', low_memory=False)

df.head()

townfix = {
    'lisbon falls':'lisbon'
    ,'bridgeton':'bridgton'
    ,'cumberland center':'cumberland'
    ,'grey':'gray'
    ,'north windham':'windham'
    ,'steep falls':'standish'
    ,'seal harbor':'mount desert'
    ,'east boothbay':'boothbay'
    ,'no. vassalboro':'vassalboro'
    ,'south paris':'paris'
    ,'east waterboro':'waterboro'
    ,'hollis center':'hollis'
    ,'springvale':'sanford'
}

df['lower_city'] = df['BUYER_CITY'].lower()

df.lower(BUYER_CITY).replace(townfix,value=None,inplace=True)

df.to_csv(cwd+'/arcos-me-statewide-cleaned-towns.csv')