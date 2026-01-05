"""
이미지에서 텍스트를 OCR로 추출하는 모듈
"""
from pathlib import Path
from typing import Dict, Sequence, Union

import pytesseract
from PIL import Image

PathLike = Union[str, Path]
TextDict = Dict[str, str]


def extract_text_from_image(image_path: PathLike, lang: str = "kor") -> str:
    """
    단일 이미지에서 텍스트 추출
    
    Args:
        image_path (PathLike): 이미지 파일 경로
        lang (str): OCR 언어 (기본값: "kor" - 한국어)
    
    Returns:
        str: 추출된 텍스트
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    try:
        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as exc:
        raise RuntimeError(f"이미지 {image_path}에서 텍스트 추출 실패: {exc}") from exc


def extract_text_from_images(image_paths: Sequence[PathLike], lang: str = "kor") -> TextDict:
    """
    여러 이미지에서 텍스트 추출
    
    Args:
        image_paths (Sequence[PathLike]): 이미지 파일 경로 리스트
        lang (str): OCR 언어 (기본값: "kor" - 한국어)
    
    Returns:
        Dict[str, str]: {이미지 경로: 추출된 텍스트} 딕셔너리
    """
    image_paths = [Path(p) for p in image_paths]
    print(f"🔍 OCR 텍스트 추출 시작 (언어: {lang})")
    print(f"   총 {len(image_paths)}개 이미지 처리 예정\n")
    
    results: TextDict = {}
    
    for i, image_path in enumerate(image_paths, start=1):
        print(f"  [{i}/{len(image_paths)}] 처리 중: {image_path.name}")
        try:
            text = extract_text_from_image(image_path, lang=lang)
            results[str(image_path)] = text
            print(f"    ✓ 추출된 텍스트: {len(text)} 글자")
        except Exception as exc:
            print(f"    ✗ 오류: {exc}")
            results[str(image_path)] = ""
    
    print(f"\n✓ OCR 추출 완료\n")
    return results


def save_extracted_text(text_dict: TextDict, output_path: PathLike = "output/extracted_text.txt") -> None:
    """
    추출된 텍스트를 파일로 저장
    
    Args:
        text_dict (Dict[str, str]): {이미지 경로: 추출된 텍스트} 딕셔너리
        output_path (PathLike): 출력 파일 경로 (기본값: "output/extracted_text.txt")
    """
    output_path = Path(output_path)
    output_dir = output_path.parent

    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 디렉토리 생성: {output_dir}")
    
    print(f"💾 텍스트 파일 저장 중: {output_path}")
    
    with output_path.open('w', encoding='utf-8') as f:
        for i, (image_path, text) in enumerate(sorted(text_dict.items()), start=1):
            page_name = Path(image_path).name
            f.write(f"{'='*80}\n")
            f.write(f"페이지 {i}: {page_name}\n")
            f.write(f"{'='*80}\n\n")
            f.write(text)
            f.write("\n\n\n")
    
    print(f"✓ 저장 완료: {output_path}\n")


if __name__ == "__main__":  # pragma: no cover - CLI helper
    import glob
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python image_to_text.py <이미지디렉토리>")
        sys.exit(1)
    
    image_dir = Path(sys.argv[1])
    image_files = sorted(glob.glob(str(image_dir / "*.png")))
    
    if not image_files:
        print(f"오류: {image_dir}에서 PNG 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    try:
        text_results = extract_text_from_images(image_files)
        save_extracted_text(text_results)
        print("텍스트 추출 및 저장 완료!")
    except Exception as exc:
        print(f"오류: {exc}")
        sys.exit(1)
