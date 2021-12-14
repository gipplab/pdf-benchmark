import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import pandas as pd

def add_value_labels(ax, spacing=5):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """

    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'

        # If value of bar is negative: Place label below bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertically align label at top
            va = 'top'

        # Use Y value as label and format number with one decimal place
        label = "{:.2f}".format(y_value)

        # Create annotation
        ax.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(0, space),          # Vertically shift label by `space`
            textcoords="offset points", # Interpret `xytext` as offset in points
            ha='center',
            fontsize=15,                # Horizontally center label
            va=va)                      # Vertically align label differently for
                                        # positive and negative values.

tools = ['Adobe Extract','Apache Tika', 'CERMINE', 'Grobid', 'PdfAct', 'PyMuPDF', 'Science Parse']
para = [0.74, 0.52, 0.90, 0.90, 0.85, 0.51, 0.76]
abstract = [0.72,0.82,0.16,0.81]
author=[0.44,0.52,0.13,0.52]

title_series=pd.Series(para)

plt.figure(figsize=(12, 12))
ax = title_series.plot(kind="bar",color='black')
ax.set_ylim([0.0,1.0])
ax.set_title("Paragraph Extract", fontsize=20)
ax.set_ylabel("F1 Score", fontsize=15)
ax.set_xticklabels(tools, rotation=45, ha='center')
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)

add_value_labels(ax)
plt.savefig('paragraph.png', dpi='figure')

plt.show()