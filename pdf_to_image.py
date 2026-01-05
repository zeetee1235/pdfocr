"""
PDF를 페이지별 이미지로 변환하는 모듈
"""
import os
from pdf2image import convert_from_path
from typing import List


def convert_pdf_to_images(pdf_path: str, output_dir: str = "images", dpi: int = 300) -> List[str]:
    """
    PDF 파일을 페이지별 이미지로 변환
    
    Args:
        pdf_path (str): 변환할 PDF 파일 경로
        output_dir (str): 이미지 저장 디렉토리 (기본값: "images")
        dpi (int): 이미지 해상도 (기본값: 300)
    
    Returns:
        List[str]: 생성된 이미지 파일 경로 리스트
    """
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ 디렉토리 생성: {output_dir}")
    
    # PDF가 존재하는지 확인
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
    
    print(f"📄 PDF 파일 변환 시작: {pdf_path}")
    
    # PDF를 이미지로 변환
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        print(f"✓ {len(images)}개 페이지 감지")
    except Exception as e:
        raise Exception(f"PDF 변환 중 오류 발생: {str(e)}")
    
    # 이미지 파일로 저장
    image_paths = []
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    for i, image in enumerate(images, start=1):
        image_path = os.path.join(output_dir, f"{pdf_basename}_page_{i:03d}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
        print(f"  ✓ 저장: {image_path}")
    
    print(f"✓ 총 {len(image_paths)}개 이미지 생성 완료\n")
    return image_paths


if __name__ == "__main__":
    # 테스트용 코드
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python pdf_to_image.py <PDF파일경로>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    try:
        image_files = convert_pdf_to_images(pdf_file)
        print(f"생성된 이미지: {len(image_files)}개")
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)
