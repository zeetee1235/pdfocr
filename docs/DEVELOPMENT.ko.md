# 개발 가이드

## 개발 환경 설정

### 1. 저장소 클론
```bash
git clone https://github.com/zeetee1235/pdfocr.git
cd pdfocr
```

### 2. 시스템 의존성 설치
```bash
./setup.sh
```

Fedora/RHEL에서 다음을 설치합니다:
- poppler-utils
- tesseract-ocr
- tesseract-langpack-kor

### 3. Python 환경 설정
```bash
./install.sh
```

다음을 수행합니다:
- Python 3.13+ 확인
- 가상 환경 생성 (.venv)
- Python 패키지 설치
- 개발 설정 구성

### 4. 설치 확인
```bash
./pdfocr --help
./test.fish
```

## 코드 스타일

### Python 규칙
- **들여쓰기**: 4칸
- **줄 길이**: 120자까지
- **따옴표**: 문자열은 큰따옴표 선호
- **명명 규칙**:
  - 함수: `snake_case`
  - 클래스: `PascalCase`
  - 상수: `UPPER_SNAKE_CASE`
  - 비공개 함수: `_leading_underscore`

### Docstring 형식
```python
def function_name(param1: str, param2: int) -> bool:
    """함수가 수행하는 작업에 대한 간단한 설명.

    Args:
        param1: 첫 번째 매개변수 설명
        param2: 두 번째 매개변수 설명

    Returns:
        반환 값 설명

    Raises:
        ValueError: 발생할 수 있는 예외 설명
    """
    pass
```

### Import 순서
```python
# 1. 표준 라이브러리
import os
import sys
from pathlib import Path

# 2. 서드파티 패키지
import cv2
import numpy as np
from PIL import Image

# 3. 로컬 모듈
from pdfocr.layout import detect_blocks
from pdfocr.types import BlockInfo
```

## 기능 추가

### 1. 계획
기능을 다음과 같이 나눕니다:
- 사용자 요구사항 정의
- 기술적 접근 방식 고려
- 기존 모듈 구조 검토

### 2. 분기 생성
```bash
git checkout -b feature/feature-name
```

### 3. 구현
코드 작성 시:
- 기존 패턴 따르기
- 오류 케이스 처리
- 적절한 로깅 추가
- 상세한 주석 작성

### 4. 테스트
```bash
# 통합 테스트 실행
./test.fish

# 특정 기능 테스트
./pdfocr test/test_document.pdf -o test_output/
```

### 5. 커밋
```bash
git add .
git commit -m "feat: 기능에 대한 간략한 설명"
```

커밋 메시지 규칙:
- `feat:` - 새로운 기능
- `fix:` - 버그 수정
- `docs:` - 문서 변경
- `style:` - 코드 형식 지정
- `refactor:` - 코드 리팩토링
- `test:` - 테스트 추가
- `chore:` - 빌드/설정 변경

## 일반적인 개발 작업

### 새로운 OCR 옵션 추가

1. **CLI 인자 추가** (`main.py`):
```python
parser.add_argument('--new-option', type=str,
                    help='옵션 설명')
```

2. **처리 함수 업데이트** (`image_to_text.py`):
```python
def extract_text_from_image(image_path, lang="kor", new_option=None):
    # 옵션 구현
    pass
```

3. **테스트 및 문서화**:
```bash
./pdfocr test.pdf --new-option value
```

### 새로운 출력 형식 추가

1. **포매터 모듈 생성** (`src/pdfocr/formatters/`):
```python
# src/pdfocr/formatters/markdown.py
def format_as_markdown(pages):
    """페이지를 마크다운 형식으로 포맷"""
    pass
```

2. **메인에서 통합** (`main.py`):
```python
from pdfocr.formatters.markdown import format_as_markdown

if args.format == "markdown":
    output = format_as_markdown(pages)
```

### 새로운 언어 지원 추가

1. **언어팩 설치**:
```bash
sudo dnf install tesseract-langpack-<언어코드>
```

2. **문서 업데이트**:
`docs/QUICKSTART.md`에 새로운 언어 코드 추가

3. **테스트**:
```bash
./pdfocr document.pdf --lang <언어코드>
```

## 디버깅

### 자세한 로깅 활성화

Python에서:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

또는 코드 편집:
```python
logger.setLevel(logging.DEBUG)
```

### 임시 이미지 검사
```bash
./pdfocr file.pdf --keep-images -i debug_images/
ls -l debug_images/
```

### OCR 정확도 테스트
```bash
# 고해상도 테스트
./pdfocr test.pdf --dpi 600

# 여러 언어 시도
./pdfocr test.pdf --lang kor+eng
```

