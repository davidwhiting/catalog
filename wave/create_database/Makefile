PYTHON := ../venv/bin/python
default: all

# Makefile for creating UMGC database with a sequence of python files

#prestep:
# Figure out how to split pdf file 2023-2024-catalog.pdf to 2023-2024-catalog-courses.pdf

step1:
	$(PYTHON) parse_catalog_pdf.py

# output is tmp_pdf2txt.txt

step2:
	rm UMGC.db
	$(PYTHON) parse_text_create_dictionary.py

# input is tmp_pdf2txt.txt
# output is UMGC.db

step3:
	$(PYTHON) create_catalog_tables.py
	$(PYTHON) create_programs_table.py
	$(PYTHON) create_program_requirements_tables.py
	$(PYTHON) create_program_descriptions.py
	$(PYTHON) create_ge_tables.py
	$(PYTHON) create_catalog_program_suggested_sequence.py
	$(PYTHON) create_student_tables.py
	$(PYTHON) create_ui_tables.py

step3b:
	$(PYTHON) create_old_tables_to_be_updated.py
	$(PYTHON) create_sample_users_and_students.py

step4:
	$(PYTHON) create_views.py

all: step1 step2 step3 step3b step4

#	$(PYTHON) create_program_descriptions.py
