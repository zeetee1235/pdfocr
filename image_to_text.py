"""
이미지에서 텍스트를 OCR로 추출하는 모듈
"""
import os
import pytesseract
from PIL import Image
from typing import List, Dict


def extract_text_from_image(image_path: str, lang: str = "kor") -> str:
    """
    단일 이미지에서 텍스트 추출
    
    Args:
        image_path (str): 이미지 파일 경로
        lang (str): OCR 언어 (기본값: "kor" - 한국어)
    
    Returns:
        str: 추출된 텍스트
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as e:
        raise Exception(f"이미지 {image_path}에서 텍스트 추출 실패: {str(e)}")


def extract_text_from_images(image_paths: List[str], lang: str = "kor") -> Dict[str, str]:
    """
    여러 이미지에서 텍스트 추출
    
    Args:
        image_paths (List[str]): 이미지 파일 경로 리스트
        lang (str): OCR 언어 (기본값: "kor" - 한국어)
    
    Returns:
        Dict[str, str]: {이미지 경로: 추출된 텍스트} 딕셔너리
    """
    print(f"🔍 OCR 텍스트 추출 시작 (언어: {lang})")
    print(f"   총 {len(image_paths)}개 이미지 처리 예정\n")
    
    results = {}
    
    for i, image_path in enumerate(image_paths, start=1):
        print(f"  [{i}/{len(image_paths)}] 처리 중: {os.path.basename(image_path)}")
        try:
            text = extract_text_from_image(image_path, lang=lang)
            results[image_path] = text
            print(f"    ✓ 추출된 텍스트: {len(text)} 글자")
        except Exception as e:
            print(f"    ✗ 오류: {e}")
            results[image_path] = ""
    
    print(f"\n✓ OCR 추출 완료\n")
    return results


def save_extracted_text(text_dict: Dict[str, str], output_path: str = "output/extracted_text.txt"):
    """
    추출된 텍스트를 파일로 저장
    
    Args:
        text_dict (Dict[str, str]): {이미지 경로: 추출된 텍스트} 딕셔너리
        output_path (str): 출력 파일 경로 (기본값: "output/extracted_text.txt")
    """
    # 출력 디렉토리가 없으면 생성
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ 디렉토리 생성: {output_dir}")
    
    print(f"💾 텍스트 파일 저장 중: {output_path}")
    
    # UTF-8 인코딩으로 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, (image_path, text) in enumerate(sorted(text_dict.items()), start=1):
            # 페이지 헤더 작성
            page_name = os.path.basename(image_path)
            f.write(f"{'='*80}\n")
            f.write(f"페이지 {i}: {page_name}\n")
            f.write(f"{'='*80}\n\n")
            
            # 텍스트 작성
            f.write(text)
            
            # 페이지 구분을 위한 줄바꿈
            f.write("\n\n\n")
    
    print(f"✓ 저장 완료: {output_path}\n")


if __name__ == "__main__":
    # 테스트용 코드
    import sys
    import glob
    
    if len(sys.argv) < 2:
        print("사용법: python image_to_text.py <이미지디렉토리>")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.png")))
    
    if not image_files:
        print(f"오류: {image_dir}에서 PNG 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    try:
        text_results = extract_text_from_images(image_files)
        save_extracted_text(text_results)
        print("텍스트 추출 및 저장 완료!")
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)
