from refextract import extract_journal_reference, extract_references_from_file

#references = extract_references_from_file('/home/apurv/Thesis/PDF-Information-Extraction-Benchmark/Data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf')
#print(references[0])

reference = extract_journal_reference('Bahdanau, D., Cho, K., and Bengio, Y. (2014). Neural ma-\
chine translation by jointly learning to align and trans-\
late. arXiv preprint arXiv:1409.0473.')
print(reference)