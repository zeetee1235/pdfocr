# 아키텍처

## 개요

pdfocr는 OCR(광학 문자 인식)을 사용하여 PDF 문서에서 텍스트를 추출하는 명령줄 도구입니다. 파이프라인은 세 가지 주요 단계로 구성됩니다:

1. **PDF to Image 변환** - PDF 페이지를 고해상도 PNG 이미지로 변환
2. **OCR 처리** - Tesseract OCR을 사용하여 이미지에서 텍스트 추출
3. **텍스트 출력** - 적절한 형식으로 추출된 텍스트 저장

## 모듈 구조

### 핵심 모듈

#### `src/pdfocr/main.py`
CLI 애플리케이션의 메인 진입점.
- 명령줄 인자 파싱
- 파이프라인 조율
- 파일 경로 해석
- 진행 상황 보고

**주요 함수:**
- `process_single_pdf()` - 단일 PDF 파일 처리
- `process_multiple_pdfs()` - 병합 옵션이 있는 일괄 처리
- `main()` - 인자 파싱이 있는 CLI 진입점

#### `src/pdfocr/pdf_to_image.py`
pdf2image(poppler 래퍼)를 사용한 PDF to Image 변환.

**주요 함수:**
- `convert_pdf_to_images()` - PDF 페이지를 PNG 이미지로 변환
  - 내부적으로 poppler의 `pdftoppm` 사용
  - 설정 가능한 DPI (기본값: 300)
  - 이미지 경로 목록 반환

**의존성:**
- `pdf2image` - poppler용 Python 래퍼
- `poppler-utils` - PDF 렌더링용 시스템 패키지

#### `src/pdfocr/image_to_text.py`
pytesseract(Tesseract 래퍼)를 사용한 OCR 텍스트 추출.

**주요 함수:**
- `extract_text_from_image()` - 단일 이미지에서 텍스트 추출
- `extract_text_from_images()` - 여러 이미지에서 일괄 추출
- `save_extracted_text()` - 결과를 형식화된 텍스트 파일로 저장

**기능:**
- 다국어 지원 (기본값: 한국어)
- 추출 실패에 대한 오류 처리
- 페이지별로 구분된 출력 형식

**의존성:**
- `pytesseract` - Tesseract용 Python 래퍼
- `Pillow` - 이미지 처리
- `tesseract-ocr` - OCR 엔진용 시스템 패키지

### 고급 모듈

#### `src/pdfocr/layout.py`
OpenCV를 사용한 레이아웃 분석 및 블록 감지.

**주요 함수:**
- `detect_blocks()` - 이미지에서 텍스트 블록 감지
- `draw_blocks()` - 감지된 블록 시각화
- 블록 감지를 위한 형태학적 연산 사용

**사용 사례:**
- 복잡한 문서 레이아웃
- 다단 텍스트
- 표 추출

#### `src/pdfocr/block_ocr.py`
복잡한 레이아웃에서 더 나은 정확도를 위한 블록 기반 OCR.

**주요 함수:**
- `extract_blocks_to_json()` - 위치 데이터와 함께 텍스트 블록 추출
- 블록 좌표와 텍스트가 포함된 JSON 출력

**사용 사례:**
- 공간 정보 보존
- 구조화된 문서 파싱
- 레이아웃 인식 텍스트 추출

## 실행 흐름

### 단일 PDF 처리

```
사용자 입력
    ↓
명령줄 파서 (main.py)
    ↓
경로 해석 및 유효성 검사
    ↓
PDF to Image (pdf_to_image.py)
    ↓
OCR 추출 (image_to_text.py)
    ↓
텍스트 파일 출력
    ↓
정리 (선택사항)
```

### 일괄 처리

```
여러 PDF 파일
    ↓
각 PDF에 대해:
    ├─→ 이미지로 변환
    ├─→ 텍스트 추출
    └─→ 개별 파일 저장
        ↓
    (선택) 모든 텍스트 병합
        ↓
    병합된 파일 출력
```

## 설정

### 환경 변수
현재 사용되지 않음.

