import pandas as pd
import pytesseract
from pytesseract import Output
import cv2

img = cv2.imread('//Data/boundingboxtest/output/table_areas_0_ori.jpg')
d = pytesseract.image_to_data(img, output_type=Output.DICT)

df = pd.DataFrame(d)
df = df.drop(['level','page_num','block_num','par_num','line_num','word_num','conf'], axis=1)
xwidth=df['left'] + df['width']
ytop=df['top'] + df['height']
df['xwidth'] = xwidth
df['ytop'] = ytop
df.to_csv('bbox.csv', index=False)

#with open('bbox.csv','w') as f:
 #   w = csv.writer(f)
  #  w.writerows(d)