#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日记词云生成脚本
读取 diaries 目录下的所有日记文件，生成词云图片
"""

import os
import re
import argparse
from pathlib import Path
from collections import Counter
import jieba
import jieba.posseg as pseg
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def load_stopwords(stopwords_file):
    """
    从文件加载停用词
    
    Args:
        stopwords_file: 停用词文件路径
    
    Returns:
        停用词集合
    """
    stopwords = set()
    try:
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:  # 跳过空行
                    stopwords.add(word)
        print(f"已加载 {len(stopwords)} 个停用词")
    except Exception as e:
        print(f"警告: 加载停用词文件失败: {e}")
        print("将使用空停用词表")
    return stopwords


def read_diary_files(diaries_dir):
    """
    读取 diaries 目录下的所有 markdown 文件
    
    Args:
        diaries_dir: 日记目录路径
    
    Returns:
        所有日记内容的组合文本
    """
    diaries_path = Path(diaries_dir)
    all_text = []
    
    # 获取所有 .md 文件并排序
    md_files = sorted(diaries_path.glob('*.md'))
    
    print(f"找到 {len(md_files)} 个日记文件")
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 移除 YAML front matter
                content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
                
                # 移除 markdown 图片链接和其他特殊格式
                content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
                content = re.sub(r'\[.*?\]\(.*?\)', '', content)
                content = re.sub(r'<details>.*?</details>', '', content, flags=re.DOTALL)
                content = re.sub(r'<summary>.*?</summary>', '', content)
                
                # 移除 markdown 标题符号
                content = re.sub(r'#+\s+', '', content)
                
                # 移除多余的空行和特殊符号
                content = re.sub(r'\n+', '\n', content)
                content = re.sub(r'-{2,}', '', content)
                
                all_text.append(content.strip())
                
        except Exception as e:
            print(f"读取文件 {md_file} 时出错: {e}")
    
    return '\n'.join(all_text)


def segment_text(text, stopwords, noun_only=False):
    """
    使用 jieba 进行中文分词
    
    Args:
        text: 待分词的文本
        stopwords: 停用词集合
        noun_only: 是否只提取名词
    
    Returns:
        分词后的词语列表
    """
    filtered_words = []
    
    if noun_only:
        # 使用词性标注，只提取名词
        print("正在使用词性标注模式，只提取名词...")
        words_with_pos = pseg.cut(text)
        
        for word, flag in words_with_pos:
            word = word.strip()
            # 过滤条件：
            # 1. 词性为名词（n开头）
            # 2. 长度大于1
            # 3. 不在停用词表中
            # 4. 不是纯数字
            # 5. 不是纯空格或标点
            if (flag.startswith('n') and  # 名词词性
                len(word) > 1 and 
                word not in stopwords and 
                not word.isdigit() and 
                not re.match(r'^[\s\W]+$', word)):
                filtered_words.append(word)
    else:
        # 普通分词模式
        words = jieba.cut(text)
        
        for word in words:
            word = word.strip()
            # 过滤条件：
            # 1. 长度大于1
            # 2. 不在停用词表中
            # 3. 不是纯数字
            # 4. 不是纯空格或标点
            if (len(word) > 1 and 
                word not in stopwords and 
                not word.isdigit() and 
                not re.match(r'^[\s\W]+$', word)):
                filtered_words.append(word)
    
    return filtered_words


def save_word_freq_to_file(words, freq_file):
    """
    保存词频列表到文件
    
    Args:
        words: 词语列表
        freq_file: 输出文件路径
    
    Returns:
        词频统计字典
    """
    # 统计词频
    word_freq = Counter(words)
    
    print(f"\n总共提取了 {len(words)} 个有效词语")
    print(f"去重后有 {len(word_freq)} 个不同的词语")
    print("\n词频 Top 20:")
    for word, freq in word_freq.most_common(20):
        print(f"  {word}: {freq}")
    
    # 保存到文件
    with open(freq_file, 'w', encoding='utf-8') as f:
        for word, freq in word_freq.most_common():
            f.write(f"{word} {freq}\n")
    
    print(f"\n词频列表已保存到: {freq_file}")
    return word_freq


def load_word_freq_from_file(freq_file):
    """
    从文件加载词频列表
    
    Args:
        freq_file: 词频文件路径
    
    Returns:
        词频统计字典
    """
    word_freq = {}
    try:
        with open(freq_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    word = ' '.join(parts[:-1])  # 词语可能包含空格
                    try:
                        freq = int(parts[-1])
                        if freq > 0:  # 只保留频率大于0的词
                            word_freq[word] = freq
                    except ValueError:
                        print(f"警告: 跳过无效行: {line}")
        print(f"\n从文件加载了 {len(word_freq)} 个词语")
    except Exception as e:
        print(f"错误: 读取词频文件失败: {e}")
    
    return word_freq


def generate_wordcloud(word_freq, output_path):
    """
    生成词云图片
    
    Args:
        word_freq: 词频统计字典
        output_path: 输出图片路径
    """
    if not word_freq:
        print("错误: 词频字典为空，无法生成词云")
        return
    
    # 创建词云对象
    # 使用系统中文字体
    wordcloud = WordCloud(
        width=1920,
        height=1080,
        background_color='white',
        font_path='/System/Library/Fonts/Hiragino Sans GB.ttc',  # macOS 中文字体
        max_words=200,
        relative_scaling=0.5,
        min_font_size=10,
        colormap='viridis',
        prefer_horizontal=1.0  # 所有词语横向排列
    ).generate_from_frequencies(word_freq)
    
    # 保存图片
    plt.figure(figsize=(16, 9), dpi=150)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n词云图片已保存到: {output_path}")
    
    # 如果在交互环境中，可以显示图片
    # plt.show()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='日记词云生成器')
    parser.add_argument('--noun', action='store_true', 
                        help='只提取名词生成词云')
    parser.add_argument('--interactive', action='store_true',
                        help='交互模式：生成词频列表文件供用户编辑后再生成词云')
    args = parser.parse_args()
    
    # 获取脚本所在目录的父目录（项目根目录）
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 日记目录、停用词文件和输出路径
    diaries_dir = project_root / 'diaries'
    stopwords_file = script_dir / 'stopwords.txt'
    output_path = project_root / 'wordcloud.png'
    freq_file = project_root / 'word_freq.txt'
    
    print("=" * 60)
    print("日记词云生成器")
    if args.noun:
        print("模式: 仅名词")
    else:
        print("模式: 全部词性")
    if args.interactive:
        print("模式: 交互式")
    print("=" * 60)
    
    # 检查目录是否存在
    if not diaries_dir.exists():
        print(f"错误: 日记目录不存在: {diaries_dir}")
        return
    
    # 加载停用词
    print(f"\n正在加载停用词文件: {stopwords_file}")
    stopwords = load_stopwords(stopwords_file)
    
    # 读取所有日记文件
    print(f"\n正在读取日记文件: {diaries_dir}")
    all_text = read_diary_files(diaries_dir)
    
    if not all_text:
        print("错误: 没有读取到任何内容")
        return
    
    print(f"总共读取了 {len(all_text)} 个字符")
    
    # 分词和过滤
    print("\n正在进行中文分词和停用词过滤...")
    words = segment_text(all_text, stopwords, noun_only=args.noun)
    
    if not words:
        print("错误: 分词后没有有效词语")
        return
    
    # 处理交互模式
    if args.interactive:
        # 保存词频列表到文件
        word_freq = save_word_freq_to_file(words, freq_file)
        
        print("\n" + "=" * 60)
        print("请编辑词频文件，然后回到控制台")
        print(f"词频文件路径: {freq_file}")
        print("=" * 60)
        print("\n您可以:")
        print("  - 删除不想要的词语（删除整行）")
        print("  - 修改词语的频率（修改数字）")
        print("  - 添加新词语（格式: 词语 频率）")
        print("\n编辑完成后，输入 'y' 继续生成词云，输入其他任意键取消: ", end='')
        
        user_input = input().strip().lower()
        
        if user_input != 'y':
            print("\n已取消生成词云")
            return
        
        # 从文件重新加载词频
        print("\n正在从编辑后的文件加载词频...")
        word_freq = load_word_freq_from_file(freq_file)
        
        if not word_freq:
            print("错误: 词频列表为空，无法生成词云")
            return
        
        # 显示编辑后的 Top 20
        print("\n编辑后词频 Top 20:")
        sorted_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        for word, freq in sorted_freq[:20]:
            print(f"  {word}: {freq}")
        
        # 生成词云
        print("\n正在生成词云图片...")
        generate_wordcloud(word_freq, output_path)
    else:
        # 非交互模式，直接生成词云
        print("\n正在生成词云图片...")
        from collections import Counter
        word_freq = Counter(words)
        
        print(f"\n总共提取了 {len(words)} 个有效词语")
        print(f"去重后有 {len(word_freq)} 个不同的词语")
        print("\n词频 Top 20:")
        for word, freq in word_freq.most_common(20):
            print(f"  {word}: {freq}")
        
        generate_wordcloud(word_freq, output_path)
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()

