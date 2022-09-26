# A Benchmark of PDF Information Extraction Tools using a Multi-Task and Multi-Domain Evaluation Framework
This project presents an evaluation framework that generates a benchmark of PDF (scientific articles) Information Extraction tools.
The framework provides (1) Multi-task and Multi-Domain evaluation capability and (2) Token-level evaluation metrics
(3) In-hand benchmark of ten actively maintained non-commercial open-source tools (4) In-depth analysis of the results.

## Multi-task and Multi-Domain evaluation framework
* The Framework can benchmark 4 (MRTG) task categories, (M)etadata Extraction (title, authors, abstract), (R)eference Extraction, (T)able Extraction, (G)eneral Extraction (paragraphs, sections, figures, captions, equations, lists, or footers).
* The Framework builds upon [DocBank](https://doc-analysis.github.io/docbank-page/index.html), a multi-domain dataset of 1.5M annotated content elements.
* PDF Object consolidates the ground-truth file and a source file along with the page number and the path.
* Ground-truth (CSV) file is converted into a Ground-truth DataFrame.
* Extracted (JSON, XML, TXT, CSV etc.) is parsed into a Extracted DataFrame.
If you want to read more about the usage and specifics, check [here](https://github.com/Media-Bias-Group/PDF-Information-Extraction-Benchmark/blob/main/doc/home.md).
## Token-level evaluation metrics
Token-level Levenshtein ratio is computed on Ground-truth DataFrame (G) and Extracted DataFrame (E) to obtain the Similarity Matrix. Based on the threshold similarity value (0.7) we computed Precision, Recall, Accuracy, and F1 Score.

## Evaluated Tools
| Tool          | Version | Task(s)<sup>1</sup>   | Technology                   | Output         |
|---------------|---------|------------|------------------------------|----------------|
| Adobe Extract | 1.0     | T, G       | Adobe Sensei AI Framework    | JSON, XLSX     |
| Apache Tika   | 2.0.0   | G          | Apache PDFBox                | TXT            |
| Camelot       | 0.10.1  | T          | PDFMiner, OpenCV             | CSV, Dataframe |
| CERMINE       | 1.13    | M, R, G    | SVM, CRF, Rule-based, iText  | NLM JATS       |
| GROBID        | 0.7.0   | M, R, T, G | CRF, Deep Learning, Pdfalto  | TEI XML        |
| PdfAct        | n/a     | M, R, T, G | Rule-based, pdftotext        | TXT, XML, JSON |
| PyMuPDF       | 1.19.1  | G          | OCR, tesseract               | TXT            |
| RefExtract    | 0.2.5   | R          | Rule-based, pdftotext        | TXT            |
| ScienceParse  | 1.0     | M, R, G    | CRF, Rule-based, pdffigures2 | JSON           |
| Tabula        | 1.2.1   | T          | Rule-based, PDFBox           | Dataframe, CSV |

<sup>1</sup> **M**etadata, **R**eferences, **T**able, **G**eneral

## Analysis of the Results
GROBID achieves the best results for the metadata and reference extraction tasks, followed by CERMINE and Science Parse. For table extraction, Adobe Extract outperforms other tools, even though the performance is much lower than other content elements. All tools struggle to extract lists, footers, and equations. We conclude that more research on improving and combining tools is necessary to achieve satisfactory extraction quality for most content elements. 
More detailed numbers are presented in case of paper acceptance.
