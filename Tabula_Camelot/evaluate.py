import csv
import os

import pandas as pd
from similarity.damerau import Damerau
from similarity.jaccard import Jaccard
from similarity.jarowinkler import JaroWinkler
from similarity.normalized_levenshtein import NormalizedLevenshtein
from similarity.qgram import QGram
from tqdm import tqdm

from GROBID.grobid_fulltext_extr import sort_label_files, create_gt_df, compute_matrix
from GROBID.grobid_metadata_extract import locate_data
from Tabula_Camelot.tabula_camelot_extract import tabula_extract_table, camelot_extract_table
from Tabula_Camelot.table_area_heuristics import get_table_coordinates
from Tabula_Camelot.genrateGT import format_tablecells_dfs, get_gt_table, load_data, PDF


def calc_similarity(table_extracted, table_groundT):
    """
    Function computes various String Similarity Indexes for Extracted and Ground truth dataframes.
    :param table_extracted: Extracted Dataframe
    :param table_groundT: Ground truth Dataframe
    :return: Similarity Index Dataframe
    """
    df=pd.MultiIndex.from_product(
    [table_extracted["token"], table_groundT["token"]] ,names=["Extracted_token", "Gt_token"]).to_frame(index=False)

    jarowinkler = JaroWinkler()
    df["jarowinkler_sim"] = [jarowinkler.similarity(i, j) for i, j in zip(df["Extracted_token"], df["Gt_token"])]

    qgram=QGram(2)
    df["qgram_sim"] = [qgram.distance(i, j) for i, j in zip(df["Extracted_token"], df["Gt_token"])]

    jaccard=Jaccard(2)
    df["jaccard_sim"] = [jaccard.similarity(i, j) for i, j in zip(df["Extracted_token"], df["Gt_token"])]

    Dlavenstein=Damerau()
    df["Dlavenstein_sim"] = [Dlavenstein.distance(i, j) for i, j in zip(df["Extracted_token"], df["Gt_token"])]

    normalized_levenshtein = NormalizedLevenshtein()
    df["Nlavenstein_sim"] = [normalized_levenshtein.similarity(i, j) for i, j in zip(df["Extracted_token"], df["Gt_token"])]

    return df

def eval_metrics(similarity_score, num_of_gt_tokens, num_of_extracted_tokens):
    """
    Function computes evaluation metrics based on the computed Similarity Scores.
    :param similarity_score: Similarity Score Daatframe
    :return: Evaluation metrics namely Precision, Recall and F1/0.5/2 Score.
    """

    precision_nr=len(similarity_score[(similarity_score['jarowinkler_sim']>0.9) & (similarity_score['jaccard_sim']>0.7) ].drop_duplicates())
    precision_dr=num_of_extracted_tokens
    precision=precision_nr/precision_dr

    recall_nr=precision_nr
    recall_dr= num_of_gt_tokens
    recall=recall_nr/recall_dr

    if precision == 0 and recall == 0:
        return 0, 0, 0
    else:
        f1_score = (5 * precision * recall) / (precision + 4 * recall)
        return f1_score, precision, recall


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
        extractedtab=' '.join(list(map(' '.join,tables.T.astype(str).values.tolist())))
        tabs.append(extractedtab)
    #data_gt = table_gt['token'].astype(str).str.cat(sep=' ')
    data_ex = ' '.join(tabs)
    return  data_ex

def rotate(PDFlist):
    resultdata=[]
    for PDF in tqdm(PDFlist):
        camelottable_df = tabula_extract_table(PDF.pdf_name,PDF.filepath)
        if isinstance(camelottable_df, type(None)):
            continue
        data_ex=calculate_metrics(camelottable_df)
        id=os.path.splitext(PDF.pdf_name)[0]
        resultdata.append([id, data_ex])


    resultdf = pd.DataFrame(resultdata,columns=['ID', 'tabstring'])
    return resultdf

            # if camelottable_df != None:
            #     f11, prec, recal = calculate_metrics(camelottable_df, table_gt,PDF)
            # # f11t=0
            # # tabulatable_df = tabula_extract_table(PDF.pdf_name, int(PDF.page_number) + 1, PDF.filepath)
            # # if tabulatable_df != None:
            # #     f11t, prect, recalt = calculate_metrics(tabulatable_df, table_gt, PDF)
            # #print(f11, prec, recal)
            # if  f11 < 0.5:
            #     tab_coordinates = get_table_coordinates(PDF, table_gt)
            #     if tab_coordinates[0]==0:
            #         print('Skipping file due to heuristics failed !', PDF.pdf_name)
            #     else:
            #         camelottable_df = camelot_extract_table(PDF.pdf_name, int(PDF.page_number) + 1, PDF.filepath, tab_coordinates)
            #         f12, prec, recal = calculate_metrics(camelottable_df, table_gt, PDF)
            #         print('Camelot : ',f12, prec, recal, f12-f11)
            #
            #         # tabulatable_df = tabula_extract_table(PDF.pdf_name, int(PDF.page_number) + 1, PDF.filepath,tab_coordinates)
            #         # f12t, prect, recalt = calculate_metrics(tabulatable_df, table_gt, PDF)
            #         # print('Tabula : ', f12t, prect, recalt, f12t - f11t)




#PDFlist=load_data('/home/apurv/Thesis/DocBank/DocBank_samples/DocBank_samples')

def main():
    dirlist = [
                 'docbank_1611', 'docbank_1612',
                 'docbank_1701', 'docbank_1702', 'docbank_1703', 'docbank_1704',  'docbank_1706',
                 'docbank_1707', 'docbank_1708', 'docbank_1709', 'docbank_1710', 'docbank_1711', 'docbank_1712'
                 ]
    for dir in dirlist:
        #dirp = '/data/pdf'
        dirp="/data/docbank/" + dir
        tabdir = sort_label_files(dirp, "table")
        PDFlist=load_data_subset(tabdir)
        ex_df=rotate(PDFlist)
        groundtdf = create_gt_df(tabdir, 'table')
        final_df = pd.merge(ex_df, groundtdf, on='ID')
        result = compute_matrix(final_df)

        resultdf = pd.DataFrame(result,
                                columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])
        key = dir.split('_')[1]
        print(result)
        filename = 'tabula_extract_tab_' + key + '.csv'
        outputf = '/data/results/tabula/' + filename
        resultdf.to_csv(outputf, index=False)

if __name__ == "__main__":
    main()
