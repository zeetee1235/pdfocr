#!/usr/bin/env python3
"""
PDF → 이미지 → 텍스트 추출 파이프라인
수업 자료 PDF를 텍스트로 변환하여 LaTeX 문서 작성을 위한 전처리 수행
"""
import argparse
import glob
import os
import tempfile
from pathlib import Path
from typing import Iterable, List, Sequence

from pdfocr.image_to_text import extract_text_from_images, save_extracted_text
from pdfocr.pdf_to_image import convert_pdf_to_images
from pdfocr.types import PathLike


def _resolve_pdf_path(pdf_path: PathLike) -> Path:
    path = Path(pdf_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
    return path


def _resolve_output_dir(pdf_path: Path, output_dir: PathLike | None) -> Path:
    if output_dir is None:
        return pdf_path.parent
    return Path(output_dir).expanduser().resolve()


def _resolve_image_dir(image_dir: PathLike | None) -> tuple[Path, bool]:
    if image_dir is None:
        temp_path = Path(tempfile.mkdtemp(prefix="pdf2txt_"))
        return temp_path, True
    return Path(image_dir).expanduser().resolve(), False


def _cleanup_images(image_paths: Sequence[str], image_dir: Path, remove_dir: bool) -> None:
    print("🗑️  임시 이미지 파일 삭제 중...")
    for img_path in image_paths:
        try:
            Path(img_path).unlink(missing_ok=True)
        except Exception as exc:
            print(f"  경고: {img_path} 삭제 실패 - {exc}")

    if remove_dir:
        try:
            if image_dir.exists() and not any(image_dir.iterdir()):
                image_dir.rmdir()
        except Exception:
            pass

    print("✓ 임시 파일 정리 완료\n")


def process_single_pdf(pdf_path: PathLike,
                       output_dir: PathLike | None = None,
                       image_dir: PathLike | None = None,
                       lang: str = "kor",
                       dpi: int = 300,
                       keep_images: bool = False):
    """
    단일 PDF 파일 처리 파이프라인
    
    Args:
        pdf_path (str): PDF 파일 경로
        output_dir (str): 텍스트 출력 디렉토리 (None이면 PDF와 같은 디렉토리)
        image_dir (str): 임시 이미지 저장 디렉토리 (None이면 임시 디렉토리 사용)
        lang (str): OCR 언어 (기본값: "kor")
        dpi (int): 이미지 해상도
        keep_images (bool): 처리 후 이미지 보존 여부
    
    Returns:
        str: 생성된 텍스트 파일 경로
    """
    pdf_path = _resolve_pdf_path(pdf_path)
    output_dir = _resolve_output_dir(pdf_path, output_dir)
    image_dir, is_temp_dir = _resolve_image_dir(image_dir)
    
    print("\n" + "="*80)
    print(f"PDF 처리 시작: {pdf_path.name}")
    print(f"위치: {pdf_path}")
    print(f"출력 디렉토리: {output_dir}")
    print("="*80 + "\n")
    
    # 1단계: PDF → 이미지 변환
    print("【1단계】 PDF → 이미지 변환")
    print("-"*80)
    try:
        image_paths = convert_pdf_to_images(pdf_path, output_dir=image_dir, dpi=dpi)
    except Exception as exc:
        print(f"✗ PDF 변환 실패: {exc}")
        return None
    
    # 2단계: 이미지 → 텍스트 추출
    print("【2단계】 이미지 → 텍스트 OCR 추출")
    print("-"*80)
    try:
        text_results = extract_text_from_images(image_paths, lang=lang)
    except Exception as exc:
        print(f"✗ OCR 추출 실패: {exc}")
        return None
    
    # 3단계: 텍스트 파일 저장
    print("【3단계】 텍스트 파일 저장")
    print("-"*80)
    pdf_basename = pdf_path.stem
    output_path = Path(output_dir) / f"{pdf_basename}_extracted.txt"
    
    try:
        save_extracted_text(text_results, output_path)
    except Exception as exc:
        print(f"✗ 파일 저장 실패: {exc}")
        return None
    
    # 임시 이미지 파일 정리
    if not keep_images:
        _cleanup_images(image_paths, image_dir, is_temp_dir)
    
    print("="*80)
    print(f"✅ 처리 완료!")
    print(f"📝 출력 파일: {output_path}")
    print("="*80 + "\n")
    
    return output_path


def process_multiple_pdfs(pdf_paths: Sequence[PathLike],
                         output_dir: PathLike | None = None,
                         image_dir: PathLike | None = None,
                         lang: str = "kor",
                         dpi: int = 300,
                         keep_images: bool = False,
                         merge: bool = False):
    """
    여러 PDF 파일 일괄 처리
    
    Args:
        pdf_paths (list): PDF 파일 경로 리스트
        output_dir (str): 텍스트 출력 디렉토리 (None이면 각 PDF와 같은 디렉토리)
        image_dir (str): 임시 이미지 저장 디렉토리
        lang (str): OCR 언어
        dpi (int): 이미지 해상도
        keep_images (bool): 처리 후 이미지 보존 여부
        merge (bool): 모든 텍스트를 하나의 파일로 병합할지 여부
    """
    print(f"\n총 {len(pdf_paths)}개의 PDF 파일 처리 예정\n")
    
    # merge 옵션이 켜져있고 output_dir이 지정되지 않았으면 현재 디렉토리 사용
    if merge and output_dir is None:
        output_dir = Path.cwd()
    
    output_files: List[Path] = []
    all_texts: List[str] = []
    
    for i, pdf_path in enumerate(pdf_paths, start=1):
        print(f"\n>>> [{i}/{len(pdf_paths)}] 처리 중...")
        output_file = process_single_pdf(
            pdf_path,
            output_dir=output_dir,
            image_dir=image_dir,
            lang=lang,
            dpi=dpi,
            keep_images=keep_images
        )
        
        if output_file:
            output_files.append(Path(output_file))
            if merge:
                with open(output_file, 'r', encoding='utf-8') as f:
                    all_texts.append(f.read())
    
    # 병합된 파일 생성
    if merge and all_texts:
        merged_path = Path(output_dir) / "merged_all_texts.txt"
        print(f"\n📚 모든 텍스트를 하나의 파일로 병합 중...")
        with merged_path.open('w', encoding='utf-8') as f:
            for i, text in enumerate(all_texts, start=1):
                f.write(f"\n{'#'*80}\n")
                f.write(f"# 문서 {i}: {Path(pdf_paths[i-1]).name}\n")
                f.write(f"{'#'*80}\n\n")
                f.write(text)
                f.write("\n\n")
        print(f"✓ 병합 파일 생성: {merged_path}\n")
    
    print("\n" + "="*80)
    print(f"✅ 전체 처리 완료! (성공: {len(output_files)}/{len(pdf_paths)})")
    print("="*80)


def _collect_valid_pdfs(patterns: Iterable[str]) -> List[Path]:
    expanded: list[str] = []
    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            expanded.extend(glob.glob(pattern))
        else:
            expanded.append(pattern)

    valid: List[Path] = []
    seen: set[Path] = set()

    for raw_path in expanded:
        resolved = Path(raw_path).expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)

        if resolved.exists():
            valid.append(resolved)
        else:
            print(f"경고: 파일을 찾을 수 없습니다 - {raw_path}")

    return sorted(valid, key=lambda p: str(p))


