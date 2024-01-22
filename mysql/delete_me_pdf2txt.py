
# Adapted from pdf2txt.py utility function

import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter

# main
input_pdf = '2023-2024-catalog-courses.pdf'
output_txt = 'test-extraction.txt'


def pdf2txt(infile=input_pdf, outfile=output_txt, maxpages=0, pages='', debug=0, password=b''):

    # input option
    pagenos = set()
    if pages != '':
        pagenos.update( int(x)-1 for x in pages.split(',') )

    # output option
    outtype = 'text'
    imagewriter = None
    rotation = 0
    stripcontrol = False
    layoutmode = 'normal'
    encoding = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    laparams = None

    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFPageInterpreter.debug = debug

    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
    if outfile:
        outfp = open(outfile, 'w', encoding=encoding)
    else:
        outfp = sys.stdout

    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, laparams=laparams,
                               imagewriter=imagewriter)

    fname = infile

    with open(fname, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
    device.close()
    outfp.close()
    return

input_pdf = '2023-2024-catalog-courses.pdf'
output_txt = 'test-extraction.txt'

pdf2txt(infile=input_pdf, outfile=output_txt)
