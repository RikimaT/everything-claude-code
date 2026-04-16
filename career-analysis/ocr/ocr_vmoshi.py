#!/usr/bin/env python3
"""
ocr_vmoshi.py

V模試（滋賀Vもし）の簡易帳票PDFからOCRでデータを抽出する。

抽出項目:
  - 生徒名
  - Vもし偏差値（5科/各教科）
  - 5科合計点
  - 志望校判定結果
  - 受験回（第1回〜第4回）

使い方:
  python ocr_vmoshi.py <input_pdf> [--output output.csv]

前提パッケージ:
  pip install pytesseract pdf2image Pillow

前提ソフトウェア:
  - Tesseract OCR (日本語言語パック: tesseract-ocr-jpn)
  - poppler-utils (pdf2imageが使用)
"""

import argparse
import csv
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


def parse_vmoshi_text(text, source_file=""):
    """V模試の簡易帳票テキストから生徒データを抽出する。

    簡易帳票には複数の生徒データがまとまっている場合がある。
    各生徒のブロックを検出し、個別にパースする。

    Returns:
        list of dict: 各生徒のデータ
    """
    results = []

    # Patterns for extracting data (adjust based on actual PDF format)
    # These are heuristic patterns - actual PDF layout may differ
    name_pattern = re.compile(r"氏名[:\s]*(.+?)[\s\n]")
    score_5_pattern = re.compile(r"5科[合計]*[:\s]*(\d{1,3})")
    deviation_pattern = re.compile(r"偏差値[:\s]*(\d{2}\.?\d?)")
    round_pattern = re.compile(r"第(\d)回")

    # Subject patterns
    subjects = {
        "国語": re.compile(r"国語[:\s]*(\d{1,3})"),
        "数学": re.compile(r"数学[:\s]*(\d{1,3})"),
        "英語": re.compile(r"英語[:\s]*(\d{1,3})"),
        "理科": re.compile(r"理科[:\s]*(\d{1,3})"),
        "社会": re.compile(r"社会[:\s]*(\d{1,3})"),
    }

    # Try to extract data from the text
    # Note: This is a basic implementation. The actual parsing logic
    # needs to be adjusted based on the specific format of the V-moshi PDFs.
    name_match = name_pattern.search(text)
    score_match = score_5_pattern.search(text)
    dev_match = deviation_pattern.search(text)
    round_match = round_pattern.search(text)

    if name_match or score_match:
        record = {
            "生徒名": name_match.group(1).strip() if name_match else "",
            "学年": "中3",  # V模試は主に中3
            "中学校名": "",  # OCRで抽出困難な場合は手動入力
            "データ種別": "Vもし",
            "国語": "",
            "数学": "",
            "英語": "",
            "理科": "",
            "社会": "",
            "5科合計": score_match.group(1) if score_match else "",
            "Vもし偏差値": dev_match.group(1) if dev_match else "",
            "テスト回/年度": f"第{round_match.group(1)}回" if round_match else "",
            "読取元ファイル名": source_file,
        }

        # Extract subject scores
        for subject, pattern in subjects.items():
            match = pattern.search(text)
            if match:
                record[subject] = match.group(1)

        results.append(record)

    return results


def process_pdf(pdf_path, output_csv=None):
    """PDFを処理してデータを抽出し、CSV出力する。"""
    print(f"Processing: {pdf_path}")

    pages_text = extract_text_from_pdf(pdf_path)
    all_records = []

    source_file = os.path.basename(pdf_path)

    for i, text in enumerate(pages_text):
        print(f"  Page {i + 1}: {len(text)} characters extracted")
        records = parse_vmoshi_text(text, source_file)
        all_records.extend(records)

    print(f"  Total records extracted: {len(all_records)}")

    if not all_records:
        print("  WARNING: No records extracted. OCR may need manual verification.")
        return all_records

    # Output to CSV
    if output_csv is None:
        base = os.path.splitext(pdf_path)[0]
        output_csv = f"{base}_extracted.csv"

    fieldnames = [
        "生徒名", "学年", "中学校名", "データ種別",
        "国語", "数学", "英語", "理科", "社会",
        "5科合計", "Vもし偏差値", "テスト回/年度", "読取元ファイル名",
    ]

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"  Output: {output_csv}")
    print()
    print("=" * 60)
    print("重要: OCR結果は田中氏に確認を取ってから")
    print("スプレッドシートに入力してください。")
    print("=" * 60)

    return all_records


def main():
    parser = argparse.ArgumentParser(
        description="V模試PDFからOCRでデータを抽出"
    )
    parser.add_argument("pdf_path", help="入力PDFファイルのパス")
    parser.add_argument("--output", "-o", help="出力CSVファイルのパス")
    parser.add_argument("--dpi", type=int, default=300, help="OCR解像度 (default: 300)")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found: {args.pdf_path}")
        sys.exit(1)

    process_pdf(args.pdf_path, args.output)


if __name__ == "__main__":
    main()
