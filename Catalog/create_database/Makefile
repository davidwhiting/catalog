# Makefile for UMGC Database Creation

# Variables
VENV_PATH := ../.venv  # Default virtual environment path
#PYTHON := $(VENV_PATH)/bin/python
PYTHON := ../.venv/bin/python
PDF_FILE := 2023-2024-catalog.pdf
DB_FILE := UMGC.db
#TMP_PDF_FILE := tmp_$(PDF_FILE)
TMP_PDF_FILE := tmp_2023-2024-catalog-courses.pdf
TMP_TXT_FILE := tmp_pdf2txt.txt

# Phony targets
.PHONY: all clean step0 step1 step2 step3 step4 step5

# Default target
default: all

# Steps

# Split pdf file 2023-2024-catalog.pdf to 2023-2024-catalog-courses.pdf
step0:
	$(PYTHON) extract_pdf_pages.py

# output is $(TMP_TXT_FILE)
step1:
	$(PYTHON) parse_catalog_pdf.py

step2:
	@echo "Removing existing database file..."
	rm -f $(DB_FILE)
	$(PYTHON) parse_text_create_dictionary.py
	rm $(TMP_TXT_FILE)

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

step4:
	$(PYTHON) create_views.py

step5:
	$(PYTHON) populate_sample_users_and_students.py

# Clean up intermediate and output files
clean:
	rm -f $(DB_FILE) $(TMP_TXT_FILE) $(TMP_PDF_FILE)

# Aggregate all steps
all: step0 step1 step2 step3 step4 step5

#
## input is tmp_pdf2txt.txt
## output is UMGC.db with catalog and courses tables
## remove tmp file at the end 
#
###################################################3
#
### To Do items:
##
## create_program_courses to do:
## 	- add Undergrad Minors
##   - add Masters
##   - add Ph.D.
##   - add Grad Certificates
##
## create_program_descriptions to do:
##   - add Associate
##   - add Masters
##   - add Ph.D.
##   - add Grad Certificates



