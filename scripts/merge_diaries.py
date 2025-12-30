#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日记整理脚本
将指定年份的所有日记按时间排序整理到一个md文件中
"""

import argparse
import re
from pathlib import Path
from datetime import datetime


def parse_diary_file(file_path):
    """
    解析单个日记文件

    Args:
        file_path: 日记文件路径

    Returns:
        (date, content) 元组，其中 date 是日期字符串，content 是去除 wordCount 的内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML front matter 中的日期
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)

        if not yaml_match:
            print(f"警告: 文件 {file_path.name} 没有找到 YAML front matter")
            return None, None

        yaml_content = yaml_match.group(1)
        body_content = yaml_match.group(2)

        # 移除所有markdown图片（使用 ![]() 格式）
        body_content = re.sub(r'!\[.*?\]\(.*?\)', '', body_content)

        # 移除空的details标签（图片被删除后可能留下空标签）
        body_content = re.sub(r'<details>\s*</details>', '', body_content, flags=re.DOTALL)
        body_content = re.sub(r'<details>\s*<summary>.*?</summary>\s*</details>', '', body_content, flags=re.DOTALL)

        # 移除单独的summary标签
        body_content = re.sub(r'<summary>.*?</summary>', '', body_content, flags=re.DOTALL)

        # 移除details和/details标签本身，但保留中间可能有的文本内容
        body_content = re.sub(r'</?details>', '', body_content)

        # 清理多余的空行
        body_content = re.sub(r'\n{3,}', '\n\n', body_content)

        # 提取日期
        date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', yaml_content)
        if not date_match:
            print(f"警告: 文件 {file_path.name} 没有找到日期")
            return None, None

        date_str = date_match.group(1)

        # 构建新的 YAML front matter（只包含 date）
        new_yaml = f"---\ndate: {date_str}\n---"

        # 组合新内容
        new_content = f"{new_yaml}\n{body_content}"

        return date_str, new_content

    except Exception as e:
        print(f"错误: 读取文件 {file_path} 失败: {e}")
        return None, None


def merge_diaries_by_year(year, diaries_dir, output_dir):
    """
    合并指定年份的所有日记

    Args:
        year: 年份
        diaries_dir: 日记目录路径
        output_dir: 输出目录路径
    """
    diaries_path = Path(diaries_dir)
    output_path = Path(output_dir)

    print(f"正在查找 {year} 年的日记文件...")
    print(f"日记目录: {diaries_path}")

    # 查找该年份的所有日记文件
    pattern = f"{year}-*.md"
    diary_files = list(diaries_path.glob(pattern))

    if not diary_files:
        print(f"错误: 没有找到 {year} 年的日记文件")
        return

    print(f"找到 {len(diary_files)} 个日记文件")

    # 解析所有日记文件
    diaries = []
    for file_path in diary_files:
        date_str, content = parse_diary_file(file_path)
        if date_str and content:
            diaries.append((date_str, content))

    if not diaries:
        print("错误: 没有成功解析任何日记文件")
        return

    print(f"成功解析 {len(diaries)} 个日记文件")

    # 按日期排序
    diaries.sort(key=lambda x: x[0])
    print(f"日期范围: {diaries[0][0]} 到 {diaries[-1][0]}")

    # 创建输出文件
    output_file = output_path / f"{year}_diaries.md"

    print(f"\n正在生成合并文件: {output_file}")

    # 写入合并后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, (date_str, content) in enumerate(diaries):
            f.write(content)
            f.write("\n")

            # 在每篇日记之间添加分隔符（最后一篇除外）
            if i < len(diaries) - 1:
                f.write("\n---\n\n")

    print(f"\n完成! 已将 {len(diaries)} 篇日记合并到: {output_file}")

    # 统计信息
    total_chars = sum(len(content) for _, content in diaries)
    print(f"\n统计信息:")
    print(f"  总篇数: {len(diaries)}")
    print(f"  总字符数: {total_chars:,}")
    print(f"  平均每篇: {total_chars // len(diaries):,} 字符")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='日记整理工具：将指定年份的日记合并到一个文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s 2025              # 整理2025年的日记
  %(prog)s 2024              # 整理2024年的日记
  %(prog)s 2025 --output ./  # 指定输出目录
        """
    )
    parser.add_argument('year', type=int, help='要整理的年份，如 2025')
    parser.add_argument('--output', '-o', default=None,
                        help='输出目录（默认为项目根目录）')

    args = parser.parse_args()

    # 验证年份
    current_year = datetime.now().year
    if args.year < 2000 or args.year > current_year + 1:
        print(f"错误: 年份 {args.year} 不合理（应在 2000-{current_year + 1} 之间）")
        return

    # 获取项目目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    diaries_dir = project_root / 'diaries'
    output_dir = Path(args.output) if args.output else project_root

    # 检查目录是否存在
    if not diaries_dir.exists():
        print(f"错误: 日记目录不存在: {diaries_dir}")
        return

    if not output_dir.exists():
        print(f"错误: 输出目录不存在: {output_dir}")
        return

    # 打印信息
    print("=" * 60)
    print(f"日记整理工具 - {args.year} 年")
    print("=" * 60)

    # 执行合并
    merge_diaries_by_year(args.year, diaries_dir, output_dir)

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
