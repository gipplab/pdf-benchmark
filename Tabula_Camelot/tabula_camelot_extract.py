import os.path
import camelot
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import tabula

def tab_csv(tabs,output):
    """
    Function creates csv file for every table extracted by Camelot.
    :param tabs: Array of tables
    :param output: Output CSV file
    """
    no_of_tabs=len(tabs)
    for i in range(no_of_tabs):
        tabs[i].to_csv(output, mode='a')

def get_coordinatedf(tables):
    """
    Function computes the bounding box of the elements extracted by camelot.
    :param tables: Array of Tables extracted by camelot.
    :return: Dataframe with every elements in the table along with its Bounding Box information.
    """
    W, C = [], []
    for x, y in zip(tables[-1].df.__array__().tolist(), tables[-1].cells):
        for word, loc in zip(x, y):
            W.append(word)
            C.append(loc)

    df = DataFrame()
    df['word'] = W
    df['loc'] = C

    def make_coordinate_list(cellvar):
        cellvar = str(cellvar)
        list = cellvar.split(' ')
        x1 = list[1].split('=')[1]
        y1 = list[2].split('=')[1]
        x2 = list[3].split('=')[1]
        y2 = list[4].split('=')[1]
        y2 = y2[:-1]
        colist = [float(x1), float(y1), float(x2), float(y2)]
        return colist

    df['loc'] = df['loc'].apply(make_coordinate_list)
    df1 = df['word']
    df = pd.DataFrame(df['loc'].values.tolist())
    df2 = pd.concat([df1, df], axis=1)
    return df2


def camelot_extract_table(pdfname, dir, *coordinates):
    """
    Function extracts table from a PDF file using provided table region, page information in stream mode.
    :param pdfname: Name of the PDF
    :param coordinates: Table region computed in the genrateGT
    :param pagenumber:
    :param dir:
    :return:
    """
    # p = Path(dir + "/table_output/")
    # p.mkdir(parents=True, exist_ok=True)
    try:
        if not coordinates:
            fname = dir + os.sep + pdfname
            camelottabs = camelot.read_pdf(fname, flavor='stream')
        else:
            cordin=coordinates[0]
            cor = [str(i) for i in cordin]
            cor = ','.join(cor)
            cordi = [cor] # Converting [58,176,280,71] into ['58,176,280,71']
            fname=dir + os.sep + pdfname
            camelottabs = camelot.read_pdf(fname, flavor='stream',table_regions=cordi)
        if (len(camelottabs) == 0) :
            #print('No table found in file', pdfname)
            pass
        else:
            #print(len(tabs), 'table found in file', pdfname)
            return camelottabs
        #return tabs, get_coordinatedf(tabs)
    except(ZeroDivisionError):
        pass


def tabula_extract_table(pdfname, dir, *coordinates):
    """
    Function extracts table from a PDF file using provided table region, page information in stream mode.
    :param pdfname: Name of the PDF
    :param coordinates: Table region computed in the genrateGT
    :param pagenumber:
    :param dir:
    :return:
    """
    try:
        if not coordinates:
            fname = dir + os.sep + pdfname
            tabulatabs = tabula.read_pdf(fname,stream=True)
        else:
            cordin=coordinates[0]
            cor = [str(i) for i in cordin]
            cor = ','.join(cor)
            #cordi = [cor] # Converting [58,176,280,71] into ['58,176,280,71']
            fname=dir + os.sep + pdfname
            tabulatabs =  tabula.read_pdf(fname, stream=True, area=cor)
        if(len(tabulatabs) == 0) :
            #print('No table found in file', pdfname)
            pass
        else:
            #print(len(tabs), 'table found in file', pdfname)
            return tabulatabs
            #return tabs, get_coordinatedf(tabs)
    except(Exception):
        pass


