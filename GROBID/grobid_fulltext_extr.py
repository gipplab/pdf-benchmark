import csv
import os
import shutil
from pathlib import Path
from shutil import copy
from os.path import splitext
import pandas as pd
from tqdm import tqdm
from GROBID.evaluate import compute_sim_matrix
from PdfAct.pdfact_extract import crop_pdf, compute_metrics
from GROBID.grobid_metadata_extract import grobid_extract
from GROBID.grobid_parse_xml import parse_extracted_paragraphs, parse_extracted_tabs, parse_extracted_equation, \
     parse_extracted_list
from Tabula_Camelot.genrateGT import load_data, locate_data, PDF


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
            txtdf=pd.read_csv(txt,sep='\t',quoting=csv.QUOTE_NONE,encoding='latin1',usecols=[0,9], names=["token","label"])
            PDFlist.append(PDF(page_number,pdf_name,dir,txt_name,txtdf))
    return PDFlist


def get_gt_metadata(PDFObj, p, label, retflag):
    txt_data = PDFObj.txt_data
    gt_frame_labled = txt_data.loc[(txt_data['label'] == label)]
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

def create_gt_df(dir, label):
    PDFlist=load_data_subset(dir)
    IDs=[]
    values=[]
    pageno=[]
    for pdf in PDFlist:
        gt_df=get_gt_metadata(pdf, '',label, False)
        if isinstance(gt_df, type(None)):
            continue
        data_str = gt_df['token'].astype(str).str.cat(sep=' ')
        values.append(data_str)
        id=os.path.splitext(pdf.pdf_name)[0]
        IDs.append(id)
        pageno.append(pdf.page_number)
    gt= label + '_gt'
    data_gt_df=pd.DataFrame({'ID':IDs, gt:values, 'page':pageno})
    return data_gt_df

def compute_matrix(dataf):
    resultdata=[]
    df_extractednp = dataf['liststring'].to_numpy()
    df_groundtruthnp = dataf['list_gt'].to_numpy()
    matrix = compute_sim_matrix(df_extractednp, df_groundtruthnp)
    for index, row in dataf.iterrows():
        resultdata.append(['GROBID', row['ID'], row['page'], 'table', 0, 0, 0, matrix.iloc[index,index]])
    return resultdata


def sort_label_files(dir, label):
    PDFlist = load_data(dir)
    p = Path(dir + "/list_pdfs/")
    p.mkdir(parents=True, exist_ok=True)
    for PDF in PDFlist:
        get_gt_metadata(PDF, p,label, True)
    return str(p)

def delete_empty_tei(dir):
    papers = sorted(Path(dir).glob('*.tei.xml'))
    for tei in papers:
        if os.path.getsize(tei) == 0:
            os.remove(tei)


def main():
    dir_array = [ 'docbank_1402', 'docbank_1403', 'docbank_1404', 'docbank_1405', 'docbank_1406',
                 'docbank_1407', 'docbank_1408', 'docbank_1409',
                 'docbank_1410', 'docbank_1411', 'docbank_1412', 'docbank_1501', 'docbank_1502', 'docbank_1503',
                 'docbank_1504', 'docbank_1505', 'docbank_1506',
                 'docbank_1507', 'docbank_1508', 'docbank_1509', 'docbank_1510', 'docbank_1511', 'docbank_1512',
                 'docbank_1801', 'docbank_1802', 'docbank_1803', 'docbank_1804',
                 'docbank_1601', 'docbank_1602', 'docbank_1603', 'docbank_1604', 'docbank_1605', 'docbank_1606',
                 'docbank_1607', 'docbank_1608', 'docbank_1609', 'docbank_1610', 'docbank_1611', 'docbank_1612',
                 'docbank_1701', 'docbank_1702', 'docbank_1703', 'docbank_1704', 'docbank_1705', 'docbank_1706',
                 'docbank_1707', 'docbank_1708', 'docbank_1709', 'docbank_1710', 'docbank_1711', 'docbank_1712'
                 ]
    for dir in tqdm(dir_array):
        #dirp='/data/pdf'
        dirp = "/data/docbank/" + dir

        refdir = sort_label_files(dirp, "list")

        #Run GROBID Metadata Extraction
        grobid_extract(refdir, 'processFulltextDocument')

        #Delete the empty result files
        #delete_empty_tei(refdir)

        # # Parse TEI XML file from GROBID
        resultdf = parse_extracted_list(refdir)
        groundtdf= create_gt_df(refdir, 'list')
        final_df=pd.merge(resultdf.astype(str), groundtdf.astype(str), on='ID')
        result=compute_matrix(final_df)


        # Correlate gt to extracted references
        # PDFlist = load_data(refdir)
        # resultdata=[]
        # for pdf in tqdm(PDFlist):
        #     resultkey, ext = splitext(pdf.pdf_name)
        #     filtered_df = resultdf[resultdf.ID.eq(resultkey)]
        #     outputfile = pdf.filepath + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0] + "_extracted_paragraph.txt"
        #     ex_data=filtered_df[['parastring']]
        #     if len(ex_data.index) == 0:
        #         continue
        #     ex_data.to_csv(outputfile, index=False, header=False)
        #     if isinstance(outputfile, type(None)):
        #         continue
        #     if isinstance(pdf, type(None)):
        #         continue
        #     elif not os.path.isfile(outputfile):
        #         continue
        #     if os.path.getsize(outputfile) == 0:
        #         resultdata.append(['GROBID', pdf.pdf_name, pdf.page_number, 'paragraph', 0, 0, 0, 0])
        #     elif isinstance(compute_metrics(pdf, outputfile, 'paragraph'), type(None)):
        #         continue
        #     else:
        #         f1, pre, recall, lavsim = compute_metrics(pdf, outputfile, 'paragraph')
        #         resultdata.append(['GROBID', pdf.pdf_name, pdf.page_number, 'paragraph', pre, recall, f1, lavsim])
        resultdf = pd.DataFrame(result,
                                columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])
        key = dir.split('_')[1]
        filename = 'grobid_extract_list_' + key + '.csv'
        outputf = '/data/results/grobid/' + filename
        resultdf.to_csv(outputf, index=False)
        #shutil.rmtree(refdir)

if __name__ == "__main__":
    main()
