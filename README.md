# PDF2TXT - PDF 텍스트 추출 CLI 도구

어디서든 사용 가능한 PDF → 이미지 → 텍스트 변환 명령줄 도구입니다.  
수업 자료 PDF를 텍스트로 변환하여 LaTeX 문서 작성을 위한 전처리를 수행합니다.

**CLI 명령어**: `pdfocr`

## 📋 개요

**PDF → 이미지 → 텍스트** 파이프라인을 통해 PDF 문서에서 텍스트를 추출합니다.

### 처리 과정
1. **PDF → 이미지 변환**: pdf2image를 사용하여 페이지별로 PNG 이미지 생성
2. **OCR 텍스트 추출**: pytesseract를 사용하여 한국어 텍스트 인식
3. **텍스트 파일 저장**: UTF-8 인코딩으로 페이지별 구분된 텍스트 파일 생성

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd /home/dev/pdf2txt

# 실행 권한 부여
chmod +x setup.sh

# 설치 스크립트 실행
./setup.sh
```

설치 스크립트는 다음을 자동으로 수행합니다:
- 시스템 의존성 설치 (poppler, tesseract)
- Python 가상환경 생성
- Python 패키지 설치
- 작업 디렉토리 생성

### 2. CLI 도구 설치 (선택사항)

어디서든 `pdfocr` 명령어를 사용하려면:

```bash
./install.sh
```

설치 옵션:
- **시스템 전역 설치** (`/usr/local/bin`) - 모든 사용자가 사용 가능
- **사용자 로컬 설치** (`~/.local/bin`) - 현재 사용자만 사용 가능
- **개발 모드** - 심볼릭 링크만 생성

### 3. 사용하기

#### CLI 도구로 설치한 경우:

```bash
# 어디서든 사용 가능!
pdfocr ~/Documents/lecture.pdf
pdfocr /path/to/any/document.pdf
pdfocr ../other-project/pdfs/*.pdf --merge
```

#### 직접 실행하는 경우:

```bash
# 가상환경 활성화
source venv/bin/activate

# Python 스크립트 실행
python main.py ~/Documents/lecture.pdf
```

## 📁 프로젝트 구조

```
pdf2txt/
├── pdfocr                  # CLI 실행 파일 (심볼릭 링크 생성용)
├── main.py                 # 전체 파이프라인 실행 (진입점)
├── pdf_to_image.py         # PDF → 이미지 변환 모듈
├── image_to_text.py        # 이미지 → 텍스트 추출 모듈
├── requirements.txt        # Python 패키지 의존성
├── setup.sh               # 환경 설정 스크립트
├── install.sh             # CLI 도구 설치 스크립트
├── README.md              # 프로젝트 문서
└── .gitignore             # Git 제외 파일
```

## 🔧 시스템 요구사항

### 필수 시스템 패키지
- **poppler-utils**: PDF를 이미지로 변환
- **tesseract-ocr**: OCR 엔진
- **tesseract-ocr-kor**: 한국어 언어팩

### Python 패키지
- `pdf2image==1.16.3`: PDF → 이미지 변환
- `pytesseract==0.3.10`: Tesseract OCR Python 래퍼
- `Pillow==10.1.0`: 이미지 처리

## 📖 사용법

### 기본 사용

```bash
# CLI 도구로 설치한 경우
pdfocr <PDF파일>

# 또는 직접 실행
python main.py <PDF파일>
```

### 다양한 위치의 PDF 처리

```bash
# 현재 디렉토리의 PDF
pdfocr document.pdf

# 상위 디렉토리의 PDF
pdfocr ../lecture.pdf

# 다른 프로젝트의 PDF
pdfocr ../other-project/materials/lecture.pdf

# 홈 디렉토리의 PDF
pdfocr ~/Documents/study/chapter1.pdf

# 여러 디렉토리의 PDF를 한번에
pdfocr ~/pdfs/lec1.pdf ../docs/lec2.pdf ./lec3.pdf --merge

# 절대 경로 사용
pdfocr /home/user/important/document.pdf
```

### 고급 옵션

```bash
pdfocr [옵션] <PDF파일들...>

옵션:
  -h, --help            도움말 표시
  -o, --output-dir DIR  텍스트 출력 디렉토리 (기본값: PDF와 같은 디렉토리)
  -i, --image-dir DIR   임시 이미지 디렉토리 (기본값: 자동 생성)
  -l, --lang LANG       OCR 언어 코드 (기본값: kor)
  -d, --dpi DPI         이미지 해상도 (기본값: 300)
  --keep-images         처리 후 이미지 보존
  --merge              모든 텍스트를 하나의 파일로 병합
```

### 사용 예시

```bash
# 상위 디렉토리의 PDF 처리
pdfocr ../lectures/week1.pdf

# 출력 디렉토리 지정
pdfocr ~/Documents/lecture.pdf -o ~/output

# 고해상도로 변환 (더 정확한 OCR)
pdfocr document.pdf --dpi 600

# 이미지 파일 보존 (디버깅용)
pdfocr lecture.pdf --keep-images -i ./temp_images

# 영어 문서 처리
pdfocr document.pdf --lang eng

# 여러 디렉토리의 PDF를 하나의 텍스트로 병합
pdfocr ../project1/doc.pdf ../project2/doc.pdf --merge -o ~/merged

# 다른 프로젝트의 모든 PDF 처리
pdfocr ../course-materials/pdfs/*.pdf --merge -o ~/summary
```

### 실제 사용 시나리오

#### 시나리오 1: 여러 과목의 강의 자료 처리

```bash
# 디렉토리 구조:
# ~/courses/
#   ├── math/lecture1.pdf, lecture2.pdf
#   ├── physics/chapter1.pdf, chapter2.pdf
#   └── chemistry/notes.pdf

# 수학 강의 전체 처리
pdfocr ~/courses/math/*.pdf --merge -o ~/notes/math

# 물리 강의 전체 처리
pdfocr ~/courses/physics/*.pdf --merge -o ~/notes/physics

# 모든 과목 한번에 처리
pdfocr ~/courses/*/*.pdf --merge -o ~/notes/all_subjects
```

#### 시나리오 2: 프로젝트 외부 문서 처리

```bash
# 현재 위치: /home/dev/pdf2txt
# 처리할 PDF: /home/dev/documents/report.pdf

