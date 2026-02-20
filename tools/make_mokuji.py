#!/usr/bin/env python3
import os
import re

def extract_headings(file_path: str) -> list[tuple[int, str]]:
    """
    マークダウンファイルから見出しを抽出する。
    コードブロック内の見出しは無視する。
    """
    headings = []
    in_code_block = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            match = re.match(r'^(#+)\s+(.*)', line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                headings.append((level, title))
    return headings

def sort_directories_by_number(directories: list[str]) -> list[str]:
    """
    ディレクトリ名の数値プレフィックスでソートする。
    数値がない場合は無限大として扱う。
    """
    def extract_number(directory: str) -> float:
        match = re.match(r'^(\d+)-', directory)
        return int(match.group(1)) if match else float('inf')

    return sorted(directories, key=extract_number)

def generate_toc(directory: str, max_level: int = 2) -> str:
    """
    指定されたディレクトリ内のマークダウンファイルから目次を生成する。
    """
    toc = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in sort_directories_by_number(dirs)]  # '0-prologue'を除外
        for file in sorted(files):
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                html_path = relative_path.replace('.md', '.html')
                headings = extract_headings(file_path)
                if headings:
                    for level, title in headings:
                        if level > max_level:  # 指定された深さを超える見出しは無視
                            continue
                        indent = '  ' * (level - 1)
                        anchor = title.lower().replace(' ', '-').replace('.', '').replace('、', '')
                        toc.append(f"{indent}- [{title}](../{html_path}#{anchor})")
    return '\n'.join(toc)

def update_toc_in_file(file_path: str, toc: str, depth: int) -> None:
    """
    指定されたファイル内のマーカー間に目次を挿入する。
    """
    start_marker = f'<!-- ここから目次(深さ={depth}) -->'
    end_marker = '<!-- ここまで目次 -->'

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # 行を正規化して余分な空白や改行を無視
    normalized_content = [line.strip() for line in content]

    start_indices = [i for i, line in enumerate(normalized_content) if line == start_marker]
    end_indices = [i for i, line in enumerate(normalized_content) if line == end_marker]

    for start_index in start_indices:
        # 対応する終了マーカーを探す
        end_index = next((i for i in end_indices if i > start_index), None)
        if end_index is not None:
            content = content[:start_index + 1] + [toc + '\n'] + content[end_index:]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(content)

def main() -> None:
    """
    メイン処理：目次を生成し、指定されたファイルに挿入する。
    """
    articles_dir = os.path.join(os.path.dirname(__file__), '../articles')
    toc_file_path = os.path.join(articles_dir, '0-prologue/README.md')

    # 深さ2の目次を生成して挿入
    toc_depth_2 = generate_toc(articles_dir, max_level=2)
    update_toc_in_file(toc_file_path, toc_depth_2, depth=2)

    # # 深さ1の目次を生成して挿入
    # toc_depth_1 = generate_toc(articles_dir, max_level=1)
    # update_toc_in_file(toc_file_path, toc_depth_1, depth=1)

    # 標準出力に目次を出力
    print("TOC (Depth 2):\n", toc_depth_2)
    # print("TOC (Depth 1):\n", toc_depth_1)

if __name__ == "__main__":
    main()
