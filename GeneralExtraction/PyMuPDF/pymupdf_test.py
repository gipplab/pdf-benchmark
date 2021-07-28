import fitz
pdf_path="/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/Data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf"
doc = fitz.open(pdf_path)
page = doc.loadPage(0)
text = page.getText("text")
metadata=doc.metadata
print(metadata)