### PDF 변환 확인
```bash
# Poppler 직접 테스트
pdftoppm test.pdf output -png -r 300
tesseract output-1.png stdout -l kor
```

## 테스트 체크리스트

릴리스 전 확인:

- [ ] 단일 PDF 처리 작동
- [ ] 여러 PDF 일괄 처리 작동
- [ ] 병합 기능 작동 (`--merge`)
- [ ] 다양한 DPI 설정 테스트
- [ ] 다른 언어 테스트
- [ ] 이미지 정리 작동
- [ ] 이미지 보존 작동 (`--keep-images`)
- [ ] 오류 처리 우아함
- [ ] 도움말 메시지 명확함
- [ ] 문서 업데이트됨

## 릴리스 프로세스

### 1. 버전 업데이트
업데이트:
- `README.md` (있는 경우 버전)
- `CHANGELOG.md` (생성 시)

### 2. 최종 테스트
```bash
./test.fish
./pdfocr test/test_document.pdf
```

### 3. 커밋 및 태그
```bash
git add .
git commit -m "chore: release v0.x.x"
git tag -a v0.x.x -m "Release v0.x.x

- 기능 1 설명
- 기능 2 설명
- 버그 수정 설명
"
```

### 4. 푸시
```bash
git push origin main
git push origin v0.x.x
```

## 기여 가이드라인

### 풀 리퀘스트 제출

1. **Fork 및 Clone**
2. **브랜치 생성**
3. **변경 사항 구현**
4. **테스트 작성**
5. **커밋 푸시**
6. **풀 리퀘스트 생성**

### 코드 리뷰 프로세스

리뷰어는 다음을 확인합니다:
- 코드가 스타일 가이드 따름
- 테스트가 통과함
- 문서가 업데이트됨
- 오류 케이스가 처리됨
- 성능에 영향 없음

### 이슈 보고

버그 보고 시 다음을 포함:
- 운영 체제 및 버전
- Python 버전
- 문제 재현 단계
- 예상 동작
- 실제 동작
- 오류 메시지/로그

## 성능 최적화

### 프로파일링

Python 프로파일러 사용:
```python
import cProfile
cProfile.run('process_single_pdf("test.pdf", "output/")')
```

### 병목 현상 식별

일반적인 느린 부분:
- PDF to Image 변환 (poppler)
- OCR 처리 (tesseract)
- 디스크 I/O

### 최적화 전략

1. **병렬 처리**:
```python
from multiprocessing import Pool

with Pool() as pool:
    pool.map(process_page, pages)
```

2. **캐싱**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation(data):
    pass
```

3. **배치 작업**:
```python
# 한 번에 모든 이미지 처리
pytesseract.image_to_string(images)  # 배치
```

## 유용한 명령어

### 개발
```bash
# 가상 환경 활성화
source .venv/bin/activate

# 종속성 설치
pip install -r requirements.txt

# 로컬 패키지 설치 (편집 가능)
pip install -e .
```

### 테스트
```bash
# 빠른 테스트
./pdfocr test/test_document.pdf -o /tmp/test

# 블록 감지 테스트
python src/pdfocr/block_ocr.py test/test_document.pdf

# 이미지 정리 테스트
./pdfocr test.pdf && ls -la output_images/
```

### 정리
```bash
# 생성된 파일 제거
rm -rf output_images/ output_text/

# 테스트 출력 제거
rm -rf test/output*

# 캐시 정리
find . -type d -name __pycache__ -exec rm -rf {} +
```

## 문제 해결

### "command not found: pdfocr"
```bash
# PATH 추가 확인
export PATH="$PATH:$(pwd)"
```

### "No module named pdfocr"
```bash
# PYTHONPATH 설정
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
```

### "Tesseract not found"
```bash
# Tesseract 설치 확인
which tesseract
tesseract --version
```

### "PDF 처리 실패"
```bash
# PDF가 유효한지 확인
pdfinfo file.pdf

# 수동으로 이미지로 변환 시도
pdftoppm file.pdf test -png
```

## 추가 자료

- [Tesseract 문서](https://tesseract-ocr.github.io/)
- [Poppler 유틸리티](https://poppler.freedesktop.org/)
- [pdf2image GitHub](https://github.com/Belval/pdf2image)
- [pytesseract GitHub](https://github.com/madmaze/pytesseract)

## 지원 받기

질문이나 도움이 필요한 경우:
1. [문서](docs/) 확인
2. [기존 이슈](https://github.com/zeetee1235/pdfocr/issues) 검색
3. 새로운 이슈 생성
4. 커뮤니티 포럼 참여 (있는 경우)
