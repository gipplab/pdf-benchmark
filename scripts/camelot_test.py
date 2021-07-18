import camelot
import matplotlib
import pandas as pd


#tables=camelot.read_pdf('/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/boundingboxtest/pdf/94.tar_1506.05555.gz_NNSHMC_SC_3rdRevision_black.pdf', flavor='stream',pages='16')
from pandas import DataFrame

tables = camelot.read_pdf('/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/Data/pdf/75.tar_1505.04211.gz_discoPoly_black.pdf', table_regions=['143,696,166,665'], flavor='stream', pages='13')

W, C=[], []
for x, y in zip(tables[-1].df.__array__().tolist(), tables[-1].cells):
    for word, loc in zip(x, y):
        W.append(word)
        C.append(loc)

df = DataFrame()
df['word'] = W
df['loc'] = C

def make_coordinate_list(cellvar):
    cellvar=str(cellvar)
    list=cellvar.split(' ')
    x1=list[1].split('=')[1]
    y1=list[2].split('=')[1]
    x2=list[3].split('=')[1]
    y2=list[4].split('=')[1]
    y2=y2[:-1]
    colist=[float(x1),float(y1),float(x2),float(y2)]
    return colist

df['loc']=df['loc'].apply(make_coordinate_list)
df1=df['word']
df=pd.DataFrame(df['loc'].values.tolist())
df2=pd.concat([df1,df], axis=1)


# table_areas=['316,499,566,337']
# co-ordinates End : 781	588	806	602
# co-ordinates Start : 223	385	291	398
# final : x1: 781 y1: 588 x2: 291 y2: 398

# table_regions=['85,771,280,665']

# Source pdfprocess.py
# 350.6926784	480.8714	353.1947784	489.8714
# 531.5139821	349.6579	536.5180821	358.6579
# Result : table_areas=['350,489,536,349']

# 275.46155	665.7660784	280.44284999999996	675.7286784
# 85.8302346 761.8060783999999	88.5998374	771.7686784
# [85,771, 280, 665]

# <word xMin="58.722000" yMin="71.177357" xMax="88.599837" yMax="80.083922">Dataset</word>
#  <word xMin="258.027000" yMin="167.217357" xMax="280.442850" yMax="176.123922">1,224</word>
# ['58,176,280,71']

# 85.8302346	761.8060783999999	88.5998374	771.7686784
# 275.46155	665.7660784	280.44284999999996	675.7286784
# 85,771,280,665
# 85.8302346	761.8060783999999	88.5998374	771.7686784
# 275.46155	665.7660784	280.44284999999996	675.7286784

# Source pdftotext tool
#<word xMin="323.179700" yMin="302.551600" xMax="353.194700" yMax="311.128600">Payroll</word>
#<word xMin="514.000004" yMin="433.396100" xMax="536.518004" yMax="442.342100">14.23</word>
# Result : table_areas=['323,442,536,302']

#143.97239015	685.6116346	148.24548461999998	696.5207346
#162.45924067	665.5188006000001	166.92887275	673.4889006000001

#print(len(tables))
#camelot.plot(tables[0], kind='grid').show()
#print(tables[-1]._bbox)
tables[0].to_csv('test.csv')
