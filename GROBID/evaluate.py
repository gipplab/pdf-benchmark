import os
import shutil
from pathlib import Path
from shutil import copy
import pandas as pd
from similarity.damerau import Damerau
from similarity.jaccard import Jaccard
from similarity.jarowinkler import JaroWinkler
from tqdm import tqdm

from CERMINE.cermine_parse_xml import extract_cermine_metadata, parse_metadata_cermine
from GROBID.grobid_metadata_extract import parse_metadata, create_pdfmetadata_obj, grobid_extract
from Tabula_Camelot.genrateGT import load_data
from scipy.spatial.distance import cdist
from Levenshtein import ratio

pd.options.mode.chained_assignment = None

def fix_hyphanated_tokens(df):
    """
    This function is fixing the hyphanated words in Ground truth dataset. As it affects the score negatively when a tool can extract hyphanated words correctly.
    :param df: GT dataframe (non-empty)
    :return: GT dataframe (without hyphanated words)
    """
    # create new column 'Ending' for True/False if column 'author_ex' ends with '-'
    df['Ending'] = df['token'].shift(1).str.contains('-$', na=False, regex=True)
    # remove the trailing '-' from the 'author_ex' column
    df['token'] = df['token'].str.replace('-$', '', regex=True)
    # create new column with values of 'author_ex' and shifted 'author_ex' concatenated together
    df['author_ex_combined'] = df['token'] + df.shift(-1)['token']
    # create a series true/false but shifted up
    index = (df['Ending'] == True).shift(-1)
    # set the last row to 'False' after it was shifted
    index.iloc[-1] = False
    # replace 'author_ex' with 'author_ex_combined' based on true/false of index series
    df.loc[index, 'token'] = df['author_ex_combined']
    # remove rows that have the 2nd part of the 'author_ex' string and are no longer required
    df = df[~df.Ending]
    # remove the extra columns
    df.drop(['Ending', 'author_ex_combined'], axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df



def process_tokens(abs_ex, auth_ex, title_ex, abs_gt, auth_gt, title_gt, pdf_name_key, toolflag):
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
    if toolflag=='GROBID':
        for author in auth_ex:
            for person in author:
                authlist.append(person.firstname)
                authlist.append(person.middlename)
                authlist.append(person.surname)
        auth_ex = pd.DataFrame(authlist, columns=['Author'])
    if toolflag=='CERMINE':
        auth_ex = auth_ex.fillna('NAN')
        auth_ex=auth_ex.to_frame()
        auth_ex = auth_ex.rename(columns={'Authors': 'Author'})

    # DocBank has hyphanated words which are treated as seperate tokens. Affects the evaluation metrics hence fixing the hyphanated word problem in GT.

    if len(title_gt) != 0:
        title_gt=fix_hyphanated_tokens(title_gt)
    if len(abs_gt) != 0:
        abs_gt=fix_hyphanated_tokens(abs_gt)
    if len(auth_gt) != 0:
        auth_gt=fix_hyphanated_tokens(auth_gt)

    # Merge all the tokens and create a sentence
    auth_ex = auth_ex['Author'].str.cat(sep=' ')
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


def compute_sim_matrix(ex_nump, gt_nump):
    """
    This function computes the similarity matrix for each word from a numpy array. or it can also compare whole abstract as a collated tokens.
    :param ex_nump: Extracted paragraph as numpy array
    :param gt_nump: Ground truth paragraph as numpy array
    :return: Similarity Matrix with Lavensteins similarity index.
    """
    matrix = cdist(ex_nump.reshape(-1, 1), gt_nump.reshape(-1, 1), lambda x, y: ratio(x[0], y[0]))
    df = pd.DataFrame(data=matrix, index=ex_nump, columns=gt_nump)
    return df

def compute_tpfp(matrix):
    """
    This function considers Extracted token as Ground-truth token when its Levenshteins similarity index is > 0.7. Otherwise it is non-gt token.
    :param matrix: Similarity Matrix
    :return: Number of GT in ET, Number of Non GT
    """
    tp=0
    fp=0
    rows=matrix.shape[0]
    cols=matrix.shape[1]
    for x in range(0,rows):
        for y in range(0,cols):
            if matrix.iloc[x,y] > 0.7:
                flag=True
                break
            else:
                flag=False
        if flag is True:
            tp=tp+1
        else:
            fp=fp+1
    return tp,fp

def compute_scores(tp,fp, gttoken):
    """
    Function to compute the evaluation metrics.
    :param tp: Number of GT in ET
    :param fp: Number of Non-GT in ET
    :param gttoken: Number of GT
    :return: Precision, Recall and F1 Score
    """
    prec=tp/(tp+fp)
    recall= tp/gttoken
    if prec==0 and recall==0:
        return 0,0,0
    else:
        f1_score= (2 * prec * recall)/ (prec + recall)
        return f1_score, prec, recall


def compute_results(dataf, field):
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

    # Computing similarity not considering reading order.
    df_extractednp = dataf[extracted].to_numpy()
    df_groundtruthnp = dataf[groundtruth].to_numpy()
    matrix = compute_sim_matrix(df_extractednp, df_groundtruthnp)

    if field == 'paragraph':
        return 0,0,0,matrix.iloc[0,0]

    # Computing the count of tokens before adding the NaN ! This is important to avoid false calculation of the metrics.
    no_of_gt_tokens=len(df_groundtruth.index)
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
        df_e = df_extracted.to_numpy()
        df_g = df_groundtruth.to_numpy()
        simmatrix = compute_sim_matrix(df_e, df_g)

        tp,fp=compute_tpfp(simmatrix)
        f1,prec,recal=compute_scores(tp,fp,no_of_gt_tokens)

    return f1,prec,recal, matrix.iloc[0,0]


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
    dir_array = [ 'docbank_1801', 'docbank_1802', 'docbank_1803','docbank_1804']
    for dir in dir_array:
        #metadir = sort_metadata_files("/data/docbank/" + dir)

        # Run GROBID Metadata Extraction
        #grobid_extract(metadir, 'processHeaderDocument')
        #extract_cermine_metadata(metadir)

        # Parse TEI XML file from GROBID
        #resultdf = parse_metadata(metadir)
        resultdf = parse_metadata_cermine("/data/docbank/" + dir + "/metadata_pdfs/")

        # Create PDFMetadata Objects
        MetaObjList = create_pdfmetadata_obj("/data/docbank/" + dir + "/metadata_pdfs/", resultdf)

        # Clean-up the sorted files directory
        #shutil.rmtree(metadir, ignore_errors=True)

        # Process Every extracted metadata field(Title, Abstract, Author) and compute the metrics.
        resultdata=[]
        for MetaObj in tqdm(MetaObjList):
            # GT DFs
            titlegt, absgt, autgt = get_gt_metadata(MetaObj,MetaObj.filepath, False)
            # One Row Consolidation
            finadf = process_tokens(MetaObj.abstract, MetaObj.authors, MetaObj.title, absgt[['token']], autgt[['token']],
                                    titlegt[['token']], MetaObj.pdf_name, 'CERMINE')
            # Evaluate every metadata label.
            if len(absgt) != 0:
                f1, pre, recall, lavsim = compute_results(finadf, 'abstract')
                resultdata.append(['CERMINE', MetaObj.pdf_name, MetaObj.page_number, 'abstract',pre,recall, f1, lavsim])
            if len(titlegt) != 0:
                f1, pre, recall, lavsim  = compute_results(finadf, 'title')
                resultdata.append(['CERMINE', MetaObj.pdf_name, MetaObj.page_number, 'title', pre,recall, f1, lavsim])
            if len(autgt) != 0:
                f1, pre, recall, lavsim  = compute_results(finadf, 'author')
                resultdata.append(['CERMINE', MetaObj.pdf_name, MetaObj.page_number, 'author', pre,recall,f1, lavsim])
            if (len(absgt) == 0 and len(titlegt) == 0 and len(autgt) == 0) or (len(finadf) == 0):
                resultdata.append(['CERMINE', MetaObj.pdf_name, MetaObj.page_number, 'author', 0,0,0, 0])

        resultdf = pd.DataFrame(resultdata, columns=['Tool', 'ID', 'Page', 'Label', 'Precision','Recall' ,'F1', 'SpatialDist'])

        key = dir.split('_')[1]
        filename = 'cermine_extract_meta_' + key + '.csv'
        outputf = '/data/results/cermine/' + filename
        resultdf.to_csv(outputf, index=False)
        #shutil.rmtree(metadir)


if __name__ == "__main__":
    main()
