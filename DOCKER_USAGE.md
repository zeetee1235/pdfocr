# Docker Usage Guide

## Build

```bash
docker build -t pdfocr .
```

## Usage

### docker run

```bash
# Basic
docker run --rm -v "$PWD":/work -w /work pdfocr /work/document.pdf

# With options
docker run --rm -v "$PWD":/work -w /work pdfocr \
  /work/document.pdf -o /work/output --keep-images
```

### docker-compose

```bash
# Basic
docker compose run --rm pdfocr /work/document.pdf

# With options
docker compose run --rm pdfocr /work/document.pdf \
  -o /work/output --keep-images --lang kor
```

## Path Mapping

- Host: `./test/document.pdf` → Container: `/work/test/document.pdf`
- Host: `./output` → Container: `/work/output`

Use `/work/...` paths inside container.

## Options

All CLI options work in Docker:
- `-o DIR`: Output directory
- `-i DIR`: Image directory
- `-l LANG`: OCR language (default: eng+kor)
- `-d DPI`: Resolution (default: 300)
- `--keep-images`: Keep temp images
- `--merge`: Merge outputs

## Examples

```bash
# Multiple files
docker compose run --rm pdfocr /work/pdfs/*.pdf --merge

# High resolution
docker compose run --rm pdfocr /work/document.pdf --dpi 600

# Debug with images
docker compose run --rm pdfocr /work/document.pdf --keep-images -i /work/images
```

## Notes

- Output persists on host filesystem
- Default output: same directory as PDF
- Files created as root, use `sudo chown` if needed

If you encounter permission issues with files created by Docker (owned by root):

```bash
# Clean up Docker-created files
sudo rm -rf test/docker_output test/docker_images

# Or change ownership
sudo chown -R $USER:$USER test/docker_output test/docker_images
```

## Comparison with Local

Docker execution should produce identical results to local execution when using the same options:

```bash
# Run local
./test.fish

# Run Docker
./test-docker.fish

# Compare results
diff test/output/test_document_extracted.txt test/docker_output/test_document_extracted.txt
```
