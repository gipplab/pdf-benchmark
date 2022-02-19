import pandas as pd
from base_coordinates import worker

def match_dfs(cordinate_df, tokens, topc ,botc):
    """
    Function to take the join of two dataframes. First it compares 4 consecutive tokens from Start and End of the table.
    Then it also compares difference between the coordinates for those tokens. Threshold for the difference is 10
    :param cordinate_df: Basic bounding box coordinates obtained from DocBank script.
    :param tokens: PDF Tokens
    :param topc: Coordinates of the first token in the table
    :param botc: Coordinates of the last token in the table.
    :return: Basic tokens of the First and Last token of the table.
    """
    cordinate_df['tablestart' ] =(cordinate_df['token'] == tokens[0]) & (cordinate_df['token'].shift(-1) == tokens[1]) & \
                               (cordinate_df['token'].shift(-2) == tokens[2])
    cordinate_df['tableend'] = (cordinate_df['token'] == tokens[5]) & (cordinate_df['token'].shift(1) == tokens[4]) & \
                               (cordinate_df['token'].shift(2) == tokens[3])
    tablestart =cordinate_df.loc[cordinate_df['tablestart'] == True]
    tableend =cordinate_df.loc[cordinate_df['tableend'] == True]

    if len(tablestart) == 1 and len(tableend) == 1:
        return tablestart, tableend
    elif len(tablestart) > 1 or len(tableend) > 1:
        tablestart.loc[:, "diff"] = tablestart["x0"].apply(lambda x: abs(x - topc[0]))
        new_tablestart =tablestart.loc[(tablestart['x0'] == topc[0]) & (tablestart['diff'] <= 4)]

        tableend.loc[:, "diff"] = tableend["x0"].apply(lambda x: abs(x - botc[0]))
        new_tableend = tableend.loc[(tableend['x0'] == botc[0]) & (tableend['diff'] <= 4)]
        if len(new_tablestart) != 1 or len(new_tableend) != 1:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return new_tablestart, new_tableend
    elif len(tablestart) == 0 or len(tableend) == 0:
        tabs= cordinate_df.loc[(cordinate_df['token'] == tokens[0])]
        tabe= cordinate_df.loc[(cordinate_df['token'] == tokens[5])]
        tabs.loc[:, "diff1"] = tabs["x0"].apply(lambda x: abs(x - topc[0]))
        tabs.loc[:, "diff2"] = tabs["y0"].apply(lambda x: abs(x - topc[1]))
        tabe.loc[:, "diff1"] = tabe["x0"].apply(lambda x: abs(x - botc[0]))
        tabe.loc[:, "diff2"] = tabe["y0"].apply(lambda x: abs(x - botc[1]))
        new_tablestart = tabs.loc[(tabs['diff1'] <= 10) & (tabs['diff2'] <= 10)]
        new_tableend = tabe.loc[(tabe['diff1'] <= 10) & (tabe['diff2'] <= 10)]
        if len(new_tablestart) != 1 or len(new_tableend) != 1:
            return pd.DataFrame(), pd.DataFrame()
        else:
            return new_tablestart, new_tableend
    else:
        return pd.DataFrame(), pd.DataFrame()


def camelot_coordinates(tablestart, tableend):
    """
    Function computes final "Table Regions" using tablestart and tableend coordinates.
    x0: Min(xMinS,xMinE)
    y0: Max(yMaxS,yMaxE)
    x1: Max(xMaxS,xMaxE)
    y1: Min(yMinS,yMinE)
    :param tablestart: Coordinates of the First token.
    :param tableend:  Coordinates of the Last token.
    :return: Table Region Coordinates.
    """
    start = tablestart[['xx0', 'yy0', 'xx1', 'yy1']]
    end = tableend[['xx0', 'yy0', 'xx1', 'yy1']]
    start =start.values.flatten().tolist()
    end =end.values.flatten().tolist()

    coordinates =[]
    coordinates.append(min(start[0] ,end[0]))
    coordinates.append(max(start[1] ,end[1]))
    coordinates.append(max(start[2] ,end[2]))
    coordinates.append(min(start[3] ,end[3]))

    coordinates = list(map(int, coordinates))
    return coordinates

def get_bbox(pdfname, pdfdir, pagenumber):
    """
    Function computes Bounding Boxes for a PDF. Sourcecode is taken from DocBanks pdf_process.py file.
    ('x0','y0','x1','y1') are Normalized co-ordiantes.
    ("xx0", "yy0", "xx1", "yy1") are basic bbox from PDFMiner.
    :param pdfname: Name of the PDF file
    :param pdfdir: Directory of the PDF file
    :param pagenumber: Page Number inside the PDF file
    :return: Dataframe with "token",'x0','y0','x1','y1', "xx0", "yy0", "xx1", "yy1"

    """
    cdf =worker(pdfname, pdfdir, pdfdir, 0) # To get the basic bbox from coordinates script
    return cdf


def calc_tokens(table_frame):
    """
    Function computes the top 4 and bottom 4 tokens along with their bounding boxes
    :param table_frame: Cropped Table Component in a dataframe.
    :return: Top + Bottom tokens in a list, Top token coordinates in a list, Bottom token coordinates in a list.
    """
    top3 = table_frame.head(3)
    bot3 = table_frame.tail(3)
    l1 =top3['token'].tolist()
    l2 =bot3['token'].tolist()
    lf= l1 + l2

    topx0 =table_frame[['x0' ,'y0' ,'x1' ,'y1']].head(1)
    botxo =table_frame[['x0' ,'y0' ,'x1' ,'y1']].tail(1)

    return lf, topx0.values.flatten().tolist(), botxo.values.flatten().tolist()

def get_table_coordinates(PDF, table_frame_labled):
    """
    Function call all other utilities in generateGT.py. Basically it takes a PDF object and Basic Coordinates Dataframe and joins them together
    to compute the ultimate "Table Areas" parameter of Camelot.
    :param PDF: PDF Object
    :return: Table area for camelot
    """
    token_list ,topc, botc = calc_tokens(table_frame_labled)
    cordinates_data = get_bbox(PDF.pdf_name, PDF.filepath,
                               0)  # Extra base coordinates for table_regions field.
    tablestart, tableend = match_dfs(cordinates_data, token_list, topc, botc)

    if tablestart.empty:
        coordinates = [0] * 4
        return coordinates  # Too much confusing data, heuristics failed. Hence, Sending 0s
    else:
        coordinates = camelot_coordinates(tablestart, tableend)
        return coordinates

