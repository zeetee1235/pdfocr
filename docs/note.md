### 내가 이걸 왜 만들었는가...!
pdf 자체에서 그냥 텍스트만 추출하는 도구를 쓰고 있었는데,
이게...그림인식을 못해서 대학교 수업자료(ex: ppt)
여기서 텍스트를 추출하는데 제한사항이 있음...

그래서! 만들었음!

### note
이걸 어떻게 해야하는가...에 대하여
텍스트를 블록으로 나누고, 그걸 따로 따로 인식하고 위치를 기반으로 조합...?
수식이랑 표는 어떻게 하는가...
수식,그림,표(이건 그냥 텍스트 블록 여러개로),텍스트블록을 나누는 알고리즘을 만들어야할듯...

0) 목표 정의

입력: 페이지 이미지(또는 PDF 렌더링 이미지)
출력:

Reading-order로 정렬된 텍스트(본문 중심)

표는 구조화 결과(CSV/Markdown/JSON)

수식/그림은 placeholder + crop 이미지(MVP), 옵션으로 수식 OCR

핵심 성능 지표(현실적인):

본문 텍스트가 깨지지 않고 문장 단위로 읽힘

표는 셀 단위 텍스트가 빠지지 않음(정확도는 다음)

수식은 “망가진 문자열”로 본문을 오염시키지 않음(= 분리)

1) 전체 파이프라인 (큰 흐름)
Stage A: Page Normalize

해상도 표준화(너무 크면 downscale, 너무 작으면 upscale)

그레이 변환

대비 개선(선택)

이진화(adaptive/otsu) → 레이아웃 분석용 바이너리 이미지 생성

Output: gray, binary

2) Stage B: Layout Segmentation (블록 후보 생성)

페이지를 “의미 있는 영역”으로 나누는 단계.

B-1) Table 후보 검출 (가장 먼저!)

표는 전체 OCR을 망치기 쉬워서, 먼저 찾아서 격리하는 게 중요.

표 검출 특징

긴 수평선/수직선이 반복

교차점(그리드) 다수

직사각형 셀 구조

방법(규칙 기반)

binary 반전(inv)에서 morphology-open으로

horizontal lines 추출(가로로 긴 커널)

vertical lines 추출(세로로 긴 커널)

grid = horizontal OR vertical

grid의 연결요소(connected components)에서 큰 덩어리들을 table 후보로

후처리:

너무 작은 덩어리 제거

페이지 가장자리 헤더/푸터 선을 table로 오인하지 않도록 “높이/폭/면적/선 비율”로 필터

Output: table_bboxes[]

MVP 포인트: table을 확실히 잡아내면 나머지(본문) OCR이 훨씬 안정화됨.

B-2) Figure(그림/도표) 후보 검출

그림은 OCR 대상이 아니거나, 캡션만 OCR하면 됨.

그림 특징

큰 영역, 텍스트 컴포넌트 밀도 낮음

edge/texture 많음(사진/그래프)

내부가 비어있지 않고 “모양”이 많음

방법

에지(Canny) 밀도 + 텍스트 컴포넌트 밀도 비교

또는 MSER/연결요소로 텍스트 후보를 먼저 찾고, 텍스트가 거의 없는 큰 영역을 figure로

Output: figure_bboxes[]

B-3) Text 후보 블록 검출 (문단/컬럼 단위)

표와 그림 영역을 mask로 제외하고 남은 영역에서 텍스트 블록을 잡는다.

방법(대표적인 규칙 기반)

binary에서 작은 글자 컴포넌트가 분리되어 있으니,

dilation으로 글자를 “문단 덩어리”로 붙임

가로 방향 dilation(단어를 줄로 연결)

세로 방향 dilation(줄들을 문단으로 연결)

contour/connected components로 bbox 추출

필터:

너무 작은 박스 제거(잡음)

너무 큰 박스(전체 페이지급)는 제외(레이아웃 실패 신호)

Output: text_bboxes[]

B-4) Math(수식) 후보 검출 (MVP에서는 ‘분리 목적’)

수식은 텍스트와 비슷해 보여서 규칙 기반 완벽 분리는 어려움.
그래서 MVP 목표는 “수식 때문에 본문을 오염시키지 않게 분리”.

수식 후보 특징(휴리스틱)

특수기호 비중이 높음(=, +, -, ∑, ∫ 등)

글줄 높이 변화가 큼(위/아래첨자)

