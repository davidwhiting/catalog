PYTHON := ../.venv/bin/python
default: all

# Makefile for creating UMGC database with a sequence of python files

# Split pdf file 2023-2024-catalog.pdf to tmp_2023-2024-catalog-courses.pdf
step0:
	$(PYTHON) extract_pdf_pages.py

step1:
	$(PYTHON) parse_catalog_pdf.py

# output is tmp_pdf2txt.txt

step2:
	rm -f UMGC.db
	$(PYTHON) parse_text_create_dictionary.py
	rm tmp_pdf2txt.txt

# input is tmp_pdf2txt.txt
# output is UMGC.db with catalog and courses tables
# remove tmp file at the end 

##################################################3

## To Do items:
#
# create_program_courses to do:
# 	- add Undergrad Minors
#   - add Masters
#   - add Ph.D.
#   - add Grad Certificates
#
# create_program_descriptions to do:
#   - add Associate
#   - add Masters
#   - add Ph.D.
#   - add Grad Certificates

step3:
	$(PYTHON) create_catalog_tables.py
	$(PYTHON) create_programs_table.py
	$(PYTHON) create_program_requirements_undergrad_major.py
	$(PYTHON) create_program_courses.py
	$(PYTHON) create_program_descriptions.py
	$(PYTHON) create_ge_tables.py
	$(PYTHON) create_catalog_program_suggested_sequence.py
	$(PYTHON) create_user_and_student_tables.py
	$(PYTHON) create_ui_tables.py
	$(PYTHON) create_student_progress_tables.py

# Need to review and update my views in create_views.py

step4:
	$(PYTHON) create_views.py

step5:
	$(PYTHON) populate_sample_users_and_students.py

all: step0 step1 step2 step3 step4 step5
