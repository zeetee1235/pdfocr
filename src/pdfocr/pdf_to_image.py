"""
PDF를 페이지별 이미지로 변환하는 모듈
"""
from pathlib import Path
from typing import List

from pdf2image import convert_from_path

from pdfocr.types import PathLike


def _ensure_output_dir(output_dir: Path) -> None:
    created = not output_dir.exists()
    output_dir.mkdir(parents=True, exist_ok=True)
    if created:
        print(f"✓ 디렉토리 생성: {output_dir}")


def convert_pdf_to_images(pdf_path: PathLike, output_dir: PathLike = "images", dpi: int = 300) -> List[str]:
    """
    PDF 파일을 페이지별 이미지로 변환
    
    Args:
        pdf_path (PathLike): 변환할 PDF 파일 경로
        output_dir (PathLike): 이미지 저장 디렉토리 (기본값: "images")
        dpi (int): 이미지 해상도 (기본값: 300)
    
    Returns:
        List[str]: 생성된 이미지 파일 경로 리스트 (문자열 경로)
    """
    pdf_path = Path(pdf_path).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    _ensure_output_dir(output_dir)

    print(f"📄 PDF 파일 변환 시작: {pdf_path}")
    try:
        images = convert_from_path(str(pdf_path), dpi=dpi)
        print(f"✓ {len(images)}개 페이지 감지")
    except Exception as exc:
        raise RuntimeError(f"PDF 변환 중 오류 발생: {exc}") from exc

    image_paths: List[str] = []
    pdf_basename = pdf_path.stem

    for i, image in enumerate(images, start=1):
        image_path = output_dir / f"{pdf_basename}_page_{i:03d}.png"
        image.save(image_path, "PNG")
        image_paths.append(str(image_path))
        print(f"  ✓ 저장: {image_path}")

    print(f"✓ 총 {len(image_paths)}개 이미지 생성 완료\n")
    return image_paths


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python pdf_to_image.py <PDF파일경로>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    try:
        image_files = convert_pdf_to_images(pdf_file)
        print(f"생성된 이미지: {len(image_files)}개")
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"오류: {exc}")
        sys.exit(1)
