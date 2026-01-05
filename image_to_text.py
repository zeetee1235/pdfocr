"""
이미지/PDF 렌더링 결과에서 OCR 텍스트를 추출하는 모듈 (OpenCV 전처리 + PSM 자동 스윕 + 표용 image_to_data 지원)

핵심 개선:
1) 전처리: 그레이/업스케일/이진화/노이즈 제거/표 선 제거(옵션)
2) PSM 여러 개 자동 시도 후 "가장 그럴듯한" 결과 선택
3) 표(그리드) 문서에서 유리한 image_to_data 기반 추출/재조립 옵션
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import cv2
import numpy as np
import pytesseract
from PIL import Image

PathLike = Union[str, Path]
TextDict = Dict[str, str]


# -----------------------------
# Utilities / Scoring
# -----------------------------
def _to_path(p: PathLike) -> Path:
    return p if isinstance(p, Path) else Path(p)


def _ensure_exists(p: Path) -> None:
    if not p.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {p}")


def _basic_text_quality_score(text: str) -> float:
    """
    OCR 결과 텍스트의 '그럴듯함'을 대략 점수화.
    - 표/수식 문서라도 최소한 "읽을만한 텍스트"가 많으면 점수↑
    - 숫자/기호 난수화면 점수↓
    """
    if not text:
        return 0.0

    total = len(text)
    if total == 0:
        return 0.0

    letters = sum(ch.isalpha() for ch in text)  # 한글도 isalpha=True
    digits = sum(ch.isdigit() for ch in text)
    spaces = sum(ch.isspace() for ch in text)
    punct = total - letters - digits - spaces

    # 문자 비중이 높을수록 좋게, 기호 비중이 높을수록 나쁘게
    letter_ratio = letters / total
    punct_ratio = punct / total

    # 너무 짧은 결과는 패널티
    length_bonus = min(total / 500.0, 1.0)  # 500자 이상이면 1.0

    # 최종 점수: 경험적으로 조합(완벽한 기준은 아님)
    score = (letter_ratio * 2.2 + (digits / total) * 0.6 - punct_ratio * 1.4) * (0.4 + 0.6 * length_bonus)
    return float(score)


# -----------------------------
# Preprocessing (OpenCV)
# -----------------------------
@dataclass
class PreprocessOptions:
    upscale: float = 2.0               # 작은 글씨면 2~3 추천
    denoise: bool = True
    binarize: bool = True
    deskew: bool = False              # 켜면 느릴 수 있음 (기울어진 스캔이면 True 고려)
    remove_table_lines: bool = True   # 표가 많으면 True 추천
    adaptive_thresh: bool = True      # 조명 uneven하면 True가 유리한 경우 많음


def _pil_to_bgr(pil_img: Image.Image) -> np.ndarray:
    rgb = np.array(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return bgr


def _upscale(img: np.ndarray, scale: float) -> np.ndarray:
    if scale is None or scale <= 1.0:
        return img
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)


def _maybe_denoise(gray: np.ndarray) -> np.ndarray:
    # 너무 강하면 글자도 뭉개질 수 있어 moderate로
    return cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)


def _binarize(gray: np.ndarray, adaptive: bool) -> np.ndarray:
    # 문서 OCR은 보통 흰바탕/검은글씨가 좋음
    if adaptive:
        # 조명 불균일/스캔 얼룩에 강함
        return cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35, 15
        )
    # 전역 threshold + Otsu
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


def _remove_lines(binary: np.ndarray) -> np.ndarray:
    """
    표의 가로/세로 선을 약하게 제거해서 글자 인식률을 올림.
    (선이 너무 강하면 글자 덩어리 분할이 망가짐)
    """
    inv = 255 - binary  # 글자/선이 흰색이 되게

    # 커널 크기는 이미지 크기에 비례하게
    h, w = binary.shape[:2]
    hk = max(10, w // 100)  # 가로선 제거용
    vk = max(10, h // 100)  # 세로선 제거용

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk))

    # 선 성분 추출
    horizontal_lines = cv2.morphologyEx(inv, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical_lines = cv2.morphologyEx(inv, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    lines = cv2.bitwise_or(horizontal_lines, vertical_lines)

    # 원본에서 선을 빼준다(복원은 inpaint로 자연스럽게)
    cleaned_inv = cv2.inpaint(inv, lines, inpaintRadius=2, flags=cv2.INPAINT_TELEA)

    # 다시 binary 형태로
    cleaned = 255 - cleaned_inv
    return cleaned


def _deskew(binary: np.ndarray) -> np.ndarray:
    """
    간단한 deskew. (기울기 심하면 개선, 애매하면 오히려 악화 가능)
    """
    # 글자가 검은색이어야 findNonZero가 유리하므로 invert 고려
    inv = 255 - binary
    coords = cv2.findNonZero(inv)
    if coords is None:
        return binary

    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    # OpenCV angle 규칙 보정
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # 너무 작은 각도는 무시
    if abs(angle) < 0.3:
        return binary

    h, w = binary.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def preprocess_for_ocr(pil_img: Image.Image, opt: PreprocessOptions) -> np.ndarray:
    """
    Tesseract에 넣기 좋은 형태(그레이/바이너리)로 전처리한 OpenCV 이미지 반환.
    반환은 uint8 단일 채널 이미지(0~255).
    """
    bgr = _pil_to_bgr(pil_img)
    bgr = _upscale(bgr, opt.upscale)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    if opt.denoise:
        gray = _maybe_denoise(gray)

    if opt.binarize:
        img = _binarize(gray, adaptive=opt.adaptive_thresh)
    else:
        img = gray

    if opt.remove_table_lines and opt.binarize:
        img = _remove_lines(img)

    if opt.deskew and opt.binarize:
        img = _deskew(img)

    return img


# -----------------------------
# OCR: string vs data
# -----------------------------
@dataclass
class OcrOptions:
    lang: str = "kor+eng"
    oem: int = 1
    psm_candidates: Tuple[int, ...] = (6, 4, 1, 11)  # 문서/다단/자동/스파스
    use_data_mode: bool = True                      # 표/혼합 문서에서 유리
    min_conf: int = 35                              # data mode에서 conf 필터
    keep_newlines: bool = True


def _tess_config(oem: int, psm: int) -> str:
    return f"--oem {oem} --psm {psm}"


def ocr_string(img_u8: np.ndarray, lang: str, config: str) -> str:
    # OpenCV 이미지를 PIL로 변환 (tesseract가 더 안정적인 경우가 많음)
    pil = Image.fromarray(img_u8)
    return pytesseract.image_to_string(pil, lang=lang, config=config)


def ocr_data_reconstruct_lines(img_u8: np.ndarray, lang: str, config: str, min_conf: int) -> str:
    """
    image_to_data로 (word 단위 + 좌표 + confidence) 가져와서
    - conf 낮은 토큰 제거
    - line_num 기반으로 라인 재조립
    표 문서에서 "이상한 난수화"를 줄이는 데 도움 되는 편.
    """
    pil = Image.fromarray(img_u8)
    data = pytesseract.image_to_data(pil, lang=lang, config=config, output_type=pytesseract.Output.DICT)

    n = len(data.get("text", []))
    if n == 0:
        return ""

    lines: Dict[Tuple[int, int, int], List[Tuple[int, str]]] = {}
    # key: (block_num, par_num, line_num), value: [(left, text), ...]
    for i in range(n):
        txt = (data["text"][i] or "").strip()
        if not txt:
            continue
        try:
            conf = int(float(data["conf"][i]))
        except Exception:
            conf = -1
        if conf != -1 and conf < min_conf:
            continue

        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        left = int(data["left"][i])
        lines.setdefault(key, []).append((left, txt))

    if not lines:
        return ""

    # 라인 정렬: block, par, line 순
    out_lines: List[str] = []
    for key in sorted(lines.keys()):
        words = sorted(lines[key], key=lambda x: x[0])  # left 기준
        out_lines.append(" ".join(w for _, w in words))

    return "\n".join(out_lines)


def extract_text_best_effort(
    pil_img: Image.Image,
    pp: PreprocessOptions,
    ocr_opt: OcrOptions,
) -> Tuple[str, Dict[str, float]]:
    """
    PSM 후보를 여러 개 돌려보고, 가장 점수 높은 결과를 선택.
    - data_mode 결과와 string 결과 중 더 나은 쪽을 선택(옵션)
    반환: (best_text, debug_scores)
    """
    img_u8 = preprocess_for_ocr(pil_img, pp)

    best_text = ""
    best_score = float("-inf")
    debug: Dict[str, float] = {}

    for psm in ocr_opt.psm_candidates:
        cfg = _tess_config(ocr_opt.oem, psm)

        # 1) 기본 string mode
        try:
            txt_s = ocr_string(img_u8, lang=ocr_opt.lang, config=cfg)
        except Exception:
            txt_s = ""
        score_s = _basic_text_quality_score(txt_s)
        debug[f"psm{psm}_string"] = score_s

        # 2) data mode (표/혼합 문서에 도움)
        txt_d = ""
        score_d = float("-inf")
        if ocr_opt.use_data_mode:
            try:
                txt_d = ocr_data_reconstruct_lines(img_u8, lang=ocr_opt.lang, config=cfg, min_conf=ocr_opt.min_conf)
            except Exception:
                txt_d = ""
            score_d = _basic_text_quality_score(txt_d)
            debug[f"psm{psm}_data"] = score_d

        # 후보들 중 최고를 채택
        if score_s > best_score:
            best_score = score_s
            best_text = txt_s
        if score_d > best_score:
            best_score = score_d
            best_text = txt_d

    if not ocr_opt.keep_newlines:
        best_text = " ".join(best_text.split())

    return best_text, debug


# -----------------------------
# Public API
# -----------------------------
def extract_text_from_image(
    image_path: PathLike,
    lang: str = "kor+eng",
    preprocess: Optional[PreprocessOptions] = None,
    ocr_options: Optional[OcrOptions] = None,
) -> str:
    """
    단일 이미지에서 텍스트 추출 (전처리 + PSM 자동 스윕 + data mode 옵션)

    Args:
        image_path: 이미지 파일 경로
        lang: OCR 언어 (기본 "kor+eng")
        preprocess: 전처리 옵션
        ocr_options: OCR 옵션

    Returns:
        추출된 텍스트
    """
    p = _to_path(image_path)
    _ensure_exists(p)

    pp = preprocess or PreprocessOptions()
    oo = ocr_options or OcrOptions()
    oo.lang = lang  # 호출자가 lang을 넘기면 반영

    try:
        with Image.open(p) as pil_img:
            text, _debug = extract_text_best_effort(pil_img, pp, oo)
        return text
    except Exception as exc:
        raise RuntimeError(f"이미지 {p}에서 텍스트 추출 실패: {exc}") from exc


def extract_text_from_images(
    image_paths: Sequence[PathLike],
    lang: str = "kor+eng",
    preprocess: Optional[PreprocessOptions] = None,
    ocr_options: Optional[OcrOptions] = None,
    show_debug: bool = False,
) -> TextDict:
    """
    여러 이미지에서 텍스트 추출

    Args:
        image_paths: 이미지 파일 경로 리스트
        lang: OCR 언어 (기본 "kor+eng")
        preprocess: 전처리 옵션
        ocr_options: OCR 옵션
        show_debug: psm별 점수 출력

    Returns:
        {이미지 경로(str): 추출된 텍스트}
    """
    paths = [_to_path(p) for p in image_paths]

    pp = preprocess or PreprocessOptions()
    oo = ocr_options or OcrOptions()
    oo.lang = lang

    print(f"🔍 OCR 텍스트 추출 시작 (언어: {lang})")
    print(f"   총 {len(paths)}개 이미지 처리 예정\n")

    results: TextDict = {}

    for i, p in enumerate(paths, start=1):
        print(f"  [{i}/{len(paths)}] 처리 중: {p.name}")
        try:
            _ensure_exists(p)
            with Image.open(p) as pil_img:
                text, debug_scores = extract_text_best_effort(pil_img, pp, oo)

            results[str(p)] = text
            print(f"    ✓ 추출된 텍스트: {len(text)} 글자")

            if show_debug:
                # 상위 5개만 보기 좋게
                top = sorted(debug_scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
                top_str = ", ".join(f"{k}:{v:.3f}" for k, v in top)
                print(f"    · 점수(top): {top_str}")

        except Exception as exc:
            print(f"    ✗ 오류: {exc}")
            results[str(p)] = ""

    print(f"\n✓ OCR 추출 완료\n")
    return results


def save_extracted_text(text_dict: TextDict, output_path: PathLike = "output/extracted_text.txt") -> None:
    """
    추출된 텍스트를 파일로 저장
    """
    output_path = _to_path(output_path)
    output_dir = output_path.parent

    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 디렉토리 생성: {output_dir}")

    print(f"💾 텍스트 파일 저장 중: {output_path}")

    with output_path.open("w", encoding="utf-8") as f:
        for i, (image_path, text) in enumerate(sorted(text_dict.items()), start=1):
            page_name = Path(image_path).name
            f.write(f"{'='*80}\n")
            f.write(f"페이지 {i}: {page_name}\n")
            f.write(f"{'='*80}\n\n")
            f.write(text)
            f.write("\n\n\n")

    print(f"✓ 저장 완료: {output_path}\n")


# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":  # pragma: no cover - CLI helper
    import argparse
    import glob
    import sys

    parser = argparse.ArgumentParser(description="OpenCV 전처리 + PSM 자동 스윕 + data mode OCR")
    parser.add_argument("image_dir", type=str, help="이미지 디렉토리 (예: ./pages)")
    parser.add_argument("--lang", type=str, default="kor+eng", help='OCR 언어 (기본 "kor+eng")')
    parser.add_argument("--ext", type=str, default="png", help='확장자 (기본 "png")')
    parser.add_argument("--out", type=str, default="output/extracted_text.txt", help="출력 txt 경로")
    parser.add_argument("--no-lines", action="store_true", help="표 선 제거 끄기")
    parser.add_argument("--deskew", action="store_true", help="deskew 켜기(느릴 수 있음)")
    parser.add_argument("--upscale", type=float, default=2.0, help="업스케일 배수 (기본 2.0)")
    parser.add_argument("--no-data", action="store_true", help="image_to_data 모드 끄기")
    parser.add_argument("--min-conf", type=int, default=35, help="data mode 최소 confidence (기본 35)")
    parser.add_argument("--debug", action="store_true", help="psm별 점수 출력")

    args = parser.parse_args()

    image_dir = _to_path(args.image_dir)
    if not image_dir.exists():
        print(f"오류: 디렉토리를 찾을 수 없습니다: {image_dir}")
        sys.exit(1)

    pattern = str(image_dir / f"*.{args.ext.lstrip('.')}")
    image_files = sorted(glob.glob(pattern))

    if not image_files:
        print(f"오류: {image_dir}에서 '*.{args.ext}' 파일을 찾을 수 없습니다.")
        sys.exit(1)

    pp = PreprocessOptions(
        upscale=args.upscale,
        remove_table_lines=not args.no_lines,
        deskew=args.deskew,
    )
    oo = OcrOptions(
        lang=args.lang,
        use_data_mode=not args.no_data,
        min_conf=args.min_conf,
    )

    try:
        text_results = extract_text_from_images(
            image_files,
            lang=args.lang,
            preprocess=pp,
            ocr_options=oo,
            show_debug=args.debug,
        )
        save_extracted_text(text_results, args.out)
        print("텍스트 추출 및 저장 완료!")
    except Exception as exc:
        print(f"오류: {exc}")
        sys.exit(1)
