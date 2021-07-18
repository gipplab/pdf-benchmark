import os
import shutil
from pathlib import Path
from shutil import copy
import pandas as pd
from similarity.damerau import Damerau
from similarity.jaccard import Jaccard
from similarity.jarowinkler import JaroWinkler
from MetadataExtraction.GROBID.grobid_metadata_extract import parse_metadata, create_pdfmetadata_obj, grobid_extract
from Table_Extraction.genrateGT import load_data



def process_tokens(abs_ex, auth_ex, title_ex, abs_gt, auth_gt, title_gt, pdf_name_key):
    """
    Function creates an unniform dataframe containing extracted and ground truth tokens in a single row. (All tokens consolidated.)
    :param abs_ex: Abstract Extracted
    :param auth_ex: Author Extracted
    :param title_ex: Title Extracted
    :param abs_gt: Abstract ground truth
    :param auth_gt: Author ground truth
    :param title_gt: Title ground truth
    :param pdf_name_key: PDF Name as Key
    :return: Consolidated dataframe.
    """
    authlist=[]
    abs_ex=abs_ex.to_frame()
    title_ex=title_ex.to_frame()

    # Extract all the authors nested in XML.
    for author in auth_ex:
        for person in author:
            authlist.append(person.firstname)
            authlist.append(person.middlename)
            authlist.append(person.surname)

    # Merge all the tokens and create a sentence
    auth_ex=pd.DataFrame(authlist,columns=['Author'])
    auth_ex=auth_ex['Author'].str.cat(sep=' ')
    abs_gt=abs_gt['token'].str.cat(sep=' ')
    auth_gt=auth_gt['token'].str.cat(sep=' ')
    title_gt=title_gt['token'].str.cat(sep=' ')
    title_ex=title_ex['Title'].str.cat(sep=' ')
    abs_ex=abs_ex['Abstract'].str.cat(sep=' ')
    d={
         'abstract_ex':[abs_ex],
         'author_ex':[auth_ex],
         'title_ex':[title_ex],
         'abstract_gt':[abs_gt],
         'author_gt':[auth_gt],
         'title_gt':[title_gt],
        'pdf_name_key':[pdf_name_key]
    }
    final_df=pd.DataFrame(d)
    return final_df


def get_gt_metadata(PDFObj, p, retflag):
    """
    Function has two purpose controlled by retflag parameter.
    1. retflag==True : find the GT files in DocBank containing metadata labels and copy them into seperate directory in tree called "metadata_pdfs"
    2. retflag==False: return the repective(title, abstract, author) metadata dataframes
    :param PDF: PDF Object
    :param retflag: flag to control the role of the function.
    :return: Extracted ground truth metadata dataframes - title, abstract, author.
    """
    txt_data = PDFObj.txt_data
    title_frame_labled = txt_data.loc[(txt_data['label'] == 'title')]
    abstract_frame_labled = txt_data.loc[(txt_data['label'] == 'abstract')]
    author_frame_labled = txt_data.loc[(txt_data['label'] == 'author')]
    if len(title_frame_labled) != 0 or len(abstract_frame_labled) !=0 or len(author_frame_labled) != 0:
        if retflag == True:
            filename = PDFObj.filepath + os.sep + PDFObj.pdf_name
            txtname = PDFObj.filepath + os.sep + PDFObj.txt_name
            copy(filename, p)
            copy(txtname, p)
            return
        else:
            return title_frame_labled, abstract_frame_labled, author_frame_labled

