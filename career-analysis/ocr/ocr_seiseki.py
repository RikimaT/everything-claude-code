#!/usr/bin/env python3
"""
ocr_seiseki.py

成績表（定期テスト等）のスキャンPDFからOCRでデータを抽出する。

抽出項目:
  - 生徒名
  - 各教科の点数（国語/数学/英語/理科/社会）
  - 5科合計
  - 中学校名・学年・テスト回（可能な場合）

使い方:
  python ocr_seiseki.py <input_pdf> [--output output.csv]
  python ocr_seiseki.py <input_dir> --batch  # フォルダ内の全PDFを処理

前提パッケージ:
  pip install pytesseract pdf2image Pillow

前提ソフトウェア:
  - Tesseract OCR (日本語言語パック: tesseract-ocr-jpn)
  - poppler-utils (pdf2imageが使用)
"""

import argparse
import csv
import glob
import os
import re
import sys

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
except ImportError:
    print("必要なパッケージをインストールしてください:")
    print("  pip install pytesseract pdf2image Pillow")
    print("  sudo apt install tesseract-ocr tesseract-ocr-jpn poppler-utils")
    sys.exit(1)


def extract_text_from_pdf(pdf_path, dpi=300):
    """PDFを画像に変換し、OCRでテキストを抽出する。"""
    images = convert_from_path(pdf_path, dpi=dpi)
    all_text = []
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image, lang="jpn")
        all_text.append(text)
    return all_text


def infer_student_info_from_path(pdf_path):
    """ファイルパスから生徒名・学年・年度を推定する。

    フォルダ構造の例:
      成績表/2024/3年/生徒名/scan.pdf
      成績表/生徒名/scan.pdf
    """
    parts = pdf_path.replace("\\", "/").split("/")
    info = {"生徒名": "", "学年": "", "年度": ""}

    for i, part in enumerate(parts):
        # Year folder (e.g., "2024")
        if re.match(r"^20\d{2}$", part):
            info["年度"] = part

        # Grade folder (e.g., "3年", "1年")
        if re.match(r"^[1-3]年$", part):
            info["学年"] = f"中{part[0]}"

        # Student name is typically the folder right before the PDF file
        if part.endswith(".pdf") and i > 0:
            parent = parts[i - 1]
            if not re.match(r"^(20\d{2}|[1-3]年|成績表|全員)$", parent):
                info["生徒名"] = parent

    return info


def parse_seiseki_text(text, source_file="", path_info=None):
    """成績表テキストから教科別点数を抽出する。

    成績表のフォーマットは中学校によって異なるため、
    複数のパターンでマッチを試みる。

    Returns:
        list of dict: 抽出された成績データ
    """
    results = []

    # Common patterns for score extraction
    subjects_patterns = {
        "国語": [
            re.compile(r"国語[:\s]*(\d{1,3})"),
            re.compile(r"国\s*語\s+(\d{1,3})"),
        ],
        "数学": [
            re.compile(r"数学[:\s]*(\d{1,3})"),
            re.compile(r"数\s*学\s+(\d{1,3})"),
        ],
        "英語": [
            re.compile(r"英語[:\s]*(\d{1,3})"),
            re.compile(r"英\s*語\s+(\d{1,3})"),
        ],
        "理科": [
            re.compile(r"理科[:\s]*(\d{1,3})"),
            re.compile(r"理\s*科\s+(\d{1,3})"),
        ],
        "社会": [
            re.compile(r"社会[:\s]*(\d{1,3})"),
            re.compile(r"社\s*会\s+(\d{1,3})"),
        ],
    }

    total_pattern = re.compile(r"(?:合計|5科|5教科|総合)[:\s]*(\d{1,3})")
    name_pattern = re.compile(r"(?:氏名|名前|生徒名)[:\s]*(.+?)[\s\n]")
    test_pattern = re.compile(
        r"(?:第(\d)[回期]|(\d)学期|中間|期末|学年末)"
    )

    record = {
        "生徒名": path_info.get("生徒名", "") if path_info else "",
        "学年": path_info.get("学年", "") if path_info else "",
        "中学校名": "",  # Usually needs manual input
        "データ種別": "定期テスト",
        "国語": "",
        "数学": "",
        "英語": "",
        "理科": "",
        "社会": "",
        "5科合計": "",
        "Vもし偏差値": "",  # Not applicable for school tests
        "テスト回/年度": path_info.get("年度", "") if path_info else "",
        "読取元ファイル名": source_file,
    }

    # Try to extract student name from text if not from path
    if not record["生徒名"]:
        name_match = name_pattern.search(text)
        if name_match:
            record["生徒名"] = name_match.group(1).strip()

    # Extract subject scores
    found_any = False
    for subject, patterns in subjects_patterns.items():
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    record[subject] = str(score)
                    found_any = True
                break

    # Extract total score
    total_match = total_pattern.search(text)
    if total_match:
        record["5科合計"] = total_match.group(1)
        found_any = True

    # Extract test period
    test_match = test_pattern.search(text)
    if test_match:
        if record["テスト回/年度"]:
            record["テスト回/年度"] += " "
        record["テスト回/年度"] += test_match.group(0)

    if found_any:
        results.append(record)

    return results


