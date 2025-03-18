# PDF Document Management System

This Django app provides functionality for generating, signing, and managing PDF documents using LaTeX templates and Makefile automation.

## Features

- **Document Generation**: Create PDF documents from LaTeX templates
- **Digital Signatures**: Add digital signatures to documents with user authentication
- **Document Management**: View, share, and track documents
- **Template Management**: Create and edit LaTeX templates for document generation

## Requirements

### System Requirements

- LaTeX installation (texlive, texlive-latex-extra, texlive-fonts-recommended, texlive-fonts-extra)
- Make utility
- Python 3.8+
- Django 5.0+

### Python Dependencies

- Django
- ReportLab (PDF generation)
- PyPDF2 (PDF manipulation)
- Pillow (Image processing)

## Setup

1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install texlive texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-xetex
   ```

2. Set up the Django app:
   ```bash
   # Create required directories
   mkdir -p media/pdfs
   
   # Apply migrations
   python manage.py makemigrations pdfdocs
   python manage.py migrate
   ```

3. Create a LaTeX template in the admin interface or use the provided default template.

## Usage

### Using the Makefile

The project includes a Makefile with various commands for PDF generation:

```bash
# Generate a PDF from a LaTeX file
make generate-pdf TEX_FILE=/path/to/document.tex OUTPUT_PDF=/path/to/output.pdf

# Clean up generated PDFs and auxiliary files
make clean-pdfs

# See all available commands
make help
```

### Security Features

The PDF documents include security features:

- QR code verification
- Timestamped digital signatures
- User authentication for document signing
- Audit trail of document access and modifications

## Implementation Details

### LaTeX Templates

LaTeX templates use placeholder variables that are replaced at generation time:

- `{{document_id}}` - Unique document identifier
- `{{document_title}}` - Document title
- `{{user_name}}` - Name of the creating user
- `{{user_email}}` - Email of the creating user
- `{{generation_date}}` - Date of document generation
- `{{custom_text}}` - Custom content specific to the document

### Digital Signatures

Digital signatures are implemented using:

1. User authentication to verify identity
2. Canvas signature capture in browser
3. Signature storage in the database
4. Cryptographic verification of document integrity

## License

This component is part of the Team Moose Jaw project and is subject to the same license terms as the overall project.