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

def extract_tika_metadata(metadir, label, dirkey):
    metaPDFlist=load_data(metadir)
    resultdata=[]
    for PDF in tqdm(metaPDFlist):
        filep=PDF.filepath + os.sep + PDF.pdf_name
        tika.initVM()
        if label == 'metadata':
            parsed = parser.from_file(filep)
            xml = dicttoxml(parsed[label], custom_root='PDF', attr_type=False)
            dom = parseString(xml)
            outfile = os.path.splitext(os.path.basename(PDF.pdf_name))[0]  + '_tika' + '.xml'
            outputf = PDF.filepath + os.sep + outfile
            with open(outputf, 'w') as result_file:
                result_file.write(dom.toprettyxml())
            authorlist, title=parse_tika_file(outputf)
            title_gt_df=get_gt_meta(PDF, 'title', PDF.filepath, False)
            author_gt_df=get_gt_meta(PDF,'author', PDF.filepath, False)

            if len(authorlist) == 0 and title == None:
                print ('cannot parse the metadata')
            else:
                print(title, authorlist)
                csv_entries=[PDF.pdf_name, title, authorlist]
                result_csv = pd.DataFrame(csv_entries, columns=['ID', 'Title', 'Authors'])
                print(result_csv)
        if label == 'paragraph':
            croppedfile = crop_pdf(PDF.filepath, PDF.pdf_name, PDF.page_number)
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

            with open(outputf , 'w') as result_file:
                result_file.write(parsed["content"])
            with open(outputf1 , 'w') as result_file1:
                result_file1.write(text)

            para_gt = get_gt_meta(PDF, 'paragraph', PDF.filepath, False)
            final_df = process_tokens(para_gt, outputf, label)
            final_df1 = process_tokens(para_gt, outputf1, label)


            if isinstance(outputf, type(None)):
                continue
            if isinstance(PDF, type(None)):
                continue
            elif not os.path.isfile(outputf):
                continue
            elif os.path.getsize(outputf) == 0:
                resultdata.append(['tika', PDF.pdf_name, PDF.page_number, label,0,0, 0, 0])
                os.remove(outputf)
            else:
                f1, pre, recall, lavsim = compute_results(final_df, label)
                resultdata.append(['Tika', PDF.pdf_name, PDF.page_number, label, pre, recall, f1, lavsim])

            if isinstance(outputf1, type(None)):
                continue
            if isinstance(PDF, type(None)):
                continue
            elif not os.path.isfile(outputf1):
                continue
            elif os.path.getsize(outputf1) == 0:
                resultdata.append(['pymupdf', PDF.pdf_name, PDF.page_number, label, 0, 0, 0, 0])
                os.remove(outputf1)
            else:
                f11, pre1, recall1, lavsim1 = compute_results(final_df1, label)
                resultdata.append(['PyMuPDF', PDF.pdf_name, PDF.page_number, label, pre1, recall1, f11, lavsim1])


    resultdf = pd.DataFrame(resultdata,
                            columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])
    return resultdf

def main():
    dir_array = ['docbank_1401']
    for dir in dir_array:
        metadir = sort_metadata("/data/docbank/" + dir, "paragraph")
        resultdf = extract_tika_metadata(metadir, 'paragraph', dir)
        resultdf.to_csv('tika_extract_para_1401.csv', index=False)

if __name__ == "__main__":
    main()