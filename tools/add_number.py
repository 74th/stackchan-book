import sys
import os
import pathlib
import re

articles_dir = pathlib.Path(__file__).resolve().parent.parent / "articles"

def main():
    if len(sys.argv) != 2:
        print("Usage: python add_number.py <chapter_number>")
        sys.exit(1)

    chapter_number = sys.argv[1]

    matching_dirs = [d for d in articles_dir.iterdir() if d.is_dir() and d.name.startswith(f"{chapter_number}-")]
    if not matching_dirs:
        print(f"Error: No directory starting with '{chapter_number}-' found in {articles_dir}.")
        sys.exit(1)
    chapter_dir = matching_dirs[0]  # Take the first matching directory

    chapter_number = int(sys.argv[1])
    chapter_markdown = articles_dir / matching_dirs[0] / "README.md"
    print(f"Chapter markdown: {chapter_dir}")

    if not chapter_markdown.exists():
        print(f"Error: README.md not found in {chapter_dir}.")
        sys.exit(1)

    with open(chapter_markdown, "r") as f:
        lines = f.readlines()

    sub_chapter_number = 1
    in_code_block = False  # コードブロック内かどうかを追跡するフラグ

    for i, line in enumerate(lines):
        # コードブロックの開始または終了を検出
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # コードブロック内の場合はスキップ
        if in_code_block:
            continue

        # 章番号あり（例: # 1. タイトル）のパターン
        match_main_with_number = re.match(r"# (\d+)\.\s+(.+)", line)
        # サブタイトル形式（例: # 1.1. サブタイトル）のパターン
        match_sub_with_number = re.match(r"## (\d+)\.(\d+)\.\s+(.+)", line)
        # 章番号なし（例: # タイトル）のパターン
        match_without_number = re.match(r"# (.+)", line)
        # サブタイトル形式、番号なし（例: ## サブタイトル）のパターン
        match_sub_without_number = re.match(r"## (.+)", line)

        if match_sub_with_number:
            # サブタイトルの場合（例: # 1.1. サブタイトル）
            extracted_title = match_sub_with_number.group(3)
            lines[i] = f"## {chapter_number}.{sub_chapter_number}. {extracted_title}\n"
            sub_chapter_number += 1
        elif match_main_with_number:
            # メインタイトルの場合（例: # 1. タイトル）
            extracted_title = match_main_with_number.group(2)  # タイトル部分を抽出
            lines[i] = f"# {chapter_number}. {extracted_title}\n"
            # サブチャプター番号をリセット
            sub_chapter_number = 1
        elif match_without_number and not re.match(r"# \d+\.(\d+)?\.?", line):
            # 章番号がない場合（かつ、"# 数字." や "# 数字.数字." の形式でない場合）
            extracted_title = match_without_number.group(1)
            lines[i] = f"# {chapter_number}. {extracted_title}\n"
            # サブチャプター番号をリセット
            sub_chapter_number = 1
        elif match_sub_without_number and not re.match(r"## \d+\.(\d+)?\.?", line):
            # サブタイトルで番号がない場合
            extracted_title = match_sub_without_number.group(1)
            lines[i] = f"## {chapter_number}.{sub_chapter_number}. {extracted_title}\n"
            sub_chapter_number += 1

    # 修正したファイルを保存
    with open(chapter_markdown, "w") as f:
        f.writelines(lines)

    print(f"Updated chapter numbers in {chapter_markdown}")


if __name__ == "__main__":
    main()