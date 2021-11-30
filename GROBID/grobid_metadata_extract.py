import csv
import os
from glob import glob
from os import path
import pandas as pd
from grobid_client.grobid_client import GrobidClient
from tqdm import tqdm
from GROBID.grobid_parse_xml import parse_extracted_metadata
from Tabula_Camelot.genrateGT import PDF

# Subclass of PDF with extra fields of title, authors and abstract.
class PDFMetadata(PDF):
    def __init__(self, page_number, pdf_name, filepath, txt_name, txt_data, title=None, authors=None, abstract=None):
        super().__init__(page_number, pdf_name, filepath, txt_name, txt_data)
        self.title = title
        self.authors = authors
        self.abstract=abstract

def locate_data(dir):
    """
    Function to find Text their respective PDF files from DocBank dataset.
    :param dir: Base directory
    :return: list of text and pdf files.
    """
    pdffiles=glob(path.join(dir,"*.{}".format('pdf')))
    txtfiles=glob(path.join(dir,"*.{}".format('txt')))
    return pdffiles, txtfiles

def create_pdfmetadata_obj(dir, resultdf):
    """
    Function creates the PDF objects for the gives base directory of DocBank dataset.
    :param dir: Base location of DocBank dataset.
    :return: List of PDF Objects.
    """
    pdff,txtf = locate_data(dir)
    MetaObjlist=[]

    for txt in tqdm(txtf):
        nwe=os.path.splitext(os.path.basename(txt))[0] # 2.tar_1801.00617.gz_idempotents_arxiv_4.txt --> 2.tar_1801.00617.gz_idempotents_arxiv_4
        keyword=nwe.rpartition('_')[0] # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 2.tar_1801.00617.gz_idempotents_arxiv
        page_number=nwe.split('_')[-1]  # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 4
        pdfn = dir + "/" +keyword + "_black.pdf"
        if os.path.isfile(pdfn):
            pdf_name=os.path.basename(pdfn)
            txt_name=os.path.basename(txt)
            txtdf=pd.read_csv(txt,sep='\t',quoting=csv.QUOTE_NONE, encoding='latin1',usecols=[0,1,2,3,4,9], names=["token", "x0", "y0", "x1", "y1","label"])

            filter=os.path.splitext(os.path.basename(pdf_name))[0]
            reser=resultdf.loc[resultdf['ID'] == filter]
            title=reser['Title']
            abstract=reser['Abstract']
            authors=reser['Authors']
            MetaObjlist.append(PDFMetadata(page_number,pdf_name,dir,txt_name,txtdf, title, authors, abstract))
    return MetaObjlist


def parse_metadata(dir):
    resultdf = parse_extracted_metadata(dir)
    return resultdf


def grobid_extract(dir, extract_param):
    client = GrobidClient(config_path="config.json")
    client.process(extract_param, dir, n=100)

