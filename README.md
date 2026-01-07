# pdfocr

PDF to text extraction CLI tool using OCR.

## Quick Start

```bash
# Build Docker image
docker build -t pdfocr .

# Process PDF
docker compose run --rm pdfocr /work/path/to/document.pdf
```

Output: `document.txt` in same directory.

## Documentation

- [SIMPLE_USAGE.md](SIMPLE_USAGE.md) - Simplest usage guide
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Docker quick reference
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Full quick start guide
- [docs/DOCKER.md](docs/DOCKER.md) - Docker deployment guide
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture details

## Pipeline

1. PDF to Image: Convert pages to PNG (pdf2image)
2. OCR: Extract text (Tesseract OCR)
3. Output: Save as UTF-8 text file

## Local Installation

### Setup

```bash
chmod +x setup.sh
./setup.sh
```

Installs dependencies, creates virtual environment, installs packages.

### Install CLI (Optional)

```bash
./install.sh
```

Options: system-wide, user-local, or development mode.

## Docker Usage

### Basic

```bash
# Build
docker build -t pdfocr .

# Run
docker compose run --rm pdfocr /work/document.pdf
```

### With Options

```bash
# Custom output directory
docker compose run --rm pdfocr /work/document.pdf -o /work/output

# Multiple files
docker compose run --rm pdfocr /work/pdfs/*.pdf --merge

# Custom language (default: eng+kor)
docker compose run --rm pdfocr /work/document.pdf --lang kor

# Keep images for debugging
docker compose run --rm pdfocr /work/document.pdf --keep-images
```

## CLI Usage

After installation:

```bash
# Simple
pdfocr document.pdf

# Multiple files
pdfocr *.pdf --merge

# Custom output
pdfocr document.pdf -o ./output
```

# Keep images for debugging
docker compose run --rm pdfocr /work/document.pdf --keep-images -i /work/images

# All options
docker compose run --rm pdfocr \
  /work/test/test_document.pdf \
  -o /work/test/output \
  --keep-images -i /work/images \
  --lang eng+kor --dpi 300
```

**Key Points**:
- 📁 Output saves to **same directory** as PDF by default
- 📄 Creates `filename.txt` from `filename.pdf`
- 🗂️ Use `/work/...` paths inside container
- 💾 All files persist on your host filesystem

See [Docker Documentation](docs/DOCKER.md) ([한국어](docs/DOCKER.ko.md)) for detailed usage.

### 4. Usage

#### Docker (simplest, no installation):

```bash
# Just specify the PDF - output auto-saves to same directory
docker compose run --rm pdfocr /work/path/to/document.pdf

# With options
docker compose run --rm pdfocr /work/document.pdf -o /work/output --lang eng+kor
```

#### After CLI installation:

```bash
# Simple - creates document.txt in same directory
pdfocr ~/Documents/lecture.pdf

# Multiple files
pdfocr /path/to/*.pdf --merge

# Custom output directory
pdfocr document.pdf -o ./output
```

## Project Structure

```
pdfocr/
├── src/pdfocr/          # Main package
│   ├── main.py          # Pipeline entry point
│   ├── pdf_to_image.py  # PDF converter
│   ├── image_to_text.py # OCR module
│   ├── layout.py        # Layout analysis
│   └── block_ocr.py     # Block-based OCR
├── docs/                # Documentation
├── test/                # Test files
├── pdfocr               # CLI executable
├── requirements.txt     # Python dependencies
├── setup.sh             # Environment setup
└── docker-compose.yml   # Docker config
```

## Requirements

System: poppler-utils, tesseract-ocr
Python: pdf2image, pytesseract, Pillow, opencv-python

## CLI Options

```
pdfocr [OPTIONS] <PDF_FILES...>

Options:
  -o, --output-dir DIR  Output directory (default: same as PDF)
  -i, --image-dir DIR   Temporary image directory
  -l, --lang LANG       OCR language (default: eng+kor)
  -d, --dpi DPI         Image resolution (default: 300)
  --keep-images         Keep temporary images
  --merge              Merge all outputs into one file
```

## Examples

```bash
# Basic
pdfocr document.pdf

# Multiple files
pdfocr *.pdf --merge

# Custom options
pdfocr document.pdf -o ./output --dpi 600 --keep-images
```
