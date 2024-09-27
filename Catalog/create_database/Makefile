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
.PHONY: all old clean old_step0 old_step1 old_step2 steps012 step3 step4 step5 step6

# Default target
default: all

# Steps

####################### BEGIN ORIGINAL VERSION #######################

# Split pdf file 2023-2024-catalog.pdf to 2023-2024-catalog-courses.pdf
old_step0:
	$(PYTHON) extract_pdf_pages.py

# output is $(TMP_TXT_FILE)
old_step1:
	$(PYTHON) parse_catalog_pdf.py

old_step2:
	@echo "Removing existing database file..."
	rm -f $(DB_FILE)
	$(PYTHON) parse_text_create_dictionary.py
	rm $(TMP_TXT_FILE)
# input is tmp_pdf2txt.txt
# output is UMGC.db with catalog and courses tables
# remove tmp file at the end 

####################### END ORIGINAL VERSION #######################

# UMGC_base.db.bz2 contains catalog and course tables
# with Skills tables. The steps012 replaces step0, step1,
# step 2 in the original.

steps012:
	bzcat UMGC_base.db.bz2 > UMGC.db

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

step6:
	$(PYTHON) populate_class_difficulty.py

copy:
	cp $(DB_FILE) ../src/

# Clean up intermediate and output files
clean:
	rm -f $(DB_FILE) $(TMP_TXT_FILE) $(TMP_PDF_FILE)

# Aggregate all steps
old: step0 step1 step2 step3 step4 step5
all: steps012 step3 step4 step5 step6 copy

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
