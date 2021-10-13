import os
import shutil
import tarfile
import sys
from glob import glob

from tqdm import tqdm


def change_pdf_name(pdfdir, txtdir):
    txtfiles = glob(os.path.join(txtdir, "*.{}".format('txt')))

    for txt in tqdm(txtfiles):
        fname=os.path.basename(txt)
        timestmp,keyword=fname.split('_')[1].replace('.gz','').split('.')
        name=fname.split('_')[1].replace('.gz', '')
        datapdfpath= pdfdir + os.sep + timestmp + os.sep + name + '.pdf'
        nwe = os.path.splitext(os.path.basename(fname))[0]  # 2.tar_1801.00617.gz_idempotents_arxiv_4.txt --> 2.tar_1801.00617.gz_idempotents_arxiv_4
        filekeyword = nwe.rpartition('_')[0]  # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 2.tar_1801.00617.gz_idempotents_arxiv
        page_number = nwe.split('_')[-1]  # 2.tar_1801.00617.gz_idempotents_arxiv_4 --> 4
        pdfname = txtdir  + os.sep + filekeyword + "_black.pdf"

        if os.path.isfile(datapdfpath):
            shutil.copy(datapdfpath, pdfname)

change_pdf_name('/home/apurv/Thesis/testd', '/home/apurv/Thesis/testd/docbank')