import pathlib

from science_parse_api.api import parse_pdf

output_dict = parse_pdf('https://science-parser.pads.fim.uni-passau.de', pathlib.Path('/data/pdf/247.tar_1710.11035.gz_MTforGSW_black.pdf'))
print(output_dict)
