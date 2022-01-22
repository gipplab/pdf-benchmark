import os
import shutil
from pathlib import Path
from shutil import copy
import pandas as pd
from refextract import extract_references_from_file
from tqdm import tqdm

from GROBID.evaluate import compute_results
from Tabula_Camelot.genrateGT import load_data


def sort_files(dir, label):
    PDFlist = load_data(dir)
    p = Path(dir + "/sort_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
       get_gt_ref(PDF,  p, True, label)
    return str(p)

def get_gt_ref(PDFObj, p, retflag, label):
    """
    Function has two purpose controlled by retflag parameter.
    1. retflag==True : find the GT files in DocBank containing metadata labels and copy them into seperate directory in tree called "metadata_pdfs"
    2. retflag==False: return the reference dataframes
    :param PDF: PDF Object
    :param retflag: flag to control the role of the function.
    :return: Ground truth reference dataframe.
    """
    txt_data = PDFObj.txt_data
    ref_frame_labled = txt_data.loc[(txt_data['label'] == label)]
    if len(ref_frame_labled) != 0:
        if retflag == True:
            filename = PDFObj.filepath + os.sep + PDFObj.pdf_name
            txtname = PDFObj.filepath + os.sep + PDFObj.txt_name
            copy(filename, p)
            copy(txtname, p)
            return
        else:
            return ref_frame_labled

def process_for_spec_ref(gt_ref, ex_references):
    """
    This function is for refextract as using refextract we cannot extract only part of References from the PDF. It needs whole PDF for successful extraction.
    for example : if References are on page 27 and 28 in a pdf but in our dataset only 27 is label we have to handle thot by using this function.
    Here we find out the citation number from dataset and use it as a subscript to only select references which are present in the dataset.
    :param gt_ref: Ground Truth References only on specific page
    :param ex_references: Extracted References whole PDF wide
    :return: Dataframe with extracted references which are only present on specific page as in GT.
    """
    ex_ref = [x['raw_ref'] for x in ex_references]
    ex_df = pd.DataFrame(ex_ref)
    ex_df = ex_df.drop_duplicates().reset_index(drop=True)

    # num_df = gt_ref.loc[gt_ref.iloc[:, 0].str.contains(r'\[.*\]')]
    # num_df = num_df[['token']].reset_index(drop=True)
    # subscript = int(num_df['token'].iloc[0].strip('[').strip(']')) - 1
    #
    # ex_df = ex_df.loc[subscript:]

    ex_df = ex_df[0].str.cat(sep=' ')
    gt_ref = gt_ref['token'].str.cat(sep=' ')

    d = {
        'ref_gt': [gt_ref],
        'ref_ex': [ex_df],
    }
    final_df = pd.DataFrame(d)

    return final_df

def main():
    dir_array = ['docbank_1501','docbank_1502','docbank_1503','docbank_1504', 'docbank_1505', 'docbank_1506', 'docbank_1507', 'docbank_1508',
                 'docbank_1509', 'docbank_1510', 'docbank_1511', 'docbank_1512']
    for dir in dir_array:
        refdir=sort_files("/data/docbank/" + dir, 'reference')
        PDFlist=load_data(refdir)
        resultdata=[]
        for pdf in tqdm(PDFlist):
            file=pdf.filepath + os.sep + pdf.pdf_name
            if isinstance(file, type(None)):
                continue
            ex_references = extract_references_from_file(file)
            gt_ref = get_gt_ref(pdf, refdir, retflag=False)
            if len(ex_references) != 0:
                final_df=process_for_spec_ref(gt_ref, ex_references)
                f1, pre, recall, lavsim = compute_results(final_df, 'ref')
                # similarity_df, no_of_gt_tok, no_of_ex_tok, ef_ex, lavsim = compute_results(final_df, 'ref')
                # f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
                resultdata.append(['RefExtract', pdf.pdf_name, pdf.page_number, 'references', pre,recall,f1, lavsim])
            else:
                resultdata.append(['RefExtract', pdf.pdf_name, pdf.page_number, 'references', 0,0,0, 0])

        resultdf = pd.DataFrame(resultdata,columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])
        key=dir.split('_')[1]
        filename='refextract_extract_ref_' + key + '.csv'
        outputf='/data/results/refextract/' + filename
        resultdf.to_csv(outputf, index=False)
        shutil.rmtree(refdir)

if __name__ == "__main__":
    main()
