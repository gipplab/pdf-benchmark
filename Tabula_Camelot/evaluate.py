import pandas as pd
from similarity.damerau import Damerau
from similarity.jaccard import Jaccard
from similarity.jarowinkler import JaroWinkler
from similarity.normalized_levenshtein import NormalizedLevenshtein
from similarity.qgram import QGram
from tqdm import tqdm
from Tabula_Camelot.tabula_camelot_extract import tabula_extract_table, camelot_extract_table
from Tabula_Camelot.table_area_heuristics import get_table_coordinates
from Tabula_Camelot.genrateGT import format_tablecells_dfs, get_gt_table, load_data


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



def calculate_metrics(table_df, table_gt, PDF):
    table_extracted = format_tablecells_dfs(table_df, PDF, True)
    similarity_score = calc_similarity(table_extracted.drop_duplicates(), table_gt[["token"]])
   # print(table_gt)
    f1, prec, recal = eval_metrics(similarity_score, len(table_gt.index), len(table_extracted.drop_duplicates()))
    return f1, prec, recal

def rotate(PDFlist):
    for PDF in tqdm(PDFlist):
        table_gt=get_gt_table(PDF)
        if len(table_gt)==0 :
            #print('PDF Does not contain a Table')
            pass
        else:
            print('processing  file', PDF.pdf_name)
            camelottable_df = camelot_extract_table(PDF.pdf_name, int(PDF.page_number) + 1,PDF.filepath)
            if camelottable_df != None:
                f11, prec, recal = calculate_metrics(camelottable_df, table_gt,PDF)
            # f11t=0
            # tabulatable_df = tabula_extract_table(PDF.pdf_name, int(PDF.page_number) + 1, PDF.filepath)
            # if tabulatable_df != None:
            #     f11t, prect, recalt = calculate_metrics(tabulatable_df, table_gt, PDF)
            #print(f11, prec, recal)
            if  f11 < 0.5:
                tab_coordinates = get_table_coordinates(PDF, table_gt)
                if tab_coordinates[0]==0:
                    print('Skipping file due to heuristics failed !', PDF.pdf_name)
                else:
                    camelottable_df = camelot_extract_table(PDF.pdf_name, int(PDF.page_number) + 1, PDF.filepath, tab_coordinates)
                    f12, prec, recal = calculate_metrics(camelottable_df, table_gt, PDF)
                    print('Camelot : ',f12, prec, recal, f12-f11)

                    # tabulatable_df = tabula_extract_table(PDF.pdf_name, int(PDF.page_number) + 1, PDF.filepath,tab_coordinates)
                    # f12t, prect, recalt = calculate_metrics(tabulatable_df, table_gt, PDF)
                    # print('Tabula : ', f12t, prect, recalt, f12t - f11t)




#PDFlist=load_data('/home/apurv/Thesis/DocBank/DocBank_samples/DocBank_samples')
PDFlist=load_data('/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/Data/pdf')
rotate(PDFlist)
