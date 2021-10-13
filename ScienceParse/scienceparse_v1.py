import os
import pathlib

from science_parse_api.api import parse_pdf

from PdfAct.pdfact_extract import load_data, crop_pdf, compute_metrics


def get_refstring(reflist):
    if len(reflist) == 0:
        return "NONE"
    else:
        for ref in reflist:
            if len(ref.get('authors')) != 0:
                authors = ' '.join(ref.get('authors'))
                refstring = authors + " " + ref.get('title') + " " + ref.get('venue') + " " + str(ref.get('year'))
                return refstring
            else:
                refstring = ref.get('title') + " " + ref.get('venue') + " " + str(ref.get('year'))
                return refstring
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
    host = 'http://127.0.0.1'
    port = '8080'
    #label_array=['author','title', 'abstract','section','reference', 'paragraph']
    label_array=['reference']
    for label in label_array:
        PDFlist=load_data(dir, label)
        for pdf in PDFlist:
            print(pdf.pdf_name, label)

            pdfpath=pathlib.Path(pdf.filepath + os.sep + pdf.pdf_name)
            page = int(pdf.page_number) - 1
            croppedfile=crop_pdf(pdf.filepath, pdf.pdf_name, str(page))
            croppedfilepath=pathlib.Path(croppedfile)

            outputfile = pdf.filepath + os.sep + os.path.splitext(os.path.basename(pdf.pdf_name))[0] + "_extracted_" + label + ".txt"

            if label == 'title':
                output_dict = parse_pdf(host, pdfpath ,port=port)
                with open(outputfile, "w") as text_file:
                    print(output_dict.get('title'), file=text_file)
                os.remove(croppedfile)
            elif label == 'abstract':
                output_dict = parse_pdf(host, pdfpath, port=port)
                with open(outputfile, "w") as text_file:
                    print(output_dict.get('abstractText'), file=text_file)
                os.remove(croppedfile)
            elif label == 'author':
                output_dict = parse_pdf(host, pdfpath, port=port)
                authlist=output_dict.get('authors')
                if len(authlist) == 0:
                    break
                with open(outputfile, "w") as text_file:
                    for auth in authlist:
                        print(auth.get('name'), file=text_file)
                os.remove(croppedfile)
            elif label == 'reference':
                output_dict = parse_pdf(host, croppedfilepath, port=port)
                reflist=output_dict.get('references')
                refstring=get_refstring(reflist)
                with open(outputfile, "w") as text_file:
                    print(refstring, file=text_file)
                os.remove(croppedfile)
            elif label == 'section':
                croppedfile = crop_pdf(pdf.filepath, pdf.pdf_name, pdf.page_number)
                croppedfilepath = pathlib.Path(croppedfile)
                output_dict = parse_pdf(host, croppedfilepath, port=port)
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
                output_dict = parse_pdf(host, croppedfilepath, port=port)
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

            if os.path.getsize(outputfile) == 0 or not os.path.isfile(outputfile):
                print("0,0,0,0")
                os.remove(outputfile)
            else:
                f1,pre,recall, lavsim=compute_metrics(pdf, outputfile, label)
                os.remove(outputfile)
                print(f1,pre, recall, lavsim)





def main():
    extract_scienceparse("/home/apurv/Thesis/DocBank/DocBank_samples/DocBank_samples")

if __name__ == "__main__":
    main()