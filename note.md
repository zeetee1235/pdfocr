PDF→이미지 단계는 문제 없어 보입니다.

pdftoppm -png -r 300 test/test_document.pdf test/debug_images/page 로 뽑아본 결과, PNG 3장이 생성됐고 모두 2550x3300 @ 300dpi(page-1.png 등). 해상도와 크기 모두 정상이며 깨짐 없이 렌더링됩니다.
즉 PDF→이미지 변환은 제대로 되고 있고, 문제는 그 다음 단계(OCR)에서 발생한 것으로 보입니다.
의심 포인트:

현재 기본 --lang kor 로 돌리면 영어/수식 위주 문서에서 인식이 거의 안 되므로 gibberish 가 나옵니다.
OCR 품질 확인을 위해 --lang eng 또는 --lang eng+kor 로 다시 실행하고, --keep-images 로 생성된 PNG(-i로 지정한 디렉토리)에 대해 tesseract <img> stdout --dpi 300 -l eng 등으로 직접 점검해 보세요.