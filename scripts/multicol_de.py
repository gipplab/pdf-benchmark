import pdfplumber
import re
from glob import glob
from os import path
from pathlib import Path
from tqdm import tqdm
import shutil

laparams = {
    'line_overlap': 0.5,
    'char_margin': 2.0,
    'line_margin': 0.5,
    'word_margin': 0.1,
    'boxes_flow': 0.5,
    'detect_vertical': False,
    'all_texts': False
}

def multicol_detect(pdf, pdf_pp, p1,p2):
    no_of_pages=len(pdf_pp.pages)
    docspace=0
    for i in range(no_of_pages):
        page=pdf_pp.pages[i]
        text=page.extract_text(x_tolerance=7)
        spaces = re.findall(r'[^\S\n\t]+', text)
        docspace=docspace + len(spaces)

    avgdocspace=docspace/no_of_pages

    # Filter the documents
    if avgdocspace > 55 and no_of_pages <= 9:
        shutil.move(pdf,p1)
    elif avgdocspace >= (no_of_pages*2):
        shutil.move(pdf,p1)
    else:
        shutil.move(pdf,p2)


def find_pdf(dr):
    return glob(path.join(dr,"*.{}".format('pdf')))

def main_call(dir):
    pdfs = find_pdf(dir)

    if len(pdfs) == 0:
        print('No PDFs found under ' + dir )
    else:
        p1 = Path(dir + "/output_multicol/")
        p2 = Path(dir + "/output_singlecol/")
        p1.mkdir(parents=True, exist_ok=True)
        p2.mkdir(parents=True, exist_ok=True)
        for pdf in tqdm(pdfs):
            pdf_pp = pdfplumber.open(pdf)
            multicol_detect(pdf,pdf_pp,p1,p2)

main_call('//Data')
