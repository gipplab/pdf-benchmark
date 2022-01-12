# PDF-Information-Extraction-Benchmark

<!---
## Related Work
![Alt text](./images/rel2.svg)
<img src="./images/rel1.svg">
-->

##
<p float="left" align="center">
<img src="./images/tools.svg" width="700">
 </p>

## Evaluation Framework
<p float="left" align="center">
<img src="./images/EvaluationModel (1).jpg" width="700">
</p>

## Evaluation Metrics

### Token-level Levenshtein ratio and Similarity Matrix <img src="https://render.githubusercontent.com/render/math?math={\Delta}_{m \times n}^{D}">

<p float="left" align="center">
<img src="https://render.githubusercontent.com/render/math?math={\gamma\left( {t}_{e}, {t}_{g} \right) } = 1 -\frac{lev_{{t}_{e},{t}_{g}}(i,j)}{\left| {t}_{e} \right| + \left| {t}_{g} \right|}" width="400">
<img src="https://render.githubusercontent.com/render/math?math={\Delta}_{m \times n}^{D} = {\gamma\left[ {E}_{i}^{s}, {G}_{j}^{s} \right] }_{i,j}^{m,n}" width="400">
</p>

<p float="left" align="center">
<img src="https://render.githubusercontent.com/render/math?math={Precision}^{D} = \frac{\# {\Delta}_{i,j}^{D} \ge 0.7}{m}" width=400>

 </p>
 
<p float="left" align="center">
<img src="https://render.githubusercontent.com/render/math?math={F1 Score}^{D} = \frac{2 \times {Precision}^{D} \times {Recall}^{D}}{ {Precision}^{D} +  {Recall}^{D}}" width="400">
<img src="https://render.githubusercontent.com/render/math?math={Accuracy}^{D} = {\gamma\left[ {E}^{c}, {G}^{c} \right] }" width="400">
</p>
## Results
<p float="left" align="center">
          <img src="./images/ref (2).svg" width="400"/>
          <img src="./images/table (2).svg" width="400"/>
</p>
<p float="left" align="center">
<img src="./images/general (2).svg" width="400"/>
<img src="./images/meta (2).svg" width="400"/>
</p>

<p float="left" align="center">
<img src="./images/res1.svg" width="700">
</p>

