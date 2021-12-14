from glob import glob
from os import path

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def lengths(x):
    if isinstance(x,list):
        yield len(x)
        for y in x:
            yield from lengths(y)

def import_csv(dir, label, sublabel):
    txtl = glob(path.join(dir, "*{}*".format(label)))
    combined_df = pd.DataFrame()
    header=pd.read_csv(txtl[0], nrows=0).columns.tolist()
    if len(header) == 6:
        for csvfile in txtl:
            monthdf = pd.read_csv(csvfile, sep=',', skiprows=1, usecols=[0, 1, 2, 3, 4, 5],
                                  names=["Tool", "ID", "Page", "Label", "F1", "SpatialDist"])
            combined_df = combined_df.append(monthdf)
    elif len(header) == 8:
        for csvfile in txtl:
            monthdf = pd.read_csv(csvfile, sep=',', skiprows=1, usecols=[0, 1, 2, 3, 4, 5, 6, 7], error_bad_lines=False,
                              names=["Tool", "ID", "Page", "Label", "Precision", "Recall", "F1", "SpatialDist"])
            combined_df = combined_df.append(monthdf)
    if len(sublabel) > 1:
        combined_df = combined_df.loc[combined_df['Label'] == sublabel]
        return combined_df
    else:
        return combined_df

tools_list=['meta']
color_list=['red']
pre_list=[]
rec_list=[]
data=[]
for tool in tools_list:
    data_df=import_csv('/data/results/Pdfact' , tool, '')


    pre_list.append(data_df['Precision'].rolling(1000).mean().tolist())
    rec_list.append(data_df['SpatialDist'].rolling(1000).mean().tolist())

    data.append(data_df['Precision'].tolist())
    data.append(data_df['SpatialDist'].tolist())

x_axis_vals = tuple(list(map(str,list(range(0, max(lengths(data))))))) # X axis values

def compute_xaxis_vals(pre_list):
   return tuple(list(map(str,list(range(0, len(pre_list))))))


for tool in range(0, len(tools_list)):
    #plt.gca().setp(['red'])
    x_ax=compute_xaxis_vals(pre_list[tool])
    x_ax2=compute_xaxis_vals(rec_list[tool])
    plt.plot(x_ax, pre_list[tool], '-', color=color_list[tool], markersize=3)
    plt.plot(x_ax2, rec_list[tool], '-.', color=color_list[tool], markersize=3)


plt.ylabel("Precision & Recall Score")
plt.ylim(0.0,1.0)
plt.xticks(np.arange(0, len(x_axis_vals) +1, 1000), rotation=90, fontsize=7)
#plt.yticks(values  * value_increment, ['%.1f' % val for val in values], fontsize=7)
plt.title('Metadata Extraction')
#plt.savefig('pr.png', dpi=300)
plt.show()