괄호가 길거나, 수평선(분수선)이 있음

주변에 “(1), (2)” 같은 수식 번호 패턴이 붙기도 함

MVP 접근

일단 text 블록을 OCR하기 전에,

“수평선(분수선)” 같은 수식 특징을 가진 작은 영역을 별도 후보로 마킹하거나

OCR 결과에서 “기호 비중 과다 + 한글 비중 낮음”인 라인을 math-like로 재분류해서 placeholder 처리

Output: math_bboxes[] 또는 math_spans(OCR 후 라인 단위 재분류)

3) Stage C: Block Classification (최종 타입 결정)

위에서 얻은 후보들이 겹칠 수 있음. 그래서 우선순위와 합집합 규칙이 필요해.

C-1) 우선순위(권장)

table

figure

math

text

C-2) 충돌 해결

IoU(겹침 비율) 기준으로:

text bbox가 table bbox 안에 있으면 → text bbox 제거(표 내부 텍스트는 table 처리로 넘김)

figure와 text가 많이 겹치면 → figure 유지, text는 캡션만 남기게 주변 작은 영역을 별도 탐색

Output: 최종 블록 리스트
blocks = [{bbox, type}, ...]

4) Stage D: Recognition (타입별 인식)
D-1) Text 블록 OCR

블록마다 OCR하면 레이아웃 붕괴 영향이 줄어듦.

블록 특성에 따라 PSM 선택:

문단/단락: psm 6

다단/불규칙: psm 4

짧은 라벨: psm 7 or 8

kor+eng 기본

Output: text_items = [{bbox, text, conf}, ...]

D-2) Table 인식 (구조화)

표는 “블록 OCR”이 아니라 “셀 OCR + 구조 조립”이 목표.

선 있는 표(grid table)

table bbox crop

horizontal/vertical line 재추출(표 영역 안에서 더 강하게)

교차점 → 셀 경계 생성

셀 bbox 목록 생성

셀마다 OCR(보통 psm 6/7)

row/col 인덱스로 매핑하여 표 구성

출력: CSV/Markdown/JSON

선 없는 표(whitespace table) — MVP에서는 fallback

일단 image_to_data로 단어 좌표 뽑고

x좌표 클러스터링으로 열 추정

y좌표로 행 추정

완벽하긴 어렵지만 “대충 표 형태”는 가능

Output: tables = [{bbox, grid, cells, text_matrix}, ...]

D-3) Figure 처리

OCR 대상 제외

다만 “캡션”은 figure bbox 아래/위 작은 텍스트 블록을 추가 탐색해서 text로 처리

Output: figures = [{bbox, image_path, caption_text?}, ...]

D-4) Math 처리

MVP 권장:

수식 bbox는 crop 저장 + placeholder 삽입

나중에 옵션으로 수식 OCR(LaTeX 모델) 붙이기

Output: math = [{bbox, image_path, latex?}, ...]

5) Stage E: Reading Order & Assembly (좌표 기반 조립)

블록별 결과를 “사람이 읽는 순서”로 합친다.

E-1) 컬럼(다단) 감지

페이지의 text bbox들의 x 중심 분포를 분석

2개 이상의 뚜렷한 군집이면 컬럼으로 분리

E-2) 순서 정렬 규칙

컬럼 단위로 left→right 순서

컬럼 내부에서 top→bottom

같은 y라인(행) 안에서는 x로 정렬

E-3) placeholder 삽입 규칙

table bbox 위치에 [TABLE_01] 삽입 + 아래에 표 결과 출력(또는 별도 섹션)

math bbox 위치에 [MATH_03] 삽입

figure bbox 위치에 [FIGURE_02] 삽입

최종 Output

document_text.md (본문 + placeholder)

tables/*.csv or tables.json

math/*.png, figures/*.png

6) MVP에서 “진짜 중요한 선택” 3가지

표를 먼저 잡아서 격리 (안 하면 본문 OCR 계속 망가짐)

페이지 전체 OCR 금지 → 블록 OCR로 분해

수식은 MVP에서 ‘텍스트화’하지 말고 분리
(수식 OCR은 별도 모델/서비스로 가는 게 맞음)



### (이건 일단 미뤄둘것)
이거 pdf텍스트 추출을 먼저하고, 그다음에 이미지로 ocr한거 비교하는 방식이면 좀 더 좋지않을까...
비교는 뭐...llm 때려박지 뭐
