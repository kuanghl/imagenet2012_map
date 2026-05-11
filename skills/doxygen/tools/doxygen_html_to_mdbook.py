#!/usr/bin/env python3
"""
将 Doxygen 生成的 HTML 文档转换为 mdBook 格式（快速修复版）
特点：
  - 按目录/类别自动分组生成 SUMMARY.md
  - 过滤 Doxygen 自动生成的噪声页面
  - 保持原有目录结构，链接自动修复
依赖: pip install markdownify beautifulsoup4
"""
import os
import re
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
from markdownify import markdownify as md

# 尝试导入 BeautifulSoup，若未安装则降级使用正则
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("⚠️  未安装 beautifulsoup4，将使用正则解析（效果可能略差）")
    print("   建议安装: pip install beautifulsoup4")

# ============ 配置区域 ============
# 需要跳过的噪声页面模式（正则匹配文件名）
SKIP_PATTERNS = [
    r'^dir_[a-f0-9]+\.html$',           # 目录哈希页
    r'^globals_[a-z]+\.html$',          # 全局符号索引页
    r'^inherits\.html$',                # 继承图
    r'^graph_legend\.html$',            # 图例说明
    r'^deprecated\.html$',              # 废弃列表（可选保留）
    r'^todo\.html$',                    # TODO 列表（可选保留）
    r'^test\.html$',                    # 测试列表（可选保留）
    r'^pages\.html$',                   # 相关页面索引
    r'^examples\.html$',                # 示例索引（如有单独示例页可保留）
    r'^annotated\.html$',               # 类列表（如已有分类可跳过）
    r'^hierarchy\.html$',               # 类层次图
    r'^functions.*\.html$',             # 函数索引
    r'^variables.*\.html$',             # 变量索引
    r'^defines.*\.html$',               # 宏定义索引
    r'^typedefs.*\.html$',              # 类型定义索引
    r'^enums.*\.html$',                 # 枚举索引
    r'^eval.*\.html$',                  # 枚举值索引
    r'^files\.html$',                   # 文件列表（如按目录分组可跳过）
    r'^modules\.html$',                 # 模块列表（如按目录分组可跳过）
]

# 顶级分类映射（按 Doxygen 默认目录名 → 显示名称）
CATEGORY_NAMES = {
    "html": "首页",
    "search": "",  # 跳过搜索目录
    "menudata": "",
    "navtree": "",
    # 常见自定义目录
    "modules": "📦 模块",
    "classes": "🧱 类参考",
    "structs": "🧱 结构体",
    "files": "📄 文件",
    "namespaces": "🌐 命名空间",
    "examples": "💡 示例",
    "pages": "📚 附加页",
}

# 分类显示顺序（未列出的按字母排序放最后）
CATEGORY_ORDER = [
    "index", "main", "home",  # 首页相关
    "modules", "groups",      # 模块
    "classes", "structs", "interfaces", "annotated",  # 类
    "namespaces",             # 命名空间
    "files", "dirs",          # 文件
    "examples", "demos",      # 示例
    "pages", "additional",    # 附加页
]
# ==================================


def extract_main_content(html_str: str) -> str:
    """提取 Doxygen HTML 正文，去除导航、页眉、搜索框等噪声"""
    if HAS_BS4:
        soup = BeautifulSoup(html_str, 'html.parser')
        # 移除噪声元素
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()
        # 移除 Doxygen 特有噪声块
        for cls in ['header', 'navpath', 'tabs', 'summary', 'memitem']:
            for tag in soup.find_all(class_=cls):
                # 只移除明显的导航/搜索块，保留内容区的 .summary
                if tag.get('id') in ['MSearchBox', 'nav-tree'] or \
                   'nav' in cls or 'header' in cls:
                    tag.decompose()
        
        # 提取主内容区域（优先级：main > contents > doc-content > body）
        content = (soup.find('main') or 
                   soup.find('div', class_='contents') or 
                   soup.find('div', id='doc-content') or
                   soup.find('body'))
        return str(content) if content else str(soup)
    else:
        # 无 BS4 时的正则降级方案
        body = re.search(r'<body[^>]*>(.*?)</body>', html_str, re.DOTALL | re.IGNORECASE)
        if not body: 
            return html_str
        content = body.group(1)
        # 移除常见噪声块
        noise_patterns = [
            r'<div[^>]*class="[^"]*header[^"]*"[^>]*>.*?</div>',
            r'<div[^>]*class="[^"]*navpath[^"]*"[^>]*>.*?</div>',
            r'<div[^>]*id="MSearchBox"[^>]*>.*?</div>',
            r'<div[^>]*class="[^"]*tabs[^"]*"[^>]*>.*?</div>',
            r'<script[^>]*>.*?</script>',
            r'<style[^>]*>.*?</style>',
        ]
        for p in noise_patterns:
            content = re.sub(p, '', content, flags=re.DOTALL | re.IGNORECASE)
        return content


