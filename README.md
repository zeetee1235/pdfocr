# pdfocr

PDF to text extraction CLI tool using OCR pipeline.

**Command**: `pdfocr`

## Overview

Extracts text from PDF documents through a **PDF → Image → Text** pipeline.

### Process
1. **PDF to Image**: Convert each page to PNG using pdf2image
2. **OCR Extraction**: Extract text using pytesseract with Tesseract OCR
3. **Text Output**: Save UTF-8 encoded text files with page markers

## Quick Start

### 1. Setup

```bash
cd /home/dev/pdfocr
chmod +x setup.sh
./setup.sh
```

The setup script automatically:
- Installs system dependencies (poppler, tesseract)
- Creates Python virtual environment
- Installs Python packages
- Creates working directories

### 2. Install CLI Tool (Optional)

To use `pdfocr` command from anywhere:

```bash
./install.sh
```

Installation options:
- **System-wide** (`/usr/local/bin`) - All users
- **User local** (`~/.local/bin`) - Current user only
- **Development mode** - Symlink only

### 3. Usage

#### After CLI installation:

```bash
pdfocr ~/Documents/lecture.pdf
pdfocr /path/to/document.pdf
pdfocr ../pdfs/*.pdf --merge
```

#### Direct execution:

```bash
source venv/bin/activate
python main.py ~/Documents/lecture.pdf
```

## Project Structure

```
pdfocr/
├── pdfocr                  # CLI executable (symlink target)
├── main.py                 # Main pipeline entry point
├── pdf_to_image.py         # PDF to image converter
├── image_to_text.py        # Image to text OCR module
├── requirements.txt        # Python dependencies
├── setup.sh               # Environment setup script
├── install.sh             # CLI installation script
├── README.md
└── .gitignore
```

## Requirements

### System Packages
- **poppler-utils**: PDF to image conversion
- **tesseract-ocr**: OCR engine
- **tesseract-langpack-kor**: Korean language pack

### Python Packages
- `pdf2image`: PDF to image conversion
- `pytesseract`: Tesseract OCR wrapper
- `Pillow`: Image processing
- `opencv-python`: Image preprocessing
- `numpy`: Numerical operations

## Usage

### Basic

```bash
pdfocr <PDF_FILE>
# or
python main.py <PDF_FILE>
```

### Multiple Files

```bash
pdfocr file1.pdf file2.pdf
pdfocr ../lectures/*.pdf
pdfocr ~/Documents/study/*.pdf --merge
```

### Options

```bash
pdfocr [OPTIONS] <PDF_FILES...>

Options:
  -h, --help            Show help message
  -o, --output-dir DIR  Output directory (default: same as PDF)
  -i, --image-dir DIR   Temporary image directory (default: auto)
  -l, --lang LANG       OCR language code (default: kor)
  -d, --dpi DPI         Image resolution (default: 300)
  --keep-images         Keep images after processing
  --merge              Merge all texts into one file
```

### Examples

```bash
# Specify output directory
pdfocr document.pdf -o ~/output

# High resolution for better OCR
pdfocr document.pdf --dpi 600

# Keep images for debugging
pdfocr lecture.pdf --keep-images -i ./temp_images

# English document
pdfocr document.pdf --lang eng

# Merge multiple PDFs
pdfocr file1.pdf file2.pdf file3.pdf --merge -o ~/merged
```

## Output Format

Generated text files follow this format:

```
================================================================================
Page 1: document_page_001.png
================================================================================

[Extracted text from page 1]


================================================================================
Page 2: document_page_002.png
================================================================================

[Extracted text from page 2]

...
```

## Troubleshooting

### Tesseract not found

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-kor

# Fedora/RHEL
sudo dnf install tesseract tesseract-langpack-kor

# macOS
brew install tesseract tesseract-lang
```

### pdftoppm not found

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# Fedora/RHEL
sudo dnf install poppler-utils

# macOS
brew install poppler
```

### Korean language not working

```bash
# Check installed languages
tesseract --list-langs

# If 'kor' is missing, install it
sudo apt-get install tesseract-ocr-kor      # Ubuntu/Debian
sudo dnf install tesseract-langpack-kor     # Fedora/RHEL
```

### Python 3.13 compatibility

If you encounter Pillow build errors on Python 3.13:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

The `requirements.txt` uses Pillow >= 11.0.0 which supports Python 3.13.
