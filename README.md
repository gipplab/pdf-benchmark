# A Benchmark of PDF Information Extraction Tools using a Multi-Task and Multi-Domain Evaluation Framework for Academic Documents
This project provides a framework for evaluating tools to extract information from scientific PDF documents.
The framework offers (1) multi-task and multi-domain evaluation capabilities, (2) token-level evaluation metrics,
(3) a benchmark of ten actively maintained non-commercial open-source tools, (4) an in-depth analysis of the results.

## Multi-task and multi-domain evaluation framework for academic documents
* The framework covers four extraction tasks (**M**)etadata Extraction (title, authors, abstract), (**R**)eference Extraction, (**T**)able Extraction, (**G**)eneral Extraction (paragraphs, sections, figures, captions, equations, lists, or footers).
* The framework builds upon [DocBank](https://doc-analysis.github.io/docbank-page/index.html), a multi-domain dataset of 1.5M annotated content elements.
* To learn more about the framework and its usage, check [here](doc/documentation.md).

## Token-level evaluation metrics
The framework computes the token-level Levenshtein ratio between the ground-truth data frame (G) and the extracted data frame (E) to obtain the similarity matrix. Based on the threshold similarity value (0.7) we compute Precision, Recall, Accuracy, and F1-Score.

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

## Analysis of the results
GROBID achieves the best results for the metadata and reference extraction tasks, followed by CERMINE and Science Parse. For table extraction, Adobe Extract outperforms other tools, even though the performance is much lower than for other content elements. All tools struggle to extract lists, footers, and equations. We conclude that more research on improving and combining tools is necessary to achieve satisfactory extraction quality for most content elements.
