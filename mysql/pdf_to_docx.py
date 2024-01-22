from pdf2docx import parse

def convert_pdf2docx(input_file: str, output_file: str):
    # Converts pdf to docx
    parse(pdf_file=input_file, docx_with_path=output_file)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_pdf2docx(input_file, output_file)

