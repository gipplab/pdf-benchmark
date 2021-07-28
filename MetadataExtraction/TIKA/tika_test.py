import pandas as pd
import tika
from tika import parser
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup

def parse_author(file):
    handler = open(file).read()
    soup = BeautifulSoup(handler, features="lxml")
    authors_in_header = soup.find_all('contrib')
    title=soup.find_all('article-title')[0].string
    abs=soup.find_all('abstract')[0].text.strip()
    aulist=[]
    for author in authors_in_header:
        au=author.find("string-name")
        aulist.append(au.text)

    return aulist, title, abs


tika.initVM()
parsed=parser.from_file('/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/Data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf')
xml = dicttoxml(parsed['metadata'], custom_root='PDF', attr_type=False)
dom = parseString(xml)
print(dom.toprettyxml())
#xml = dicttoxml(parsed, custom_root='PDF', attr_type=False)
# dom = parseString(xml)
# with open('result.xml', 'w') as result_file:
#     result_file.write(dom.toprettyxml())

# print()



#pd.DataFrame()

#print(parsed["content"])