def fix_markdown_links(md_content: str, base_path: Path = None) -> str:
    """修复 Markdown 链接：.html -> .md，处理相对路径与锚点"""
    def replace_link(match):
        full_match = match.group(0)
        url = match.group(1)
        
        # 忽略外部链接、邮件、纯锚点、JavaScript
        if url.startswith(("http://", "https://", "mailto:", "#", "javascript:")):
            return full_match
        
        # 分离锚点
        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor
        
        # 替换后缀
        if url.endswith(".html"):
            new_url = url[:-5] + ".md"
        elif url.endswith(".htm"):
            new_url = url[:-4] + ".md"
        else:
            new_url = url  # 可能是目录或其他
        
        # 处理根路径
        if new_url.startswith("/"):
            new_url = "." + new_url
        
        return f']({new_url}{anchor})'

    # 匹配 [text](url) 格式，支持含空格的 URL（Doxygen 可能生成）
    return re.sub(r'\]\(([^)\s]+(?:\s+[^)\s]+)*)\)', replace_link, md_content)


def extract_title(md_content: str, fallback_name: str) -> str:
    """从 Markdown 提取第一个有效标题，否则使用文件名美化"""
    # 跳过元数据块（如 --- title: xxx ---）
    content = re.sub(r'^---\n.*?\n---\n', '', md_content, flags=re.DOTALL)
    
    # 匹配 # 标题（排除 ##+ 子标题）
    m = re.search(r'^#\s+([^\n#]+?)(?:\n|$)', content, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        # 清理常见 Doxygen 标题后缀
        title = re.sub(r'\s*[-–—]\s*Reference$', '', title)
        title = re.sub(r'\s+Module$', '', title)
        return title
    
    # 备用：从 <h1> 提取（如果 markdownify 保留了 HTML）
    m = re.search(r'<h1[^>]*>(.*?)</h1>', md_content, re.IGNORECASE)
    if m:
        from html import unescape
        return unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    
    # 最终回退：美化文件名
    name = fallback_name.replace('_', ' ').replace('-', ' ').strip()
    return name.title() if name else "Untitled"


def should_skip_file(filename: str) -> bool:
    """判断是否跳过该文件（噪声页面）"""
    return any(re.match(pattern, filename, re.IGNORECASE) for pattern in SKIP_PATTERNS)


def get_category(filepath: Path, base_path: Path) -> str:
    """根据文件路径确定所属分类（用于 SUMMARY 分组）"""
    try:
        rel = filepath.relative_to(base_path)
    except ValueError:
        return "其他"
    
    parts = rel.parts
    if len(parts) <= 1:
        return "首页"
    
    # 取第一级目录作为分类
    category_key = parts[0].lower().rstrip('/')
    
    # 映射到友好名称
    for key, name in CATEGORY_NAMES.items():
        if category_key == key:
            return name if name else None  # None 表示跳过该分类
    
    # 未匹配则返回首字母大写
    return category_key.capitalize()


def convert_doxygen_to_mdbook(input_html: str, output_dir: str):
    in_path = Path(input_html).resolve()
    out_path = Path(output_dir).resolve()
    src_path = out_path / "src"

    if not in_path.is_dir():
        raise FileNotFoundError(f"❌ 输入目录不存在: {input_html}")

    # 清理输出目录
    if out_path.exists():
        shutil.rmtree(out_path)
    src_path.mkdir(parents=True, exist_ok=True)

    # 收集并过滤 HTML 文件
    all_html = sorted(in_path.rglob("*.html"))
    html_files = [f for f in all_html if not should_skip_file(f.name)]
    
    print(f"🔍 找到 {len(all_html)} 个 HTML 文件，过滤后处理 {len(html_files)} 个...")
    
    # 存储转换结果：{相对路径: (md 内容, 标题)}
    converted = {}
    
    for html_file in html_files:
        rel = html_file.relative_to(in_path)
        md_rel = rel.with_suffix(".md")
        md_full = src_path / md_rel

        try:
            html_text = html_file.read_text(encoding="utf-8", errors="ignore")
            clean_html = extract_main_content(html_text)
            
            # 转换为 Markdown
            md_text = md(clean_html, strip=["script", "style"], heading_style="ATX")
            
            # 修复链接（传入基路径用于相对路径计算）
            md_text = fix_markdown_links(md_text, base_path=rel.parent)
            
            # 确保以标题开头
            if not md_text.strip().startswith("#"):
                fallback = md_full.stem.replace('_', ' ').replace('-', ' ')
                md_text = f"# {fallback.title()}\n\n" + md_text
            
            # 提取标题用于 SUMMARY
            title = extract_title(md_text, md_full.stem)
            
            # 写入文件
            md_full.parent.mkdir(parents=True, exist_ok=True)
            md_full.write_text(md_text, encoding="utf-8")
            converted[str(md_rel)] = (md_full, title)
            print(f"  ✅ {rel} -> {md_rel}")

        except Exception as e:
            print(f"  ⚠️ 跳过 {rel} | 错误: {type(e).__name__}: {e}")
            continue

    # 📦 复制静态资源（图片、CSS 等）
    print("\n📦 复制静态资源...")
    asset_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".css"}
    copied = 0
    for f in in_path.rglob("*"):
        if f.is_file() and f.suffix.lower() in asset_exts:
            # 跳过 Doxygen 生成的动态资源（可选）
            if "search" in f.parts or "menudata" in f.name:
                continue
            dest = src_path / f.relative_to(in_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                shutil.copy2(f, dest)
                copied += 1
    print(f"   已复制 {copied} 个资源文件")

    # 📖 生成结构化 SUMMARY.md
    print("\n📖 生成 src/SUMMARY.md ...")
    
    # 按分类分组
    groups = defaultdict(list)
    for md_rel, (md_full, title) in converted.items():
        category = get_category(md_full, src_path)
        if category:  # None 表示跳过
            groups[category].append((md_rel, title))
    
    # 生成 SUMMARY 内容
    lines = ["# Summary\n", "\n"]
    
    # 1. 首页置顶
    if "index.md" in converted:
        lines.append("- [🏠 首页](index.md)\n")
        if "main.md" in converted and "main.md" != "index.md":
            lines.append("- [📋 概览](main.md)\n")
        lines.append("\n")
    
    # 2. 按预定义顺序输出分类
    processed_cats = set()
    for cat_key in CATEGORY_ORDER:
        # 查找匹配的分类名称
        cat_name = None
        for name in groups.keys():
            if cat_key.lower() in name.lower() or name.lower() in cat_key.lower():
                cat_name = name
                break
        if not cat_name or cat_name in processed_cats:
            continue
        
        items = groups[cat_name]
        if not items:
            continue
            
        lines.append(f"\n# {cat_name}\n\n")
        for md_rel, title in sorted(items, key=lambda x: x[0]):
            # 计算缩进（根据路径深度）
            depth = Path(md_rel).parent.as_posix().count('/')
            indent = "  " * min(depth, 2)  # 最多两级缩进
            lines.append(f"{indent}- [{title}]({md_rel})\n")
        processed_cats.add(cat_name)
    
    # 3. 其他未分类文件
    remaining = {k: v for k, v in groups.items() if k not in processed_cats}
    if remaining:
        lines.append("\n# 其他\n\n")
        for cat_name in sorted(remaining.keys()):
            if len(remaining) > 1:  # 多个剩余分类时显示子标题
                lines.append(f"## {cat_name}\n")
            for md_rel, title in sorted(remaining[cat_name], key=lambda x: x[0]):
                lines.append(f"- [{title}]({md_rel})\n")
    
    (src_path / "SUMMARY.md").write_text("".join(lines), encoding="utf-8")
    print(f"   ✅ 生成 {len(lines)} 行 SUMMARY.md")

    # ⚙️ 生成 book.toml
    book_toml = f"""[book]
title = "Doxygen 技术文档"
authors = ["Your Name"]
description = "由 Doxygen HTML 自动转换生成"
language = "zh"
src = "src"

[output.html]
git-repository-url = ""
git-repository-icon = "fa-github"
mathjax-support = true
curly-quotes = true

[output.html.search]
enable = true
limit-results = 20
"""
    (out_path / "book.toml").write_text(book_toml, encoding="utf-8")

    # 🎉 完成
    print(f"\n🎉 转换完成！")
    print(f"📁 输出目录: {out_path}")
    print(f"📊 转换统计: {len(converted)} 个页面, {len(groups)} 个分类")
    print(f"\n🚀 启动预览:")
    print(f"   cd {out_path} && mdbook serve")
    print(f"\n🔧 自定义建议:")
    print(f"   - 编辑 book.toml 修改标题/作者")
    print(f"   - 调整 CATEGORY_NAMES/CATEGORY_ORDER 定制分类")
    print(f"   - 修改 SKIP_PATTERNS 控制页面过滤")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="将 Doxygen HTML 转换为 mdBook 格式（结构优化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s doxygen_html/                    # 输出到 mdbook_output/
  %(prog)s doxygen_html/ -o my_docs/        # 自定义输出目录
  %(prog)s doxygen_html/ --help             # 查看帮助

提示:
  - 确保已安装依赖: pip install markdownify beautifulsoup4
  - 转换后可用 mdbook serve 预览，mdbook build 构建静态站
        """)
    parser.add_argument("input_html", help="Doxygen 生成的 HTML 目录路径")
    parser.add_argument("-o", "--output", default="mdbook_output", 
                        help="mdBook 输出目录 (默认: mdbook_output)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="显示详细转换日志")
    args = parser.parse_args()
    
    try:
        convert_doxygen_to_mdbook(args.input_html, args.output)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断，已清理临时文件")
    except Exception as e:
        print(f"\n❌ 转换失败: {type(e).__name__}: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        exit(1)