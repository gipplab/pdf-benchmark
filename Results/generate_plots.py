import numpy as np
import matplotlib.pyplot as plt

# data to plot
n_groups = 6
para = (0.78, 0.52, 0.88, 0.91, 0.96,0.56)
section = (0.0, 0.0, 0.8, 0.88, 0.74,0.0)
# abstract = (0.83, 0.92, 0.20, 0.68)
# author = (0.81, 0.97, 0.21, 0.7)

# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.25
opacity = 0.8

rects1 = plt.bar(index, para, bar_width,
alpha=opacity,
color='b',
label='Paragraph')

rects2 = plt.bar(index + bar_width, section, bar_width,
alpha=opacity,
color='g',
label='Section')

# rects3 = plt.bar(index + bar_width + bar_width, author, bar_width,
# alpha=opacity,
# color='r',
# label='Author')

plt.xlabel('System')
plt.ylabel('F1 Scores')
plt.title('General Extraction')
plt.xticks(index + bar_width, ('Adobe Extract','Apache Tika','CERMINE', 'GROBID', 'PdfAct', 'PyMuPDF'))
plt.legend(loc="best")

plt.tight_layout()
plt.show()
plt.savefig('generalex.png')