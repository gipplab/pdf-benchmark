import pandas as pd
from scipy.spatial.distance import cdist
from Levenshtein import ratio
pd.options.mode.chained_assignment = None

datafe=pd.read_csv('/CERMINE/extracted.csv', sep=',', index_col=0)
datafg=pd.read_csv('/CERMINE/groundtruth.csv', sep=',', index_col=0)

#ex_nump = datafe['author_ex'].to_numpy()
#gt_nump = datafg['author_gt'].to_numpy()

#matrix = cdist(ex_nump.reshape(-1, 1), gt_nump.reshape(-1, 1), lambda x, y: ratio(x[0], y[0]))
#df = pd.DataFrame(data=matrix, index=ex_nump, columns=gt_nump)


def remove_hyp(df):
    # create new column 'Ending' for True/False if column 'author_ex' ends with '-'
    df['Ending'] = df['author_ex'].shift(1).str.contains('-$', na=False, regex=True)
    # remove the trailing '-' from the 'author_ex' column
    df['author_ex'] = df['author_ex'].str.replace('-$', '', regex=True)
    # create new column with values of 'author_ex' and shifted 'author_ex' concatenated together
    df['author_ex_combined'] = df['author_ex'] + df.shift(-1)['author_ex']
    # create a series true/false but shifted up
    index = (df['Ending'] == True).shift(-1)
    # set the last row to 'False' after it was shifted
    index.iloc[-1] = False
    # replace 'author_ex' with 'author_ex_combined' based on true/false of index series
    df.loc[index, 'author_ex'] = df['author_ex_combined']
    # remove rows that have the 2nd part of the 'author_ex' string and are no longer required
    df = df[~df.Ending]
    # remove the extra columns
    df.drop(['Ending', 'author_ex_combined'], axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

datafe=remove_hyp(datafe)
print(datafe)
