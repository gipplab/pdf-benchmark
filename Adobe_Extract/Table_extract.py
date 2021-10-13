import os
import shutil
import subprocess
from pathlib import Path
import pandas as pd
from tqdm import tqdm

from PdfAct.pdfact_extract import  crop_pdf
import zipfile
from GROBID.evaluate import fix_hyphanated_tokens, similarity_index, eval_metrics
from Tabula_Camelot.genrateGT import load_data


def sort_table_files(dir):
    PDFlist = load_data(dir)
    p = Path(dir + "/table_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
       get_gt_metadata(PDF,  p, True)
    return str(p)

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
    table_frame_labled = txt_data.loc[(txt_data['label'] == 'table') & (txt_data['token'] != "##LTLine##")]
    if len(table_frame_labled) != 0:
        if retflag == True:
            filename = PDFObj.filepath + os.sep + PDFObj.pdf_name
            txtname = PDFObj.filepath + os.sep + PDFObj.txt_name
            shutil.copy(filename, p)
            shutil.copy(txtname, p)
            return
        else:
            return table_frame_labled

def csv_from_excel(outzip):
    with zipfile.ZipFile(outzip) as z:
        count=0
        for filename in z.namelist():
            if filename.startswith('tables'):
                count=count + 1
        multi_tables=[]
        for c in range(count):
            tabledata=z.open("tables/fileoutpart" + str(c) + ".xlsx")
            table_df=pd.read_excel(tabledata, engine='openpyxl',sheet_name='Sheet1')
            table_df=table_df.replace(r'_x000D_', '', regex=True)
            table_df.columns = table_df.columns.str.replace(r'_x000D_', '', regex=True)

            header = table_df.columns.values.tolist()
            final_df = pd.melt(table_df)
            ex_df_temp = final_df[['value']]
            header.extend(ex_df_temp['value'].tolist())
            ex_df=pd.DataFrame({'value':header})

            if count != 1:
                multi_tables.append(ex_df)
            else:
                return ex_df
        if len(multi_tables) != 0:
            ex_df=pd.concat(multi_tables,ignore_index=True)
            return ex_df

def process_df(ex_df, gt_df):

    if len(gt_df) != 0:
        data_gt = fix_hyphanated_tokens(gt_df)

    #Merge all the tokens and create a sentence
    data_gt1=data_gt['token'].str.cat(sep=' ')
    data_ex = ex_df['value'].str.cat(sep=' ')

    d={
         'table_ex':[data_ex],
         'table_gt':[data_gt1],
    }
    final_df=pd.DataFrame(d)

    return final_df


def extract_table_adobe(dir):
    PDFlist=load_data(dir)
    Path(dir + "/output").mkdir(parents=True, exist_ok=True)
    resultdata=[]
    for pdf in tqdm(PDFlist):
        croppedfile = crop_pdf(pdf.filepath, pdf.pdf_name, pdf.page_number)

        outputfile = pdf.filepath + os.sep + "output" + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0]+ "_subset_" + pdf.page_number + "_extract.zip"

        subprocess.call(["python3","/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Adobe_Extract/adobe-dc-pdf-services-sdk-extract-python-samples/src/extractpdf/extract_txt_table_info_from_pdf.py"
                            , croppedfile])
        os.remove(croppedfile)

        if os.path.getsize(outputfile) != 0:
            extracted_df=csv_from_excel(outputfile)
            os.remove(outputfile)
            groundt_df=get_gt_metadata(pdf, dir, False)
            final_df=process_df(extracted_df, groundt_df)
            similarity_df, no_of_gt_tok, no_of_ex_tok, df_ex, lavsim = similarity_index(final_df, 'table')
            f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
            resultdata.append(['AdobeExtract',pdf.pdf_name,pdf.page_number, 'table', f1, lavsim])
        else:
            resultdata.append(['AdobeExtract', pdf.pdf_name,pdf.page_number, 'table', 0, 0])

    resultdf = pd.DataFrame(resultdata, columns=['Tool', 'ID', 'Page' ,'Label','F1','SpatialDist'])

    return resultdf


def main():
    tabledir = sort_table_files("/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/pdf")
    resultdf=extract_table_adobe(tabledir)
    resultdf.to_csv('adobe_extract.csv', index=False)
    shutil.rmtree(tabledir, ignore_errors=True)

if __name__ == "__main__":
    main()
