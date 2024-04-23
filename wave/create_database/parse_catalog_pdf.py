import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LTTextContainer, LAParams
from pdfminer.image import ImageWriter

def pdf_to_txt(outfile='tmp_pdf2txt.txt', infile='tmp_2023-2024-catalog-courses.pdf', 
               pages='', maxpages=0, password=b'', debug=0 ):

    # input option
    pagenos = set()
    if pages != '':
        pagenos.update( int(x)-1 for x in pages.split(',') )
    imagewriter = None
    rotation = 0
    stripcontrol = False
    layoutmode = 'normal'
    encoding = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    laparams = LAParams()
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    outfp = open(outfile, 'w', encoding=encoding)
    device = TextConverter(rsrcmgr, outfp, laparams=laparams, imagewriter=None)
    with open(infile, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            interpreter.process_page(page)
    device.close()
    outfp.close()
    return

pdf_to_txt()
