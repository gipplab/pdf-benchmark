import os
import shutil
from pathlib import Path
from shutil import copy
import pandas as pd
from refextract import extract_journal_reference, extract_references_from_file, extract_references_from_url
from MetadataExtraction.GROBID.evaluate import similarity_index, eval_metrics
from Table_Extraction.genrateGT import load_data


def sort_ref_files(dir):
    PDFlist = load_data(dir)
    p = Path(dir + "/ref_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
       get_gt_ref(PDF,  p, True)
    return str(p)

def get_gt_ref(PDFObj, p, retflag):
    """
    Function has two purpose controlled by retflag parameter.
    1. retflag==True : find the GT files in DocBank containing metadata labels and copy them into seperate directory in tree called "metadata_pdfs"
    2. retflag==False: return the reference dataframes
    :param PDF: PDF Object
    :param retflag: flag to control the role of the function.
    :return: Ground truth reference dataframe.
    """
    txt_data = PDFObj.txt_data
    ref_frame_labled = txt_data.loc[(txt_data['label'] == 'reference')]
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
    refdir=sort_ref_files("/home/apurv/Thesis/DocBank/DocBank_samples/DocBank_samples")
    PDFlist=load_data(refdir)
    for pdf in PDFlist:
        file=pdf.filepath + os.sep + pdf.pdf_name
        ex_references = extract_references_from_file(file)
        gt_ref = get_gt_ref(pdf, refdir, retflag=False)
        if len(ex_references) != 0:
            final_df=process_for_spec_ref(gt_ref, ex_references)
            similarity_df, no_of_gt_tok, no_of_ex_tok, ef_ex, lavsim = similarity_index(final_df, 'ref')
            f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
            print(lavsim, f1)
        else:
            print(0,0)
    shutil.rmtree(refdir)

if __name__ == "__main__":
    main()