# 어디서든 실행 가능
pdfocr /home/dev/documents/report.pdf

# 출력 파일: /home/dev/documents/report_extracted.txt (PDF와 같은 디렉토리)
```

## 🔍 개별 모듈 사용

### PDF → 이미지 변환만 수행

```bash
python pdf_to_image.py <PDF파일>
```

### 이미지 → 텍스트 추출만 수행

```bash
python image_to_text.py <이미지디렉토리>
```

## 📝 출력 형식

생성되는 텍스트 파일은 다음 형식을 따릅니다:

```
================================================================================
페이지 1: lecture_page_001.png
================================================================================

[페이지 1의 추출된 텍스트 내용]


================================================================================
페이지 2: lecture_page_002.png
================================================================================

[페이지 2의 추출된 텍스트 내용]

...
```

## 🐛 문제 해결

### Tesseract를 찾을 수 없음

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-kor

# Fedora/RHEL/CentOS
sudo dnf install tesseract tesseract-langpack-kor

# macOS
brew install tesseract tesseract-lang
```

### pdftoppm을 찾을 수 없음

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# Fedora/RHEL/CentOS
sudo dnf install poppler-utils

# macOS
brew install poppler
```

### 한국어 인식이 안 됨

```bash
# 한국어 언어팩 설치 확인
tesseract --list-langs

# 'kor'이 목록에 없다면 설치
sudo apt-get install tesseract-ocr-kor      # Ubuntu/Debian
sudo dnf install tesseract-langpack-kor     # Fedora/RHEL/CentOS
```

### Python 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

## 💡 팁

1. **고품질 OCR**: `--dpi 600` 옵션으로 더 높은 해상도 사용
2. **빠른 처리**: 기본값 300 DPI로도 대부분의 문서에서 충분
3. **디버깅**: `--keep-images` 옵션으로 이미지 확인 가능
4. **대량 처리**: `--merge` 옵션으로 여러 파일을 하나로 통합

## 🎯 다음 단계: LaTeX 변환

추출된 텍스트를 LaTeX 문서로 변환하려면:

1. `output/` 디렉토리의 텍스트 파일 검토
2. 필요에 따라 수동 편집 및 정리
3. LaTeX 템플릿에 내용 삽입

LaTeX 변환 스크립트 예시:

```python
# 추후 구현 예정
# text_to_latex.py - 텍스트를 LaTeX 형식으로 변환
```

## 📄 라이선스

이 프로젝트는 교육 목적으로 만들어졌습니다.

## 🤝 기여

버그 리포트나 개선 사항은 이슈로 등록해주세요.
