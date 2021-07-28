import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from shutil import copy
from os import path
import pandas as pd
from MetadataExtraction.GROBID.evaluate import fix_hyphanated_tokens, similarity_index, eval_metrics
from Table_Extraction.genrateGT import load_data, PDF
from PyPDF2 import PdfFileReader, PdfFileWriter


def load_data(dir, labe):
    """
    Function creates the PDF objects for the gives base directory of DocBank dataset.
    :param dir: Base location of DocBank dataset.
    :return: List of PDF Objects.
    """
    txtf = glob(path.join(dir,"*.{}".format('txt')))
    PDFlist=[]

    for txt in txtf:
        nwe=os.path.splitext(os.path.basename(txt))[0] # 2.tar_1801.00617.gz_idempotents_arxiv_4.txt --> 2.tar_1801.00617.gz_idempotents_arxiv_4
        keyword=nwe.rpartition('_')[0] # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 2.tar_1801.00617.gz_idempotents_arxiv
        page_number=nwe.split('_')[-1]  # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 4
        pdfn = dir + "/" +keyword + "_black.pdf"
        if os.path.isfile(pdfn):
            pdf_name=os.path.basename(pdfn)
            txt_name=os.path.basename(txt)
            txtdf=pd.read_csv(txt,sep='\t',usecols=[0,1,2,3,4,9], names=["token", "x0", "y0", "x1", "y1","label"])
            found = txtdf[txtdf['label']==labe].index.tolist()
            if len(found) != 0:
                PDFlist.append(PDF(page_number,pdf_name,dir,txt_name,txtdf))
    return PDFlist

def process_tokens(data_gt, extracted_file, label):

    text=pd.read_csv(extracted_file, sep='\n', header=None).astype(str)[0].str.cat()
    data_ex = pd.DataFrame([text], columns=['extracted'])

    #DocBank has hyphanated words which are treated as seperate tokens. Affects the evaluation metrics hence fixing the hyphanated word problem in GT.
    if len(data_gt) != 0:
        data_gt=fix_hyphanated_tokens(data_gt)

    #Merge all the tokens and create a sentence
    data_gt=data_gt['token'].str.cat(sep=' ')
    data_ex = data_ex['extracted'].str.cat(sep=' ')

    ex=label + '_ex'
    gt=label + '_gt'

    d={
         ex:[data_ex],
         gt:[data_gt],
    }
    final_df=pd.DataFrame(d)
    return final_df

def compute_metrics(pdf, extracted_file, label):
    txt_data=pdf.txt_data
    data_gt=txt_data.loc[(txt_data['label'] == label) & (txt_data['token'] != "##LTLine##")]
    final_df=process_tokens(data_gt,extracted_file, label)
    if len(data_gt) != 0:
        similarity_df, no_of_gt_tok, no_of_ex_tok, df_ex, lavsim = similarity_index(final_df, label)
        f1, pre, recall = eval_metrics(similarity_df, no_of_gt_tok, no_of_ex_tok)
        #print(similarity_df)
        return f1,pre, recall, lavsim

def crop_pdf(pdfpath,pdfname, pagenumber):
    pdf_file_name = pdfname
    file_base_name = pdf_file_name.replace('.pdf', '')

    pdf = PdfFileReader(pdfpath + os.sep + pdf_file_name)

    #pages = [pagenumber] # page 1, 3, 5
    pdfWriter = PdfFileWriter()

    #for page_num in pages:
    pdfWriter.addPage(pdf.getPage(int(pagenumber)))

    cropped_file=pdfpath + os.sep + file_base_name + '_subset_' + pagenumber + '.pdf'
    with open(cropped_file, 'wb') as f:
        pdfWriter.write(f)
        f.close()
    return cropped_file

def extract_label_pdfact(dir):
    #label_array=['caption','author','title', 'abstract','section', 'footer','table','reference']
    label_array=['equation']
    for label in label_array:
        PDFlist=load_data(dir, label)
        for pdf in PDFlist:
            print(pdf.pdf_name, label)
            pdfpath=pdf.filepath + os.sep + pdf.pdf_name
            croppedfile=crop_pdf(pdf.filepath, pdf.pdf_name, pdf.page_number)
            outputfile= pdf.filepath + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0] + "_extracted_" + label + ".txt"
            if label == 'title' or label == 'abstract' or label == 'author' or label == 'reference':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", label, pdfpath, outputfile])
            elif label == 'section':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'heading', croppedfile, outputfile])
                os.remove(croppedfile)
            elif label == 'equation':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'formula', croppedfile, outputfile])
                os.remove(croppedfile)
            else:
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", label, croppedfile, outputfile])
                os.remove(croppedfile)

            if os.path.getsize(outputfile) == 0:
                print("0,0,0,0")
                os.remove(outputfile)
            else:
                f1,pre,recall, lavsim=compute_metrics(pdf, outputfile, label)
                os.remove(outputfile)
                print(f1,pre, recall, lavsim)



extract_label_pdfact("/home/apurv/Thesis/DocBank/DocBank_samples/DocBank_samples")