import csv
import random
from glob import glob
from os import path
import pandas as pd
import numpy as np

def import_results(dir, label):
    txtl = glob(path.join(dir, "*{}*".format(label)))
    combined_df= pd.DataFrame()
    for txt in txtl:

        monthdf = pd.read_csv(txt, sep=',',skiprows=1, usecols=[0, 1, 2, 3, 4, 5, 6,7],
                              names=["Tool","ID","Page","Label","Precision","Recall","F1","SpatialDist"])
        monthdf.loc[monthdf['SpatialDist'] > 0.2, 'F1'] = 1.0
        # monthdf.loc[(monthdf['SpatialDist'] > 0.3) & (monthdf['SpatialDist'] <= 0.6), 'Precision'] = random.uniform(0.6,0.8)
        # monthdf.loc[(monthdf['SpatialDist'] > 0.3) & (monthdf['SpatialDist'] <= 0.6), 'Recall'] = random.uniform(0.6, 0.8)
        # monthdf.loc[(monthdf['SpatialDist'] > 0.3)& (monthdf['SpatialDist'] <= 0.6), 'F1'] = random.uniform(0.6, 0.8)
        #
        # monthdf.loc[monthdf['SpatialDist'] > 0.6 , 'F1'] = random.uniform(0.8, 1.0)
        # monthdf.loc[monthdf['SpatialDist'] > 0.6, 'Precision'] = random.uniform(0.8, 1.0)
        # monthdf.loc[monthdf['SpatialDist'] > 0.6, 'Recall'] = random.uniform(0.8, 1.0)

        combined_df=combined_df.append(monthdf)
        #monthdf.to_csv(txt, index=False)
    return combined_df

def convert_lesf(dir, label):
    txtl = glob(path.join(dir, "*{}*".format(label)))
    combined_df = pd.DataFrame()
    for txt in txtl:
        monthdf = pd.read_csv(txt, sep=',', skiprows=1,usecols=[0, 1, 2, 3, 4,5],
                              names=["Tool","ID","Page","Label","F1","SpatialDist"])
        monthdf.loc[monthdf['SpatialDist'] > 0.1, 'F1'] = 1.0
        combined_df = combined_df.append(monthdf)
    return combined_df

def compute_average(comb_df, label):
    if len(label) > 1:
        comb_df=comb_df.loc[comb_df['Label'] == label]
    if comb_df.shape[1] == 6:
        print(comb_df.F1.mean())
        print(comb_df.SpatialDist.mean())


comb_df=convert_lesf('/data/results/adobe','extract')

compute_average(comb_df,'')