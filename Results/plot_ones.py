import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# data = [[ 0.0, 0.0,  0.0, 0.81,  0.91, 0.85, 0.0,  0.0, 0.70,  0.0],
#         [ 0.0, 0.0,  0.0, 0.72,  0.82, 0.16, 0.0,  0.0, 0.81,  0.0],
#         [ 0.0, 0.0,  0.0, 0.44,  0.52, 0.13, 0.0,  0.0, 0.52,  0.0],
#         [ 0.0, 0.0,  0.0, 0.74,  0.79, 0.33, 0.0,  0.49, 0.50,  0.0],
#         [0.47, 0.0,  0.30, 0.0,  0.23, 0.0, 0.0,  0.0, 0.0,  0.28],
#         [ 0.74, 0.52,  0.0, 0.90,  0.90, 0.85, 0.51,  0.0, 0.76,  0.0],
#         [ 0.0, 0.0,  0.0, 0.35,  0.74, 0.16, 0.0,  0.0, 0.49,  0.0],
#         [ 0.0, 0.0,  0.0, 0.0,  0.49, 0.44, 0.0,  0.0, 0.0,  0.0],
#         [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         [0.0, 0.0, 0.0, 0.0, 0.0, 0.20, 0.0, 0.0, 0.0, 0.0],
#         [0.0, 0.0, 0.0, 0.0, 0.20, 0.20, 0.0, 0.0, 0.0, 0.0]]

# data = [ [0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0],
#          [0.0, 0.0, 0.0, 0.0, 0.20, 0.0, 0.0],
#          [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#          [0.0, 0.0, 0.0, 0.49, 0.45, 0.0, 0.0],
#          [0.0, 0.0, 0.35, 0.74, 0.16, 0.0, 0.49],
#          [ 0.74, 0.52, 0.85,  0.90, 0.85, 0.51,  0.76]
#         ]

data = [[0.74, 0.79, 0.15, 0.49, 0.49]]

#columns = ('Adobe Extract', 'Apache Tika', 'Camelot', 'CERMINE', 'Grobid', 'PdfAct', 'PyMuPDF', 'RefExtract', 'Science Parse', 'Tabula')
columns = ('CERMINE', 'Grobid','PdfAct', 'Science Parse', 'RefExtract')

#rows = ['%s' % x for x in ('Title', 'Abstract', 'Authors', 'Reference', 'Table', 'Paragraph', 'Section', 'Caption', 'List', 'Footer', 'Equation')]
rows = ['%s' % x for x in ('Reference')]

# values = np.arange(0.0, 3.0 , 0.1)
# value_increment = 1.0

# Get some pastel shades for the colors
colors = plt.cm.BuPu(np.linspace(0.3, 0.6, len(rows)))
n_rows = len(data)

index = np.arange(len(columns)) + 0.3
bar_width = 0.4

y_offset = np.zeros(len(columns))

# Plot bars and create text labels for the table
cell_text = []
for row in range(n_rows):
    plt.bar(index, data[row], bar_width, bottom=y_offset, color=colors[row])
    y_offset = y_offset + data[row]
    cell_text.append(['%.2f' % x for x in data[row]])

# Reverse colors and text labels to display the last value at the top.
colors = colors[::-1]
cell_text.reverse()

# Add a table at the bottom of the axes
the_table = plt.table(cellText=cell_text,
                      rowLabels=['Reference'],
                      rowColours=colors[6:],
                      colLabels=columns,
                      loc='bottom')
the_table.auto_set_font_size(False)
the_table.set_fontsize(5.5)

cells = the_table.properties()["celld"]

col=5
rows=1
for i in range(0,col):
    for j in range(0,rows):
        cells[1, i].set_text_props(ha="center")

# Adjust layout to make room for the table:
plt.subplots_adjust(left=0.25, bottom=0.25)

plt.ylabel("F1 Score")
plt.ylim(0.0,1.0)
#plt.yticks(values  * value_increment, ['%.1f' % val for val in values], fontsize=7)
plt.xticks([])
plt.title('Reference Extraction')
plt.savefig('reference.png', dpi=300)
plt.show()