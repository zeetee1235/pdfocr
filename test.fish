#!/usr/bin/env fish
# Build the LaTeX stress-test PDF and run it through the OCR pipeline.

set -l project_dir (realpath (dirname (status -f)))
cd $project_dir

set -l tex_file test/test_document.tex
set -l pdf_file test/test_document.pdf
set -l output_dir test/output
set -l pdf_basename (basename $pdf_file .pdf)
set -l text_file "$output_dir/$pdf_basename"_extracted.txt

if not command -q pdflatex
  echo "pdflatex not found; install TeX Live/LaTeX first."
  exit 1
end

if not command -q python3
  echo "python3 not found; install Python 3 to continue."
  exit 1
end

echo "==> Building test PDF from $tex_file"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory test $tex_file; or exit $status

echo "==> Cleaning auxiliary TeX files"
rm -f test/test_document.aux test/test_document.log test/test_document.out

echo "==> Running OCR pipeline"
mkdir -p $output_dir
.venv/bin/python main.py $pdf_file -o $output_dir; or exit $status

echo ""
echo "Test finished."
echo "PDF: $pdf_file"
echo "Extracted text: $text_file"