### 명령줄 옵션
- `-o, --output-dir` - 출력 디렉토리
- `-i, --image-dir` - 임시 이미지 디렉토리
- `-l, --lang` - OCR 언어 코드 (기본값: "kor")
- `-d, --dpi` - 이미지 해상도 (기본값: 300)
- `--keep-images` - 임시 이미지 보존
- `--merge` - 여러 출력을 하나의 파일로 병합

## 의존성

### Python 패키지
- `pdf2image` - PDF to Image 변환
- `pytesseract` - Tesseract OCR 래퍼
- `Pillow>=11.0.0` - 이미지 처리 (Python 3.13 호환)
- `opencv-python>=4.8.0` - 컴퓨터 비전 (선택사항, 레이아웃용)
- `numpy>=1.24.0` - 수치 연산 (선택사항, 레이아웃용)

### 시스템 패키지
- `poppler-utils` - PDF 렌더링 (pdftoppm, pdfinfo)
- `tesseract-ocr` - OCR 엔진
- `tesseract-langpack-kor` - 한국어 지원 (선택사항)

## 오류 처리

### 파일을 찾을 수 없음
- 처리 전 모든 입력 경로 유효성 검사
- 파일 경로와 함께 명확한 오류 메시지 제공

### OCR 실패
- 나머지 파일 처리 계속
- 파이프라인을 중단하지 않고 오류 기록
- 실패한 추출에 대해 빈 문자열 반환

### 리소스 정리
- 기본적으로 임시 이미지 삭제
- `--keep-images`로 보존 가능
- 정리 실패를 우아하게 처리

## 성능 고려사항

### 메모리 사용량
- 이미지를 한 번에 하나씩 로드
- 처리 후 임시 파일 정리
- 일괄 처리를 위한 메모리 누적 없음

### 처리 속도
속도에 영향을 미치는 요인:
- DPI 설정 (높을수록 느리지만 더 정확)
- 페이지 수
- 이미지 복잡도
- 시스템 OCR 성능

일반적인 속도:
- 300 DPI: 페이지당 약 2-5초
- 600 DPI: 페이지당 약 5-10초

### 병렬화
현재 단일 스레드. 향후 개선 사항:
- 병렬 페이지 처리
- 일괄 OCR 작업
- 파일 작업을 위한 비동기 I/O

## 향후 개선사항

### 계획된 기능
- [ ] 여러 페이지에 대한 병렬 처리
- [ ] PDF 텍스트 레이어 감지 (텍스트가 있으면 OCR 건너뛰기)
- [ ] 추출된 텍스트에 대한 신뢰도 점수
- [ ] 더 나은 표 추출
- [ ] 수학 공식 인식
- [ ] 긴 작업을 위한 진행률 표시줄

### 잠재적 개선사항
- 설정 파일 지원
- 사용자 정의 프로세서를 위한 플러그인 시스템
- 웹 API 인터페이스
- GUI 애플리케이션
- Docker 컨테이너

## 테스트

### 테스트 스위트
`test/` 디렉토리에 위치:
- `test_document.tex` - 테스트 PDF용 LaTeX 소스
- `test_document.pdf` - 생성된 테스트 문서
- `test.fish` - 통합 테스트 스크립트

### 테스트 실행
```bash
./test.fish
```

다음을 수행합니다:
1. LaTeX에서 테스트 PDF 빌드
2. OCR 파이프라인 실행
3. 블록 감지 수행
4. 출력 검증

## 로깅

### 로그 레벨
- `INFO` - 일반 작업 메시지
- `DEBUG` - 상세한 처리 정보
- `WARNING` - 중요하지 않은 문제
- `ERROR` - 실패 메시지

### 로그 출력
현재 stdout으로 로깅. 향후: 설정 가능한 로그 파일.

## 호환성

### Python 버전
- Python 3.13+ (권장)
- Python 3.11+ (지원)

### 운영 체제
- Linux (Fedora, Ubuntu, Debian) - 주요
- macOS - 지원
- Windows - 테스트되지 않음

### 알려진 제한사항
- 오른쪽에서 왼쪽 텍스트 최적화되지 않음
- 세로 텍스트는 회전 필요할 수 있음
- 손글씨 텍스트는 정확도가 낮음
- 수학 기호는 종종 잘못 인식됨
