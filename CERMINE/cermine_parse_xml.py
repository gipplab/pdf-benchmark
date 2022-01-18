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
    if len(soup.find_all('contrib')) ==0:
        aulist=[]
    else:
        aulist = []
        authors_in_header = soup.find_all('contrib')
        for author in authors_in_header:
            au = author.find("string-name")
            aulist.append(au.text)
    if len(soup.find_all('article-title')) == 0:
        title=''
    else:
        title=soup.find_all('article-title')[0].string
    if len(soup.find_all('abstract')) ==0:
        abs=''
    else:
        abs=soup.find_all('abstract')[0].text.strip()

    return aulist, title, abs

def parse_para(file):
    handler = open(file).read()
    soup = BeautifulSoup(handler, features="lxml")
    paratags=soup.select('p')
    para=[]
    for tag in paratags:
        if tag.parent.name == 'sec':
            para.append(tag.text)
    return ' '.join(para)

def parse_sec(file):
    handler = open(file).read()
    soup = BeautifulSoup(handler, features="lxml")
    sectags=soup.select('p')
    sec=[]
    for tag in sectags:
        if tag.parent.name == 'sec' and len(tag.text) <= 50:
            sec.append(tag.text)
    return ' '.join(sec)

def parse_ref(file):
    handler = open(file).read()
    soup = BeautifulSoup(handler, features="lxml")
    reftags=soup.select('ref')
    ref=[]
    for tag in reftags:
        if tag.parent.name == 'ref-list':
            ref.append(tag.text)
    return ' '.join(ref)


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
    dfarray=[]
    for paper in papers:
        paper=str(paper)
        authors, title, abstract=parse_author(paper)
        pers_authors=pers_objs(authors)
        ID=Path(paper).stem
        dfarray.append([ID, title, abstract, pers_authors])
    parseddf = pd.DataFrame(dfarray,columns=['ID', 'Title', 'Abstract', 'Authors'])
    return parseddf

def parse_para_cermine(dir):
    papers = sorted(Path(dir).glob('*.cermxml'))

    dfarray=[]
    for paper in papers:
        paper=str(paper)
        para=parse_para(paper)
        ID=Path(paper).stem
        dfarray.append([ID, para])
    parseddf = pd.DataFrame(dfarray,columns=['ID', 'paragraph_ex'])
    return parseddf

def parse_sec_cermine(dir):
    papers = sorted(Path(dir).glob('*.cermxml'))
    dfarray=[]
    for paper in papers:
        paper=str(paper)
        para=parse_sec(paper)
        ID=Path(paper).stem
        dfarray.append([ID, para])

    parseddf = pd.DataFrame(dfarray,columns=['ID', 'section_ex'])
    return parseddf

def parse_ref_cermine(dir):
    papers = sorted(Path(dir).glob('*.cermxml'))
    dfarray=[]
    for paper in papers:
        paper=str(paper)
        para=parse_ref(paper)
        ID=Path(paper).stem
        dfarray.append([ID, para])

    parseddf = pd.DataFrame(dfarray,columns=['ID', 'reference_ex'])
    return parseddf

# parse=parse_ref_cermine("/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/Docbank_sample/sort_pdfs")
# print(parse)
