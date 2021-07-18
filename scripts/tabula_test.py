import tabula
import camelot

tables = tabula.read_pdf('/Data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf', stream=True, pages='3')
print(tables)

tablesc = camelot.read_pdf('/Data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf', flavor='stream', pages='3')
df=tablesc[0].df
print(df)