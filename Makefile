# Makefile for Team Moose Jaw PDF Generation

.PHONY: setup clean-pdfs run-server migrations migrate install-deps

# LaTeX dependencies
LATEX_DEPS = texlive texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-xetex

# Django settings
PYTHON = python3
MANAGE = $(PYTHON) manage.py

# PDF generation settings
MEDIA_DIR = media
PDF_DIR = $(MEDIA_DIR)/pdfs
LATEX_DIR = pdfdocs/templates/latex

# Setup environment
setup: install-deps setup-dirs migrations migrate

# Install dependencies
install-deps:
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y $(LATEX_DEPS) python3-dev default-libmysqlclient-dev build-essential
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Create required directories
setup-dirs:
	@echo "Creating required directories..."
	mkdir -p $(PDF_DIR)
	mkdir -p $(LATEX_DIR)

# Run Django server
run-server:
	$(MANAGE) runserver

# Apply database migrations
migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

# PDF generation functions
generate-pdf:
	@if [ -z "$(TEX_FILE)" ]; then \
		echo "Error: TEX_FILE is required"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT_PDF)" ]; then \
		echo "Error: OUTPUT_PDF is required"; \
		exit 1; \
	fi
	@echo "Generating PDF from $(TEX_FILE)..."
	pdflatex -interaction=nonstopmode -output-directory=$(dir $(TEX_FILE)) $(TEX_FILE)
	@mkdir -p $(dir $(OUTPUT_PDF))
	@mv $(basename $(TEX_FILE)).pdf $(OUTPUT_PDF)
	@echo "PDF generated successfully: $(OUTPUT_PDF)"

# Clean up generated PDFs and LaTeX auxiliary files
clean-pdfs:
	@echo "Cleaning up PDF directory..."
	rm -rf $(PDF_DIR)/*
	@echo "Cleaning up LaTeX auxiliary files..."
	find . -name "*.aux" -delete
	find . -name "*.log" -delete
	find . -name "*.out" -delete

# Help command
help:
	@echo "Available commands:"
	@echo "  setup           - Install dependencies and set up the environment"
	@echo "  install-deps    - Install system and Python dependencies"
	@echo "  setup-dirs      - Create required directories"
	@echo "  run-server      - Run the Django development server"
	@echo "  migrations      - Create database migrations"
	@echo "  migrate         - Apply database migrations"
	@echo "  generate-pdf    - Generate a PDF from a LaTeX file (requires TEX_FILE and OUTPUT_PDF)"
	@echo "  clean-pdfs      - Clean up generated PDFs and auxiliary files"
	@echo "  help            - Show this help message"