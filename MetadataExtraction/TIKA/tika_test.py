import pandas as pd
import tika
from tika import parser
tika.initVM()
parsed = parser.from_file('/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/Data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf')
print(parsed["metadata"])
pd.DataFrame()

#print(parsed["content"])

