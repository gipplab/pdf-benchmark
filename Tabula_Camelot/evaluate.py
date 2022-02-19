import csv
import os
from pathlib import Path
from shutil import copy

import pandas as pd
from similarity.damerau import Damerau
from similarity.jaccard import Jaccard
from similarity.jarowinkler import JaroWinkler
from similarity.normalized_levenshtein import NormalizedLevenshtein
from similarity.qgram import QGram
from tqdm import tqdm
from GROBID.evaluate import compute_sim_matrix, compute_results
from GROBID.grobid_fulltext_extr import create_gt_df
from GROBID.grobid_metadata_extract import locate_data
from PdfAct.pdfact_extract import crop_pdf
from Tabula_Camelot.tabula_camelot_extract import tabula_extract_table, camelot_extract_table
from Tabula_Camelot.table_area_heuristics import get_table_coordinates
from Tabula_Camelot.genrateGT import format_tablecells_dfs, get_gt_table, load_data, PDF


def load_data_subset(dir):
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
        pdfn = dir + "/" +keyword + "_black_subset_" + str(page_number) +".pdf"
        if os.path.isfile(pdfn):
            pdf_name=os.path.basename(pdfn)
            txt_name=os.path.basename(txt)
            txtdf=pd.read_csv(txt,sep='\t',quoting=csv.QUOTE_NONE,encoding='latin1',usecols=[0,1,2,3,4,9], names=["token", "x0", "y0", "x1", "y1","label"])
            PDFlist.append(PDF(page_number,pdf_name,dir,txt_name,txtdf))
    return PDFlist

def calculate_metrics(table_df):
    #table_extracted = format_tablecells_dfs(table_df, PDF, True)
    #similarity_score = calc_similarity(table_extracted.drop_duplicates(), table_gt[["token"]])
    #f1, prec, recal = eval_metrics(similarity_score, len(table_gt.index), len(table_extracted.drop_duplicates()))
    tabs=[]
    for tables in table_df:
        if hasattr(tables, 'T'):
            extractedtab = ' '.join(list(map(' '.join, tables.T.astype(str).values.tolist())))
        else:
            extractedtab = ' '.join(list(map(' '.join, tables.df.T.astype(str).values.tolist())))
        tabs.append(extractedtab)
    #data_gt = table_gt['token'].astype(str).str.cat(sep=' ')
    data_ex = ' '.join(tabs)
    return  data_ex

def get_gt_crop(PDFObj, p, retflag, label):
    txt_data = PDFObj.txt_data
    gt_frame_labled = txt_data.loc[(txt_data['label'] == label) & (txt_data['token'] != "##LTLine##")]
    if len(gt_frame_labled) != 0:
        if retflag == True:
            croppedfile = crop_pdf(PDFObj.filepath, PDFObj.pdf_name, PDFObj.page_number)
            if isinstance(croppedfile, type(None)):
                return
            #realfile= str(p) + os.sep + PDFObj.pdf_name
            txtname = PDFObj.filepath + os.sep + PDFObj.txt_name
            copy(croppedfile, p)
            #os.replace(croppedfile, realfile)
            copy(txtname, p)
            return
        else:
            return gt_frame_labled

def compute_smmatrix(dataf):
    resultdata=[]
    df_extractednp = dataf['table_ex'].to_numpy()
    df_groundtruthnp = dataf['table_gt'].to_numpy()
    matrix = compute_sim_matrix(df_extractednp, df_groundtruthnp)
    for index, row in dataf.iterrows():
        resultdata.append(['GROBID', row['ID'], row['page'], 'table', 0, 0, 0, matrix.iloc[index,index]])
    return resultdata

def sort_files(dir, label):
    PDFlist = load_data(dir)
    p = Path(dir + "/sort_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
        ## Here can go either of below 2 methods
       get_gt_crop(PDF,  p, True, label)
    return str(p)

def rotate(PDFlist, cor_flag):
    resultdata=[]
    if not cor_flag:
        for PDF in tqdm(PDFlist):
            camelottable_df = camelot_extract_table(PDF.pdf_name,PDF.filepath)
            if isinstance(camelottable_df, type(None)):
                continue
            data_ex=calculate_metrics(camelottable_df)
            id=os.path.splitext(PDF.pdf_name)[0]
            resultdata.append([id, data_ex])
        resultdf = pd.DataFrame(resultdata,columns=['ID', 'table_ex'])
        return resultdf
    if cor_flag:
        for PDF in tqdm(PDFlist):
            table_gt = get_gt_crop(PDF, '', False, 'table')
            tab_coordinates = get_table_coordinates(PDF, table_gt)
            if tab_coordinates[0] != 0:
                camelottable_df = camelot_extract_table(PDF.pdf_name, PDF.filepath, tab_coordinates)

            if isinstance(camelottable_df, type(None)):
                continue

            data_ex=calculate_metrics(camelottable_df)
            id=os.path.splitext(PDF.pdf_name)[0]
            resultdata.append([id, data_ex])
        resultdf = pd.DataFrame(resultdata,columns=['ID', 'table_ex'])
        return resultdf


def main():
        dirp = '/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/pdf'
        tabdir = sort_files(dirp, "table")
        PDFlist=load_data_subset(tabdir)
        ex_df=rotate(PDFlist, True)
        groundtdf = create_gt_df(tabdir, 'table')
        final_df = pd.merge(ex_df, groundtdf, on='ID')

        resultdata = []
        for i in tqdm(range(len(final_df))):
            df = final_df.iloc[i, 1:3].to_frame().transpose()
            f1, pre, recall, lavsim = compute_results(df, 'table')

            resultdata.append(
                ['CAMELOT', final_df.iloc[i, 0] + ".pdf", final_df.iloc[i, 3], 'table', pre,
                 recall, f1, lavsim])


        resultdf = pd.DataFrame(resultdata,
                                columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])

        filename = 'tabula_extract_tab_1_wcor.csv'
        outputf = '/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Tabula_Camelot/' + filename
        resultdf.to_csv(outputf, index=False)

if __name__ == "__main__":
    main()
