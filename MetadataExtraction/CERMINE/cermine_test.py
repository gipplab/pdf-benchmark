import csv
import math
import re
import subprocess
from multiprocessing import Pool

import pandas as pd

from MetadataExtraction.GROBID.grobid_parse_xml import Person
from bs4 import BeautifulSoup
import os
import lxml.etree as et
from pathlib import Path

def extract_cermine_metadata(dir):
    subprocess.call(["java", "-cp", "/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/MetadataExtraction/CERMINE/cermine-impl-1.13-jar-with-dependencies.jar", "pl.edu.icm.cermine.ContentExtractor",
                     "-path",dir, "-outputs", "jats"])


def get_article_abs_title(article_file, tag_path_elements=None):
    """
    :param article_file: the xml file for a single article
    :param tag_path_elements: xpath search results of the location in the article's XML tree
    :param article_file: individual local PLOS XML article
    :return: plain-text string of content in abstract
    """
    if tag_path_elements is None:
        tag_path_elements = ("/",
                             "article",
                             "front",
                             "article-meta",
                             "abstract")
    article_tree = et.parse(article_file)
    article_root = article_tree.getroot()
    tag_location = '/'.join(tag_path_elements)
    abstract = article_root.xpath(tag_location)
    abstract_text = et.tostring(abstract[0], encoding='unicode', method='text')

    # clean up text: rem white space, new line marks, blank lines
    abstract_text = abstract_text.strip().replace('  ', '')
    abstract_text = os.linesep.join([s for s in abstract_text.splitlines() if s])

    return abstract_text

def parse_author(file):
    handler = open(file).read()
    soup = BeautifulSoup(handler, features="lxml")
    authors_in_header = soup.find_all('contrib')
    title=soup.find_all('article-title')[0].string
    abs=soup.find_all('abstract')[0].text.strip()
    aulist=[]
    for author in authors_in_header:
        au=author.find("string-name")
        aulist.append(au.text)

    return aulist, title, abs


def pers_objs(authors):
    result=[]
    for author in authors:
        if author.count(" ") == 2:
            au=author.split()
            #person=Person(au[0],au[1], au[2])
            result.append(au[0])
            result.append(au[1])
            result.append(au[2])
        if author.count(" ") == 1:
            au=author.split()
            #person=Person(au[0], "", au[1])
            result.append(au[0])
            result.append(au[1])
    restr = ' '.join(result)
    return restr

def parse_metadata_cermine(dir):
    papers = sorted(Path(dir).glob('*.cermxml'))
    if os.path.isfile('final.csv'):
        os.remove('final.csv')
    for paper in papers:
        paper=str(paper)
        #abstract=get_article_abs_title(paper)
        #title=get_article_abs_title(paper, ("/","article","front","article-meta","title-group"))
        authors, title, abstract=parse_author(paper)
        pers_authors=pers_objs(authors)
        ID=Path(paper).stem
        with open('final.csv' ,'a') as csvfile:
            fieldnames = ['ID', 'Title', 'Abstract', 'Author']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'ID': ID, 'Title': title, 'Abstract':abstract, 'Author':pers_authors})

    result_csv = pd.read_csv('final.csv',sep=',', names=['ID', 'Title', 'Abstract', 'Authors'])

    return result_csv

#parse_metadata_cermine("/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/pdf/")