def main():
    parser = argparse.ArgumentParser(
        description="PDF를 텍스트로 변환하는 파이프라인 (수업 자료 → LaTeX 전처리)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 단일 PDF 처리
  python main.py lecture1.pdf
  
  # 여러 PDF 처리
  python main.py lecture1.pdf lecture2.pdf lecture3.pdf
  
  # 디렉토리의 모든 PDF 처리
  python main.py pdfs/*.pdf
  
  # 모든 텍스트를 하나의 파일로 병합
  python main.py pdfs/*.pdf --merge
  
  # 이미지 파일 보존 (디버깅용)
  python main.py lecture.pdf --keep-images
        """
    )
    
    parser.add_argument(
        'pdf_files',
        nargs='+',
        help='처리할 PDF 파일 경로 (여러 개 가능)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default=None,
        help='텍스트 출력 디렉토리 (기본값: PDF와 같은 디렉토리)'
    )
    
    parser.add_argument(
        '-i', '--image-dir',
        default=None,
        help='임시 이미지 저장 디렉토리 (기본값: 자동 생성된 임시 디렉토리)'
    )
    
    parser.add_argument(
        '-l', '--lang',
        default='kor',
        help='OCR 언어 코드 (기본값: kor - 한국어)'
    )
    
    parser.add_argument(
        '-d', '--dpi',
        type=int,
        default=300,
        help='이미지 변환 해상도 (기본값: 300)'
    )
    
    parser.add_argument(
        '--keep-images',
        action='store_true',
        help='처리 후 이미지 파일 보존 (기본값: 삭제)'
    )
    
    parser.add_argument(
        '--merge',
        action='store_true',
        help='모든 텍스트를 하나의 파일로 병합'
    )
    
    args = parser.parse_args()
    
    valid_pdfs = _collect_valid_pdfs(args.pdf_files)
     
    if not valid_pdfs:
        print("오류: 처리할 PDF 파일이 없습니다.")
        sys.exit(1)
    
    # 파이프라인 실행
    if len(valid_pdfs) == 1:
        process_single_pdf(
            valid_pdfs[0],
            output_dir=args.output_dir,
            image_dir=args.image_dir,
            lang=args.lang,
            dpi=args.dpi,
            keep_images=args.keep_images
        )
    else:
        process_multiple_pdfs(
            valid_pdfs,
            output_dir=args.output_dir,
            image_dir=args.image_dir,
            lang=args.lang,
            dpi=args.dpi,
            keep_images=args.keep_images,
            merge=args.merge
        )


if __name__ == "__main__":
    main()
