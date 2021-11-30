import os
import shutil
from pathlib import Path
from shutil import copy
from os.path import splitext

import pandas as pd
from tqdm import tqdm

from PdfAct.pdfact_extract import crop_pdf, compute_metrics
from GROBID.grobid_metadata_extract import grobid_extract
from GROBID.grobid_parse_xml import parse_extracted_references
from Tabula_Camelot.genrateGT import load_data


def get_gt_metadata(PDFObj, p, label, retflag):
    txt_data = PDFObj.txt_data
    gt_frame_labled = txt_data.loc[(txt_data['label'] == label)]
    if len(gt_frame_labled) != 0:
        if retflag == True:
            croppedfile = crop_pdf(PDFObj.filepath, PDFObj.pdf_name, PDFObj.page_number)
            if isinstance(croppedfile, type(None)):
                return
            realfile= str(p) + os.sep + PDFObj.pdf_name
            txtname = PDFObj.filepath + os.sep + PDFObj.txt_name
            os.replace(croppedfile, realfile)
            copy(txtname, p)
            return
        else:
            return gt_frame_labled

def sort_label_files(dir, label):
    PDFlist = load_data(dir)

    p = Path(dir + "/label_pdfs/")

    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
        get_gt_metadata(PDF, p,label, True)
    return str(p)

def delete_empty_tei(dir):
    papers = sorted(Path(dir).glob('*.tei.xml'))
    for tei in papers:
        if os.path.getsize(tei) == 0:
            os.remove(tei)

def main():
    dir_array = ['docbank_1709', 'docbank_1710', 'docbank_1711', 'docbank_1712', 'docbank_1801', 'docbank_1802', 'docbank_1803', 'docbank_1804']
    for dir in dir_array:
        dirp="/data/docbank/" + dir
        refdir = sort_label_files(dirp, "reference")

        # Run GROBID Metadata Extraction
        grobid_extract(refdir, 'processReferences')

        #Delete the empty result files
        delete_empty_tei(refdir)

        # Parse TEI XML file from GROBID
        resultdf = parse_extracted_references(refdir)

        if resultdf.empty:
            print("0,0")
        # Correlate gt to extracted references
        PDFlist = load_data(refdir)
        resultdata=[]
        for pdf in tqdm(PDFlist):
            resultkey, ext = splitext(pdf.pdf_name)
            filtered_df = resultdf[resultdf.ID.eq(resultkey)]
            outputfile = pdf.filepath + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0] + "_extracted_reference.txt"
            ex_data=filtered_df[['refstring']]
            ex_data.to_csv(outputfile, index=False, header=False)
            if isinstance(outputfile, type(None)):
                continue
            if os.path.getsize(outputfile) == 0:
                resultdata.append(['GROBID', pdf.pdf_name, pdf.page_number, 'reference', 0, 0, 0, 0])
            else:
                f1, pre, recall, lavsim = compute_metrics(pdf, outputfile, 'reference')
                resultdata.append(['GROBID', pdf.pdf_name, pdf.page_number, 'reference', pre, recall, f1, lavsim])

        resultdf = pd.DataFrame(resultdata,
                                columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])
        key = dir.split('_')[1]
        filename = 'grobid_extract_ref_' + key + '.csv'
        outputf = '/data/results/grobid/' + filename
        resultdf.to_csv(outputf, index=False)

if __name__ == "__main__":
    main()
