import pandas as pd
from bs4 import BeautifulSoup
from dataclasses import dataclass
from os.path import basename, splitext
import glob
from pathlib import Path
import multiprocessing
from multiprocessing.pool import Pool

# Data structure for the Author from XML file.
@dataclass
class Person:
    firstname: str
    middlename: str
    surname: str

class TEIFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.soup = read_tei(filename)
        self._text = None
        self._title = ''
        self._abstract = ''


    @property
    def doi(self):
        """
        Function to parse DOI (Date of Issue) from XML
        :return: DOI in string.
        """
        idno_elem = self.soup.find('idno', type='DOI')
        if not idno_elem:
            return ''
        else:
            return idno_elem.getText()

    @property
    def title(self):
        """
        Function to parse Title from XML
        :return: Title in string
        """
        if not self._title:
            self._title = self.soup.title.getText()
        return self._title

    @property
    def abstract(self):
        """
        Function to parse the Abstract from XML
        :return: Abstract in string
        """
        if not self._abstract:
            abstract = self.soup.abstract.getText(separator=' ', strip=True)
            self._abstract = abstract
        return self._abstract

    @property
    def authors(self):
        """
        Function to parse authors from XML
        :return: Author of Person type.
        """
        authors_in_header = self.soup.analytic.find_all('author')

        result = []
        for author in authors_in_header:
            persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            person = Person(firstname, middlename, surname)
            result.append(person)
        return result

    @property
    def text(self):
        """
        Function to parse the pain text from the XML file. Not Reference and Not Appendix.
        :return:
        """
        if not self._text:
            divs_text = []
            for div in self.soup.body.find_all("div"):
                # div is neither an appendix nor references, just plain text.
                if not div.get("type"):
                    div_text = div.get_text(separator=' ', strip=True)
                    divs_text.append(div_text)

            plain_text = " ".join(divs_text)
            self._text = plain_text
        return self._text

    @property
    def refstring(self):
        result = self.text
        return result

    @property
    def parastring(self):
        result = self.text
        return result


def read_tei(tei_file):
    with open(tei_file, 'r') as tei:
        soup = BeautifulSoup(tei, 'lxml')
        return soup

def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default

def basename_without_ext(path):
    base_name = basename(path)
    stem, ext = splitext(base_name)
    if stem.endswith('.tei'):
        # Return base name without tei file
        return stem[0:-4]
    else:
        return stem

def tei_to_csv_entry(tei_file):
    tei = TEIFile(tei_file)
    #print(f"Handled {tei_file}")
    base_name = basename_without_ext(tei_file)
    return base_name, tei.title, tei.abstract, tei.authors

def tei_to_csv_entry_ref(tei_file):
    tei = TEIFile(tei_file)
    base_name = basename_without_ext(tei_file)
    return base_name, tei.refstring

def tei_to_csv_entry_para(tei_file):
    tei = TEIFile(tei_file)
    base_name = basename_without_ext(tei_file)
    return base_name, tei.parastring

def parse_extracted_metadata(dir):
    papers = sorted(Path(dir).glob('*.tei.xml'))
    pool = Pool()
    csv_entries = pool.map(tei_to_csv_entry, papers)
    result_csv = pd.DataFrame(csv_entries, columns=['ID','Title', 'Abstract', 'Authors'])
    return result_csv

def parse_extracted_references(dir):
    papers = sorted(Path(dir).glob('*.tei.xml'))
    pool = Pool()
    csv_entries = pool.map(tei_to_csv_entry_ref, papers)
    result_csv = pd.DataFrame(csv_entries, columns=['ID','refstring'])
    return result_csv

def parse_extracted_paragraphs(dir):
    papers = sorted(Path(dir).glob('*.tei.xml'))
    pool = Pool()
    csv_entries = pool.map(tei_to_csv_entry_para, papers)
    result_csv = pd.DataFrame(csv_entries, columns=['ID','parastring'])
    return result_csv
