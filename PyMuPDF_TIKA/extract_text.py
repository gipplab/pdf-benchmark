import os
import shutil
from pathlib import Path
from shutil import copy
from xml.dom.minidom import parseString
import pandas as pd
import tika
from bs4 import BeautifulSoup
from dicttoxml import dicttoxml
from tika import parser
from tqdm import tqdm

from PdfAct.pdfact_extract import process_tokens, crop_pdf
from GROBID.evaluate import  compute_results
from Tabula_Camelot.genrateGT import load_data
import fitz


def get_gt_meta(PDFObj, label,p, retflag):
    """
    Function has two purpose controlled by retflag parameter.
    1. retflag==True : find the GT files in DocBank containing metadata labels and copy them into seperate directory in tree called "metadata_pdfs"
    2. retflag==False: return the repective(title, abstract, author) metadata dataframes
    :param PDF: PDF Object
    :param retflag: flag to control the role of the function.
    :return: Extracted ground truth metadata dataframes - title, abstract, author.
    """
    txt_data = PDFObj.txt_data
    frame_labled = txt_data.loc[(txt_data['label'] == label) & (txt_data['token'] != "##LTLine##")]
    if len(frame_labled) != 0:
        if retflag == True:
            filename = PDFObj.filepath + os.sep + PDFObj.pdf_name
            txtname = PDFObj.filepath + os.sep + PDFObj.txt_name
            copy(filename, p)
            copy(txtname, p)
            return
        else:
            return frame_labled

def sort_metadata(dir, label):
    PDFlist = load_data(dir)
    dirname='metadata' + '_' + label
    p = Path(dir +  os.sep + dirname)
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
       get_gt_meta(PDF, label ,p, True)
    return str(p)


def parse_author(file):
    handler = open(file).read()
    soup = BeautifulSoup(handler, features="lxml")
    authors_in_header = soup.find_all('Author')
    title=soup.find_all('title')
    if len(title) == 0:
        title=None
    else:
        title=title[0].string
    return authors_in_header, title

def parse_tika_file(outputfile):
    authorlist, title= parse_author(outputfile)
    return authorlist, title

def extract_tika_metadata(metadir, label):
    metaPDFlist=load_data(metadir)
    for PDF in tqdm(metaPDFlist):
        filep=PDF.filepath + os.sep + PDF.pdf_name
        tika.initVM()
        if label == 'metadata':
            parsed = parser.from_file(filep)
            xml = dicttoxml(parsed[label], custom_root='PDF', attr_type=False)
            dom = parseString(xml)
            outfile = os.path.splitext(os.path.basename(PDF.pdf_name))[0]  + '_tika' + '.xml'
            outfilecsv = os.path.splitext(os.path.basename(PDF.pdf_name))[0] + '_tika' + '.csv'
            outputf = PDF.filepath + os.sep + outfile
            with open(outputf, 'w') as result_file:
                result_file.write(dom.toprettyxml())
            authorlist, title=parse_tika_file(outputf)

            if len(authorlist) == 0 and title == None:
                print ('cannot parse the metadata')
            else:
                record=title + ',' + ' '.join(authorlist)
                with open(outfilecsv, 'w') as res:
                    res.write(record)
        if label == 'paragraph':
            croppedfile = crop_pdf(PDF.filepath, PDF.pdf_name, PDF.page_number)

            if isinstance(croppedfile, type(None)):
                continue
            parsed = parser.from_file(croppedfile)

            # PyMuPDF_TIKA Text extraction
            doc = fitz.open(croppedfile)
            page = doc.loadPage(0)
            text = page.getText("text")

            os.remove(croppedfile)

            outfile = os.path.splitext(os.path.basename(PDF.pdf_name))[0]  +  '_tika' + '.txt'
            outfile1 = os.path.splitext(os.path.basename(PDF.pdf_name))[0] + '_pymupdf' + '.txt'

            outputf = PDF.filepath + os.sep + outfile
            outputf1 = PDF.filepath + os.sep + outfile1

            if isinstance(parsed["content"], type(None)):
                continue
            with open(outputf , 'w') as result_file:
                result_file.write(parsed["content"])
            with open(outputf1 , 'w') as result_file1:
                result_file1.write(text)
    return

def main():
    dir_array = ['docbank_1601', 'docbank_1602', 'docbank_1603', 'docbank_1604', 'docbank_1605', 'docbank_1606',
                   'docbank_1607', 'docbank_1608', 'docbank_1609','docbank_1610', 'docbank_1611', 'docbank_1612',
                   'docbank_1701', 'docbank_1702', 'docbank_1703', 'docbank_1704', 'docbank_1705', 'docbank_1706',
                   'docbank_1707', 'docbank_1708', 'docbank_1709', 'docbank_1710', 'docbank_1711', 'docbank_1712']
    for dir in dir_array:
        metadir = sort_metadata("/data/docbank/" + dir, "paragraph")
        extract_tika_metadata(metadir, 'paragraph')
        #resultdf.to_csv('tika_extract_para_1401.csv', index=False)

if __name__ == "__main__":
    main()