import csv
import os
import shutil
from pathlib import Path
from shutil import copy
from os.path import splitext
import pandas as pd
from tqdm import tqdm
from CERMINE.cermine_parse_xml import extract_cermine_metadata, parse_para_cermine, parse_sec_cermine, parse_ref_cermine
from GROBID.evaluate import compute_sim_matrix, process_tokens, compute_results
from GROBID.grobid_fulltext_extr import create_gt_df, get_gt_metadata
from PdfAct.pdfact_extract import crop_pdf
from Refextract.refextract_extract import sort_files
from Tabula_Camelot.genrateGT import load_data

def create_gt_df_nonsubset(dir, label):
    PDFlist=load_data(dir)
    IDs=[]
    values=[]
    pageno=[]
    for pdf in PDFlist:
        gt_df=get_gt_metadata(pdf, '',label, False)
        if isinstance(gt_df, type(None)):
            continue
        data_str = gt_df['token'].astype(str).str.cat(sep=' ')
        values.append(data_str)
        id=os.path.splitext(pdf.pdf_name)[0]
        IDs.append(id)
        pageno.append(pdf.page_number)
    gt= label + '_gt'
    data_gt_df=pd.DataFrame({'ID':IDs, gt:values, 'page':pageno})
    return data_gt_df


def sort_label_files(dir, label):
    PDFlist = load_data(dir)
    p = Path(dir + "/sorted_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
        get_gt_metadata(PDF, p,label, True)
    return str(p)

def main():
    paradir = sort_files("/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/Docbank_sample", 'reference')
    #paradir="/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/pdf/para_pdf"
    #extract_cermine_metadata(paradir)

    resultdf = parse_ref_cermine(paradir)

    gtdf=create_gt_df_nonsubset(paradir, 'reference')

    final_df = pd.merge(resultdf.astype(str), gtdf.astype(str), on='ID')

    resultdata=[]
    for i in tqdm(range(len(final_df))):
        df=final_df.iloc[i, 1:3].to_frame().transpose()
        f1, pre, recall, lavsim = compute_results(df, 'reference')
        #resultdata.append(['CERMINE', final_df.iloc[i, 0].rpartition("_subset")[0] + ".pdf", final_df.iloc[i, 3], 'reference', pre, recall, f1, lavsim])
        resultdata.append(
            ['CERMINE', final_df.iloc[i, 0] + ".pdf", final_df.iloc[i, 3], 'reference', pre,
             recall, f1, lavsim])


    resultdf = pd.DataFrame(resultdata, columns=['Tool', 'ID', 'Page', 'Label', 'Precision','Recall' ,'F1', 'SpatialDist'])
    filename = 'cermine_extract_ref.csv'
    outputf = '/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Results/' + filename
    resultdf.to_csv(outputf, index=False)
    #shutil.rmtree(paradir)


if __name__ == "__main__":
    main()
