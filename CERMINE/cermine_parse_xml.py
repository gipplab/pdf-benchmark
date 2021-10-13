import csv
import math
import re
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
import os
import lxml.etree as et
from pathlib import Path

def extract_cermine_metadata(dir):
    subprocess.call(["java", "-cp", "/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/CERMINE/cermine-impl-1.13-jar-with-dependencies.jar", "pl.edu.icm.cermine.ContentExtractor",
                     "-path",dir, "-outputs", "jats"])


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