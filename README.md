# A Benchmark of PDF Information Extraction Tools using a Multi-Task and Multi-Domain Evaluation Framework
This project presents an evaluation framework which generates a benchmark of PDF (scientific articles) Information Extraction tools.
Framework provides, (1) Multi-task and Multi-Domain evaluation capability (2) Token-level evaluation metrics
(3) In-hand benchmark of ten actively maintained non-commercial open-source tools (4) In-dept analysis of the results.

## Multi-task and Multi-Domain evaluation framework
* Framework is able to evaluate 4 (MRTG) task categories, (M)etadata Extraction (title, authors, abstract), (R)eference Extraction, (T)able Extraction, (G)eneral Extraction (paragraphs, sections, figures, captions, equations, lists, or footers).
* Framework builds upon [DocBank](https://doc-analysis.github.io/docbank-page/index.html), a multi-domain dataset of 1.5M annotated content elements.
* PDF Object consolidates the ground-truth file and a source file along with page number and the path.
* Groud-truth (CSV) file is converted into a Ground-truth DataFrame.
* Extracted (JSON, XML, TXT, CSV etc.) is parsed into a Extracted DataFrame.
* Detailed flow is here
## Token-level evaluation metrics
Token-level Levenshtein ratio is computed on Ground-truth DataFrame (G) and Extracted DataFrame (E) to obtain the Similarity Matrix. Based on the threshold similarity value (0.7) we computed Precision, Recall, Accuracy and F1 Score.
### Token-level Levenshtein ratio <img src="https://render.githubusercontent.com/render/math?math={\gamma\left( {t}_{e}, {t}_{g} \right) }"> and Similarity Matrix <img src="https://render.githubusercontent.com/render/math?math={\Delta}_{m \times n}^{d}">

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

## Benchmark of ten active tools

## Analysis of the Results
