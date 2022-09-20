# A Benchmark of PDF Information Extraction Tools using a Multi-Task and Multi-Domain Evaluation Framework
This project presents an evaluation framework which generates a benchmark of PDF (scientific articles) Information Extraction tools.
The framework provides (1) Multi-task and Multi-Domain evaluation capability (2) Token-level evaluation metrics
(3) In-hand benchmark of ten actively maintained non-commercial open-source tools (4) In-dept analysis of the results.

## Multi-task and Multi-Domain evaluation framework
* Framework is able to benchmark 4 (MRTG) task categories, (M)etadata Extraction (title, authors, abstract), (R)eference Extraction, (T)able Extraction, (G)eneral Extraction (paragraphs, sections, figures, captions, equations, lists, or footers).
* Framework builds upon [DocBank](https://doc-analysis.github.io/docbank-page/index.html), a multi-domain dataset of 1.5M annotated content elements.
* PDF Object consolidates the ground-truth file and a source file along with page number and the path.
* Ground-truth (CSV) file is converted into a Ground-truth DataFrame.
* Extracted (JSON, XML, TXT, CSV etc.) is parsed into a Extracted DataFrame.
* Detailed flow and how to use wiki is [here](https://github.com/Media-Bias-Group/PDF-Information-Extraction-Benchmark/wiki)
## Token-level evaluation metrics
Token-level Levenshtein ratio is computed on Ground-truth DataFrame (G) and Extracted DataFrame (E) to obtain the Similarity Matrix. Based on the threshold similarity value (0.7) we computed Precision, Recall, Accuracy and F1 Score.

<p float="left">
<img src="https://render.githubusercontent.com/render/math?math={\gamma\left( {t}_{e}, {t}_{g} \right) } = 1 -\frac{lev_{{t}_{e},{t}_{g}}(i,j)}{\left| {t}_{e} \right| %2b \left| {t}_{g} \right|}" width="250">
<img src="https://render.githubusercontent.com/render/math?math={\Delta}_{m \times n}^{d} = {\gamma\left[ {E}_{i}^{s}, {G}_{j}^{s} \right] }_{i,j}^{m,n}" width="250">
</p>

<p float="left">
<img src="https://render.githubusercontent.com/render/math?math={P}^{d} = \frac{%23{\Delta}_{i,j}^{d} \ge 0.7}{m}" width="200">
 <img src="https://render.githubusercontent.com/render/math?math={R}^{d} = \frac{%23{\Delta}_{i,j}^{d} \ge 0.7}{n}" width="200">
 </p>
 
<p float="left">
<img src="https://render.githubusercontent.com/render/math?math={F1}^{d} = \frac{2 \times {P}^{d} \times {R}^{d}}{ {P}^{d} %2b  {R}^{d}}" width="200">
<img src="https://render.githubusercontent.com/render/math?math={A}^{d} = {\gamma\left[ {E}^{c}, {G}^{c} \right] }" width="200">
</p>

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
GROBID achieves the best results for the metadata and reference extraction tasks, followed by CERMINE and Science Parse. For table extraction, Adobe Extract outperforms other tools, even though the performance is much lower than for other content elements. All tools struggle to extract lists, footers, and equations. We conclude that more research on improving and combining tools is necessary to achieve satisfactory extraction quality for most content elements. 
More detailed numbers are presented [here](https://github.com/Media-Bias-Group/PDF-Information-Extraction-Benchmark/tree/main/Results).
