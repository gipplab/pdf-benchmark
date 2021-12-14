import csv
import os
import random
import subprocess
from glob import glob
from os import path
import pandas as pd
from tqdm import tqdm
from GROBID.evaluate import fix_hyphanated_tokens, compute_results
from Tabula_Camelot.genrateGT import load_data, PDF
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
            txtdf=pd.read_csv(txt,sep='\t',quoting=csv.QUOTE_NONE, encoding='latin1',usecols=[0,1,2,3,4,9], names=["token", "x0", "y0", "x1", "y1","label"])
            found = txtdf[txtdf['label']==labe].index.tolist()
            if len(found) != 0:
                PDFlist.append(PDF(page_number,pdf_name,dir,txt_name,txtdf))
    return PDFlist

def process_tokens(data_gt, extracted_file, label):

    # DocBank has hyphanated words which are treated as seperate tokens. Affects the evaluation metrics hence fixing the hyphanated word problem in GT.
    # if len(data_gt) != 0:
    #     data_gt=fix_hyphanated_tokens(data_gt)

    text=pd.read_csv(extracted_file, quoting=csv.QUOTE_NONE,encoding='latin1',engine='python', sep='\n', header=None).astype(str)[0].str.cat()
    data_ex = pd.DataFrame([text], columns=['extracted'])
    # Merge all the tokens and create a stream
    data_gt = data_gt['token'].astype(str).str.cat(sep=' ')
    data_ex = data_ex['extracted'].astype(str).str.cat(sep=' ')

    ex = label + '_ex'
    gt = label + '_gt'

    d = {
        ex: [data_ex],
        gt: [data_gt],
    }
    final_df = pd.DataFrame(d)
    return final_df

def compute_metrics(pdf, extracted_file, label):
    txt_data=pdf.txt_data
    data_gt=txt_data.loc[(txt_data['label'] == label) & (txt_data['token'] != "##LTLine##")]
    final_df=process_tokens(data_gt,extracted_file, label)
    if len(data_gt) != 0:
        f1,pre,recall,lavsim=compute_results(final_df, label)
        return f1,pre, recall, lavsim

def crop_pdf(pdfpath,pdfname, pagenumber):
    #pages = [pagenumber] # page 1, 3, 5
    try:
        pdf_file_name = pdfname
        file_base_name = pdf_file_name.replace('.pdf', '')
        pdf = PdfFileReader(pdfpath + os.sep + pdf_file_name, strict=False)
        pdfWriter = PdfFileWriter()
        #for page_num in pages:
        pdfWriter.addPage(pdf.getPage(int(pagenumber)))
        cropped_file=pdfpath + os.sep + file_base_name + '_subset_' + pagenumber + '.pdf'
        with open(cropped_file, 'wb') as f:
            pdfWriter.write(f)
            f.close()
        return cropped_file
    except Exception:
        pass

def extract_label_pdfact(dir):
    #label_array=['caption','author','title', 'abstract','section', 'footer','table','reference', 'body']
    label_array=['equation']
    resultdata=[]
    for label in label_array:
        PDFlist=load_data(dir, label)
        for pdf in tqdm(PDFlist):
            pdfpath=pdf.filepath + os.sep + pdf.pdf_name
            croppedfile=crop_pdf(pdf.filepath, pdf.pdf_name, pdf.page_number)
            outputfile= pdf.filepath + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0] + "_extracted_" + label + ".txt"

            if isinstance(croppedfile,type(None)):
                continue

            if label == 'title' or label == 'abstract' or label == 'authors' or label == 'reference':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", label, pdfpath, outputfile])
                os.remove(croppedfile)
            elif label == 'section':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'heading', croppedfile, outputfile])
                os.remove(croppedfile)
            elif label == 'equation':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'formula', croppedfile, outputfile])
                os.remove(croppedfile)
            elif label == 'paragraph':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'body', croppedfile, outputfile])
                os.remove(croppedfile)
            elif label == 'list':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'itemize-item', croppedfile, outputfile])
                os.remove(croppedfile)
            elif label == 'formula':
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", 'formula', croppedfile, outputfile])
                os.remove(croppedfile)
            else:
                subprocess.call(["./pdfact/bin/pdfact", "--include-roles", label, croppedfile, outputfile])
                os.remove(croppedfile)

            if isinstance(outputfile, type(None)):
                continue
            if isinstance(pdf, type(None)):
                continue
            elif not os.path.isfile(outputfile):
                continue
            elif os.path.getsize(outputfile) == 0:
                #resultdata.append(['GROBID', pdf.pdf_name, pdf.page_number, label,random.uniform(0.4,0.5), random.uniform(0.4,0.5), random.uniform(0.8,1.0), random.uniform(0.8,1.0)])
                resultdata.append(['Pdfact', pdf.pdf_name, pdf.page_number, label, 0,0,0,0])
                os.remove(outputfile)
            else:
                f1,pre,recall, lavsim=compute_metrics(pdf, outputfile, label)
                lavsim=compute_metrics(pdf, outputfile, label)
                resultdata.append(['Pdfact', pdf.pdf_name, pdf.page_number, label, pre, recall, f1, lavsim])
                os.remove(outputfile)
    resultdf = pd.DataFrame(resultdata,
                            columns=['Tool', 'ID', 'Page', 'Label','Precision','Recall', 'F1', 'SpatialDist'])
    return resultdf

def main():
    #dir_array = ['docbank_1401', 'docbank_1402', 'docbank_1403', 'docbank_1404', 'docbank_1405', 'docbank_1406']
    dir_array = [  'docbank_1401', 'docbank_1402', 'docbank_1403', 'docbank_1404', 'docbank_1405', 'docbank_1406', 'docbank_1407', 'docbank_1408', 'docbank_1409',
                   'docbank_1410', 'docbank_1411', 'docbank_1412', 'docbank_1501', 'docbank_1502', 'docbank_1503', 'docbank_1504', 'docbank_1505','docbank_1506',
                   'docbank_1507', 'docbank_1508', 'docbank_1509', 'docbank_1510', 'docbank_1511', 'docbank_1512',
                   'docbank_1801', 'docbank_1802', 'docbank_1803', 'docbank_1804',
                   'docbank_1601', 'docbank_1602', 'docbank_1603', 'docbank_1604', 'docbank_1605', 'docbank_1606',
                   'docbank_1607', 'docbank_1608', 'docbank_1609','docbank_1610', 'docbank_1611', 'docbank_1612',
                   'docbank_1701', 'docbank_1702', 'docbank_1703', 'docbank_1704', 'docbank_1705', 'docbank_1706',
                   'docbank_1707', 'docbank_1708', 'docbank_1709', 'docbank_1710', 'docbank_1711', 'docbank_1712'
                 ]
    for dir in dir_array:
        resultdf=extract_label_pdfact("/data/docbank/" + dir)
        key=dir.split('_')[1]
        filename='pdfact_extract_eq_' + key + '.csv'
        outputf='/data/results/Pdfact/' + filename
        resultdf.to_csv(outputf, index=False)

    # resultdf = extract_label_pdfact('/data/ProjectDir/Data/pdf')
    # resultdf.to_csv('/data/results/Pdfact/output_Result.csv', index=False)
if __name__ == "__main__":
    main()