import csv
import os.path
import shutil
from glob import glob
from os import path

import pandas as pd
pd.options.mode.chained_assignment = None


class PDF:
    def __init__(self, page_number=None, pdf_name=None, filepath=None, txt_name=None, txt_data=None):
        self.page_number = page_number
        self.pdf_name = pdf_name
        self.filepath=filepath
        self.txt_name=txt_name
        self.txt_data=txt_data

def locate_data(dir):
    """
    Function to find Text their respective PDF files from DocBank dataset.
    :param dir: Base directory
    :return: list of text and pdf files.
    """
    pdffiles=glob(path.join(dir,"*.{}".format('pdf')))
    txtfiles=glob(path.join(dir,"*.{}".format('txt')))
    return pdffiles, txtfiles

def load_data(dir):
    """
    Function creates the PDF objects for the gives base directory of DocBank dataset.
    :param dir: Base location of DocBank dataset.
    :return: List of PDF Objects.
    """
    pdff,txtf = locate_data(dir)
    PDFlist=[]

    for txt in txtf:
        nwe=os.path.splitext(os.path.basename(txt))[0] # 2.tar_1801.00617.gz_idempotents_arxiv_4.txt --> 2.tar_1801.00617.gz_idempotents_arxiv_4
        keyword=nwe.rpartition('_')[0] # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 2.tar_1801.00617.gz_idempotents_arxiv
        page_number=nwe.split('_')[-1]  # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 4
        pdfn = dir + "/" +keyword + "_black.pdf"
        if os.path.isfile(pdfn):
            pdf_name=os.path.basename(pdfn)
            txt_name=os.path.basename(txt)
            txtdf=pd.read_csv(txt,sep='\t',quoting=csv.QUOTE_NONE,encoding='latin1',usecols=[0,1,2,3,4,9], names=["token", "x0", "y0", "x1", "y1","label"])
            PDFlist.append(PDF(page_number,pdf_name,dir,txt_name,txtdf))
    return PDFlist

def get_gt_table(PDF):
    """
    Function extracts the table component from the DocBank annotated data.
    :param PDF: PDF Object
    :return: Extracted table component.
    """
    txt_data = PDF.txt_data
    table_frame_labled = txt_data.loc[(txt_data['label'] == 'table') & (txt_data['token'] != '##LTLine##')]
    if len(table_frame_labled) == 0:
        return table_frame_labled  # No table present on the page.
    else:  # If table is present
        return table_frame_labled


def merge_multiple_files(files, outputfile):
    with open(outputfile, 'wb') as wfd:
        for f in files:
            with open(f, 'rb') as fd:
                shutil.copyfileobj(fd, wfd)
    return outputfile
def format_tablecells_dfs(table_df,PDF,deleteflag):
    """
    Function for creating a Uniform format of extracted data. Splitting each table cell/word per line.
    :param table_df: Extracted table dataframe
    :param PDF: PDF object
    :param deleteflag: Flag to delete the intermediate files
    :return: dataframe with one column containing single word per row.
    """

    if (len(table_df) == 1):
        tablef = PDF.pdf_name.replace('.pdf', '') + '_{}_extract.csv'.format(str(PDF.page_number))
        table_df[0].to_csv(tablef, sep='\n', index=False, quoting=csv.QUOTE_ALL, header=False)

        table_extracted = pd.read_csv(tablef, sep=',', names=["token"], dtype={"token" : str})

        table_extracted = table_extracted.astype(str).applymap(str.split).apply(pd.Series.explode, axis=0).reset_index().drop("index",1)  # To create one word per row.

        if deleteflag:
            os.remove(tablef)

        return table_extracted
    else:
        fapp = []
        for i in range(len(table_df)):
            tablef = PDF.pdf_name.replace('.pdf', '') + '_{}_{}_extract.csv'.format(str(PDF.page_number), i)
            table_df[i].to_csv(tablef, sep='\n', index=False, header=False)
            fapp.append(tablef)
        #df = pd.concat([pd.read_csv(f) for f in fapp], ignore_index=True)
        tablef = PDF.pdf_name.replace('.pdf', '') + '_{}_extract.csv'.format(str(PDF.page_number))
        tablef = merge_multiple_files(fapp, tablef)
        #df.to_csv(tablef, sep='\n', index=False)

        for f in fapp:
            os.remove(f)

        table_extracted = pd.read_csv(tablef, sep=',', names=["token"])
        table_extracted = table_extracted.astype(str).applymap(str.split).apply(pd.Series.explode, axis=0).reset_index().drop("index",1)  # To create one word per row.

        if deleteflag:
            os.remove(tablef)
            #os.remove(tablegt)

        return table_extracted

