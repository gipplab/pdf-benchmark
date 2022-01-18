import os
import pathlib

import pandas as pd
from science_parse_api.api import parse_pdf
from tqdm import tqdm

from PdfAct.pdfact_extract import load_data, crop_pdf, compute_metrics


def get_refstring(reflist):
    refs=[]
    if len(reflist) == 0:
        return refs
    else:
        for ref in reflist:
            if len(ref.get('authors')) != 0:
                authors = ' '.join(ref.get('authors'))
                reststr=' '.join(list(map(str, list(ref.values())[1:])))
                refstring = authors + reststr
                refs.append(refstring)
            else:
                reststr=' '.join(list(map(str, list(ref.values())[0:])))
                refs.append(reststr)
        return refs
def get_sectstr(sectlist, label):
    if len(sectlist) == 0:
        return "NONE"
    else:
        sectstr=""
        for sect in sectlist:
            if label == 'heading':
                if 'heading' in sect:
                    sectstr = sectstr + " " + sect.get('heading')
                else:
                    continue
            if label == 'text':
                if 'text' in sect:
                    sectstr = sectstr + os.linesep + sect.get('text')
                else:
                    continue
        return sectstr


def extract_scienceparse(dir):
    host = 'https://science-parser.pads.fim.uni-passau.de'
    #port = '8080'
    #label_array=['author','title', 'abstract','section','reference', 'paragraph']
    label_array=['reference']
    resultdata=[]
    for label in label_array:
        PDFlist=load_data(dir, label)
        for pdf in tqdm(PDFlist):
            pdfpath=pathlib.Path(pdf.filepath + os.sep + pdf.pdf_name)
            page = int(pdf.page_number) - 1
            croppedfile=crop_pdf(pdf.filepath, pdf.pdf_name, str(page))
            if isinstance(croppedfile, type(None)):
                continue
            croppedfilepath=pathlib.Path(croppedfile)

            outputfile = pdf.filepath + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0] + "_extracted_" + label + ".txt"

            if label == 'title':
                output_dict = parse_pdf(host, pdfpath)
                if isinstance(output_dict, type(None)):
                    continue
                with open(outputfile, "w") as text_file:
                    print(output_dict.get('title'), file=text_file)
                os.remove(croppedfile)
            elif label == 'abstract':
                output_dict = parse_pdf(host, pdfpath)
                if isinstance(output_dict, type(None)):
                    continue
                with open(outputfile, "w") as text_file:
                    print(output_dict.get('abstractText'), file=text_file)
                os.remove(croppedfile)
            elif label == 'author':
                output_dict = parse_pdf(host, pdfpath)
                if isinstance(output_dict, type(None)):
                    continue
                authlist=output_dict.get('authors')
                if len(authlist) == 0:
                    break
                with open(outputfile, "w") as text_file:
                    for auth in authlist:
                        print(auth.get('name'), file=text_file)
                os.remove(croppedfile)
            elif label == 'reference':
                output_dict = parse_pdf(host, croppedfilepath)
                if isinstance(output_dict, type(None)):
                    continue
                reflist=output_dict.get('references')
                refstring=get_refstring(reflist)
                with open(outputfile, "w") as text_file:
                    print(refstring, file=text_file)
                os.remove(croppedfile)
            elif label == 'section':
                croppedfile = crop_pdf(pdf.filepath, pdf.pdf_name, pdf.page_number)
                croppedfilepath = pathlib.Path(croppedfile)
                output_dict = parse_pdf(host, croppedfilepath)
                if isinstance(output_dict, type(None)):
                    continue
                sectlist=output_dict.get('sections')
                sectstr=get_sectstr(sectlist, 'heading')
                if sectstr == "" or sectstr == " ":
                    open(outputfile, 'w').close()
                else:
                    with open(outputfile, "w") as text_file:
                        print(sectstr, file=text_file)
                os.remove(croppedfile)
            elif label == 'paragraph':
                croppedfile = crop_pdf(pdf.filepath, pdf.pdf_name, pdf.page_number)
                croppedfilepath = pathlib.Path(croppedfile)
                output_dict = parse_pdf(host, croppedfilepath)

                if isinstance(output_dict, type(None)):
                    continue

                sectlist=output_dict.get('sections')
                sectstr=get_sectstr(sectlist, 'text')
                if sectstr == "" or sectstr == os.linesep:
                    open(outputfile, 'w').close()
                else:
                    with open(outputfile, "w") as text_file:
                        print(sectstr, file=text_file)
                os.remove(croppedfile)
            else:
                print('cannot process the label')

            if isinstance(outputfile, type(None)):
                continue
            if os.path.getsize(outputfile) == 0 or not os.path.isfile(outputfile):
                resultdata.append(['ScienceParse', pdf.pdf_name, pdf.page_number, label, 0,0,0, 0])
                os.remove(outputfile)
            else:
                f1,pre,recall, lavsim=compute_metrics(pdf, outputfile, label)
                resultdata.append(['ScienceParse', pdf.pdf_name, pdf.page_number, label, pre,recall,f1, lavsim])
                os.remove(outputfile)

    resultdf = pd.DataFrame(resultdata,
                            columns=['Tool', 'ID', 'Page', 'Label', 'Precision', 'Recall', 'F1', 'SpatialDist'])

    return resultdf




def main():
        resultdf=extract_scienceparse("/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/Docbank_sample")
        filename='scienceparse_extract_ref.csv'
        outputf='/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Results' + filename
        resultdf.to_csv(outputf, index=False)

if __name__ == "__main__":
    main()