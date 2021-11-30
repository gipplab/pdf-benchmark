import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

objects = ('Adobe Extract', 'PdfAct', 'Camelot', 'Tabula')
y_pos = np.arange(len(objects))
performance = [0.70, 0.0, 0.0, 0.0]

plt.bar(y_pos, performance, align='center', alpha=0.8, color='b')
plt.xticks(y_pos, objects)
plt.ylabel('F1 Score')
plt.xlabel('System')
plt.title('Table Extraction')

plt.show()
plt.savefig('tableex.png')