import cv2
import pytesseract

file = '//Utility_Scripts/247.tar_1710.11035.gz_MTforGSW_2_ori.jpg'

img = cv2.imread(file)
h, w, _ = img.shape

boxes = pytesseract.image_to_boxes(img)

for b in boxes.splitlines():
    b = b.split(' ')
    img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (250, 150, 50), 2)

cv2.imshow('test.png', img)
cv2.waitKey(0)