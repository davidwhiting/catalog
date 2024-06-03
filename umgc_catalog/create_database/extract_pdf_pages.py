import sys
from PyPDF2 import PdfReader, PdfWriter

def extract_pages(input_pdf, output_pdf, start_page, end_page):
    # Open the pdf file
    reader = PdfReader(input_pdf)

    # Create a pdf writer object
    writer = PdfWriter()

    # Add pages in the range to the writer object
    for i in range(start_page-1, end_page):
        page = reader.pages[i]
        writer.add_page(page)

    # Write the pages to a new file
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

# Call the function
extract_pages('2023-2024-catalog.pdf', 'tmp_2023-2024-catalog-courses.pdf', 201, 326)