def process_pdf(pdf_path, output_csv=None):
    """1つのPDFを処理してデータを抽出する。"""
    print(f"Processing: {pdf_path}")

    pages_text = extract_text_from_pdf(pdf_path)
    all_records = []

    source_file = os.path.basename(pdf_path)
    path_info = infer_student_info_from_path(pdf_path)

    for i, text in enumerate(pages_text):
        print(f"  Page {i + 1}: {len(text)} characters extracted")
        records = parse_seiseki_text(text, source_file, path_info)
        all_records.extend(records)

    print(f"  Total records extracted: {len(all_records)}")

    if not all_records:
        print("  WARNING: No records extracted. OCR may need manual verification.")

    return all_records


def process_batch(input_dir, output_csv):
    """フォルダ内の全PDFを一括処理する。"""
    pdf_files = glob.glob(os.path.join(input_dir, "**/*.pdf"), recursive=True)
    pdf_files += glob.glob(os.path.join(input_dir, "**/*.PDF"), recursive=True)

    if not pdf_files:
        print(f"No PDF files found in: {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files")
    all_records = []

    for pdf_path in sorted(pdf_files):
        records = process_pdf(pdf_path)
        all_records.extend(records)

    save_csv(all_records, output_csv)
    return all_records


def save_csv(records, output_csv):
    """抽出結果をCSVに保存する。"""
    if not records:
        print("No records to save.")
        return

    fieldnames = [
        "生徒名", "学年", "中学校名", "データ種別",
        "国語", "数学", "英語", "理科", "社会",
        "5科合計", "Vもし偏差値", "テスト回/年度", "読取元ファイル名",
    ]

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\nOutput: {output_csv}")
    print(f"Total records: {len(records)}")
    print()
    print("=" * 60)
    print("重要: OCR結果は田中氏に確認を取ってから")
    print("スプレッドシートに入力してください。")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="成績表PDFからOCRでデータを抽出"
    )
    parser.add_argument("input_path", help="入力PDFファイルまたはフォルダのパス")
    parser.add_argument("--output", "-o", help="出力CSVファイルのパス")
    parser.add_argument(
        "--batch", action="store_true",
        help="フォルダ内の全PDFを一括処理"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print(f"Error: Path not found: {args.input_path}")
        sys.exit(1)

    if args.batch or os.path.isdir(args.input_path):
        output = args.output or "seiseki_extracted.csv"
        process_batch(args.input_path, output)
    else:
        output = args.output
        if output is None:
            base = os.path.splitext(args.input_path)[0]
            output = f"{base}_extracted.csv"
        records = process_pdf(args.input_path)
        save_csv(records, output)


if __name__ == "__main__":
    main()
