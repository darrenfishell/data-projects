import pandas as pd
import numpy as np

df = pd.read_csv('/Volumes/Photos & Storage/Big Data Store/arcos_all.tsv.gz', delimiter='\t'
                ,compression='gzip', header=0, sep=' ', quotechar='"'
                ,encoding='utf-8', error_bad_lines=False)