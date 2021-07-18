import pandas as pd
from grobid_client.grobid_client import GrobidClient

# client = GrobidClient(config_path="./config.json")
# client.process("processHeaderDocument","/home/apurv/Thesis/PoC/PDF_Extraction_Benchmarking/Data/pdf", n=20)

from similarity.jarowinkler import JaroWinkler