def similarity_index(dataf, field):
    """
    Function computes the similarity index and string distance for extracted and ground truth tokens.
    :param dataf: dataframe with one row of extracted and ground truth
    :param field: Token for which similarity is computed. e.g. Title, Abstract, Author.
    :return: Dataframe with computed similarity indices, no. of extracted tokens, no. of ground truth tokens.
    """
    extracted=field + '_ex'
    groundtruth=field + '_gt'
    df_extracted=dataf[[extracted]]
    df_groundtruth=dataf[[groundtruth]]
    df_extracted = df_extracted.astype(str).applymap(str.split).apply(pd.Series.explode,axis=0).reset_index().drop("index", 1)
    df_groundtruth = df_groundtruth.astype(str).applymap(str.split).apply(pd.Series.explode, axis=0).reset_index().drop("index", 1)
    df_extracted=df_extracted.applymap(str)
    # Compting the count of tokens before adding the NaN ! This is important to avoid false calculation of the metrics.
    no_of_gt_tokens=len(df_groundtruth.index)
    no_of_ex_tokens=len(df_extracted.index)
    # Adding NaN to the dataframes if their length is not equal.
    if (len(df_extracted.index)-len(df_groundtruth.index)) < 0:
        diff=abs(len(df_extracted.index)-len(df_groundtruth.index))
        for i in range(diff):
            df_extracted.loc[len(df_extracted)] = 'NaN'
    if (len(df_extracted.index)-len(df_groundtruth.index)) > 0:
        diff = (len(df_extracted.index)-len(df_groundtruth.index))
        for i in range(diff):
            df_groundtruth.loc[len(df_groundtruth)] = 'NaN'
    if (len(df_extracted.index)-len(df_groundtruth.index)) == 0:
        # Computing similarity index which also considers the token sequence !! as ZIP is used.
        jarowinkler = JaroWinkler()
        df_groundtruth['jarowinkler_sim'] = [jarowinkler.similarity(x.lower(), y.lower()) for x, y in zip(df_extracted[extracted], df_groundtruth[groundtruth])]

        jaccard = Jaccard(2)
        df_groundtruth['jaccard_sim'] = [jaccard.similarity(x.lower(), y.lower()) for x, y in
                                         zip(df_extracted[extracted], df_groundtruth[groundtruth])]
        Dlavenstein = Damerau()
        df_groundtruth["Dlavenstein_sim"] = [Dlavenstein.distance(i.lower(), j.lower()) for i, j in zip(df_extracted[extracted], df_groundtruth[groundtruth])]
    return df_groundtruth, no_of_gt_tokens, no_of_ex_tokens, df_extracted

def eval_metrics(similarity_score, num_of_gt_tokens, num_of_extracted_tokens):
    """
    Function computes evaluation metrics based on the computed Similarity Scores.
    :param similarity_score: Similarity Score Daatframe
    :return: Evaluation metrics namely Precision, Recall and F1/0.5/2 Score.
    """
    # Setting the similarity index thresholds to 0.5, 0.3 and 4 based on the sample data.
    precision_nr=len(similarity_score[(similarity_score['jarowinkler_sim']>0.5) & (similarity_score['jaccard_sim']>0.3) &
                                      (similarity_score['Dlavenstein_sim']<=3)])
    precision_dr=num_of_extracted_tokens
    precision=precision_nr/precision_dr

    recall_nr=precision_nr
    recall_dr= num_of_gt_tokens
    recall=recall_nr/recall_dr

    if precision==0 and recall==0:
        return 0,0,0
    else:
        f1_score= (2 * precision * recall)/ (precision + recall)
        return f1_score, precision, recall


def sort_metadata_files(dir):
    PDFlist = load_data(dir)
    p = Path(dir + "/metadata_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
       get_gt_metadata(PDF,  p, True)
    return str(p)
    # if os.path.isdir(str(metadir)):
    #     return metadir
    # else:
    #     return None


def main():
    metadir = sort_metadata_files("/home/apurv/Thesis/DocBank/DocBank_samples/DocBank_samples")
    # Run GROBID Metadata Extraction
    grobid_extract(metadir, 'processHeaderDocument')
    # Parse TEI XML file from GROBID
    resultdf = parse_metadata(metadir)
    # Create PDFMetadata Objects
    MetaObjList = create_pdfmetadata_obj(metadir, resultdf)
    # Clean-up the sorted files directory
    shutil.rmtree(metadir, ignore_errors=True)
    # Process Every extracted metadata field(Title, Abstract, Author) and compute the metrics.
    for MetaObj in MetaObjList:
        # GT DFs
        titlegt, absgt, autgt = get_gt_metadata(MetaObj,MetaObj.filepath, False)
        # One Row Consolidation
        finadf = process_tokens(MetaObj.abstract, MetaObj.authors, MetaObj.title, absgt[['token']], autgt[['token']],
                                titlegt[['token']], MetaObj.pdf_name)
        # Evaluate every metadata label.
        if len(absgt) != 0:
            similarity_df, no_of_gt_tok, no_of_ex_tok, df_ex = similarity_index(finadf, 'abstract')
            f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
            print('Abstract', f1, pre, recall)
        if len(titlegt) != 0:
            similarity_df, no_of_gt_tok, no_of_ex_tok, df_ex = similarity_index(finadf, 'title')
            f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
            print('Title', f1, pre, recall)
        if len(autgt) != 0:
            similarity_df, no_of_gt_tok, no_of_ex_tok, ef_ex = similarity_index(finadf, 'author')
            f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
            print('Author', f1, pre, recall)


if __name__ == "__main__":
    main()
