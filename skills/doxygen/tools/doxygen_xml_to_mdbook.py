#!/usr/bin/env python3
"""
Doxygen XML → mdBook 转换器（修复版）
修复: FutureWarning + KeyError: '@' + 全部跳过问题
"""

import os, re, shutil, argparse, traceback
from pathlib import Path
from collections import defaultdict
from lxml import etree
from markdownify import markdownify as md

# ============ 配置 ============
SKIP_COMPOUND_TYPES = set()  # 不再跳过任何类型，保留所有文档
CATEGORY_MAP = {
    'class': {'name': '🧱 类参考', 'order': 20, 'prefix': ''},
    'struct': {'name': '🧱 结构体', 'order': 21, 'prefix': ''},
    'union': {'name': '🔗 联合体', 'order': 22, 'prefix': ''},
    'file': {'name': '📄 文件', 'order': 40, 'prefix': ''},
    'namespace': {'name': '🌐 命名空间', 'order': 30, 'prefix': ''},
    'dir': {'name': '📁 目录', 'order': 50, 'prefix': ''},
    'group': {'name': '📦 分组', 'order': 60, 'prefix': ''},
    'page': {'name': '📃 页面', 'order': 70, 'prefix': ''},
}
CODE_LANG_MAP = {'cpp': 'cpp', 'c': 'c', 'py': 'python', 'python': 'python'}

# Mermaid 配置文件默认路径（可通过 --assets-dir 参数覆盖）
DEFAULT_ASSETS_DIR = Path(__file__).parent.parent.parent.parent / 'docs'
MERMAID_FILES_TEMPLATE = {
    'mermaid.min.js': 'mermaid.min.js',
    'mermaid-init.js': 'mermaid-init.js',
    'book.toml.template': 'book.toml',
}

# ============ 工具函数 ============
def safe_get(element, attr, default=None):
    """安全获取属性，避免 KeyError"""
    if element is None:
        return default
    try:
        return element.get(attr, default)
    except (KeyError, AttributeError):
        return default

def safe_bool(element):
    """lxml 元素安全布尔检查（兼容新版）"""
    return element is not None and len(element) > 0

def refid_to_markdown_link(refid, text=None, parser=None):
    """
    将 Doxygen refid 转换为正确的 Markdown 链接
    
    Args:
        refid: Doxygen 的 refid (如 'debug_8c_1a3fda2c744132d907c936b9edbdd67932')
        text: 链接显示文本
        parser: DoxygenXMLParser 实例，用于查找文件路径
    
    Returns:
        Markdown 链接字符串
    """
    if not refid or refid.startswith('@'):
        return text or refid
    
    # 如果提供了 parser，尝试查找目标文件
    if parser and hasattr(parser, 'refid_to_file'):
        # 直接查找
        target_file = parser.refid_to_file.get(refid)
        
        # 如果是成员级别的 refid（包含下划线和哈希），尝试提取文件部分
        if not target_file and '_' in refid:
            # 尝试提取文件部分的 refid (如 debug_8c_1a3fda... -> debug_8c)
            parts = refid.split('_')
            if len(parts) >= 2:
                # 找到最后一个纯字母数字的部分作为文件名
                for i in range(len(parts)-1, 0, -1):
                    file_refid = '_'.join(parts[:i])
                    if file_refid in parser.refid_to_file:
                        target_file = parser.refid_to_file[file_refid]
                        break
        
        if target_file:
            # 跨文件链接，添加锚点指向具体成员
            display_text = text or refid
            return f'[{display_text}]({target_file}#{refid})'
    
    # 降级：使用页面内锚点
    display_text = text or refid
    return f'[{display_text}](#{refid})'

# ============ 解析器 ============
class DoxygenXMLParser:
    def __init__(self, xml_dir: Path):
        self.xml_dir = xml_dir.resolve()
        self.compounds = {}
        self.refid_to_file = {}  # refid -> 生成的 Markdown 文件路径
        self.verbose = False
        
    def load_index(self):
        index_path = self.xml_dir / 'index.xml'
        if not index_path.exists():
            raise FileNotFoundError(f"未找到: {index_path}")
        
        # 使用 recover 模式处理可能的编码问题
        parser = etree.XMLParser(recover=True, encoding='UTF-8')
        tree = etree.parse(str(index_path), parser)
        for compound in tree.xpath('//compound'):
            refid = compound.get('refid')
            kind = compound.get('kind')
            if kind in SKIP_COMPOUND_TYPES:
                continue
            self.compounds[refid] = {
                'kind': kind,
                'name': compound.findtext('name', default='Unknown'),
            }
        print(f"📚 加载 {len(self.compounds)} 个条目")
        
    def parse_compound(self, refid: str):
        """解析单个 compound（增强容错）"""
        try:
            compound_file = self.xml_dir / f"{refid}.xml"
            if not compound_file.exists():
                return None
                
            # 使用 encoding 参数处理编码问题
            parser = etree.XMLParser(recover=True, encoding='UTF-8')
            tree = etree.parse(str(compound_file), parser)
            root = tree.getroot()
            compound_def = root.find('compounddef')
            if compound_def is None:
                return None
                
            info = self.compounds.get(refid, {}).copy()
            info.update({
                'title': self._get_text(compound_def, 'compoundname') or info.get('name', 'Untitled'),
                'brief': self._para_to_md(compound_def.find('briefdescription')),
                'details': self._para_to_md(compound_def.find('detaileddescription')),
                'members': self._extract_members(compound_def),
                'graphs': self._extract_graphs(compound_def),
            })
            return info
        except KeyError as e:
            if self.verbose:
                print(f"  🔍 KeyError in {refid}: {e}")
                traceback.print_exc()
            return None  # 返回 None 让调用方决定是否降级处理
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️ 解析 {refid} 失败: {e}")
            return None
    
    def _get_text(self, parent, tag_name):
        """安全提取文本内容（递归获取所有文本）"""
        if parent is None:
            return None
        elem = parent.find(tag_name)
        if elem is None:
            return None
        # 递归获取元素内所有文本（包括子元素）
        texts = []
        if elem.text:
            texts.append(elem.text.strip())
        for child in elem:
            if child.text:
                texts.append(child.text.strip())
            if child.tail:
                texts.append(child.tail.strip())
        result = ' '.join(texts).strip()
        return result if result else None
    
    def _para_to_md(self, element):
        """XML para → Markdown（安全版）"""
        if not safe_bool(element):
            # 处理空元素或仅有文本的情况
            if element is not None:
                # 递归获取所有文本内容
                texts = []
                if element.text:
                    texts.append(element.text.strip())
                for child in element:
                    if child.text:
                        texts.append(child.text.strip())
                    if child.tail:
                        texts.append(child.tail.strip())
                return ' '.join(texts).strip()
            return ''
        
        try:
            # 克隆避免修改原树
            elem = etree.fromstring(etree.tostring(element, encoding='unicode', method='xml'))
            self._convert_tags(elem)
            html = etree.tostring(elem, encoding='unicode', method='html')
            # 清理 para 标签
            html = re.sub(r'</?para[^>]*>', '', html)
            return md(html, strip=['script', 'style'], heading_style='ATX').strip()
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️ Markdown 转换失败: {e}")
            # 降级：返回纯文本
            texts = []
            if element.text:
                texts.append(element.text.strip())
            for child in element:
                if child.text:
                    texts.append(child.text.strip())
                if child.tail:
                    texts.append(child.tail.strip())
            return ' '.join(texts).strip()
    
    def _convert_tags(self, elem):
        """转换 Doxygen 标签（安全属性访问）"""
        # 格式标签
        for tag, repl in [('c', 'code'), ('em', 'em'), ('b', 'strong')]:
            for child in elem.findall(f'.//{tag}'):
                parent = child.getparent()
                if parent is not None:
                    new = etree.Element(repl)
                    new.text, new.tail = child.text, child.tail
                    # 安全复制属性
                    for k, v in child.attrib.items():
                        if not k.startswith('{'):
                            new.set(k, v)
                    parent.replace(child, new)
        
        # 代码块
        for code in elem.xpath('.//programlisting'):
            lang = safe_get(code, 'language', '') or safe_get(code, 'lang', '')
            lang = CODE_LANG_MAP.get(lang.lower().strip(), 'text')
            pre = etree.Element('pre')
            code_el = etree.SubElement(pre, 'code', {'class': f'language-{lang}'})
            # 正确提取代码文本
            code_text = []
            if code.text:
                code_text.append(code.text)
            for child in code:
                if child.text:
                    code_text.append(child.text)
                if child.tail:
                    code_text.append(child.tail)
            code_el.text = ''.join(code_text)
            parent = code.getparent()
            if parent is not None:
                parent.replace(code, pre)
        
        # 链接
        for ref in elem.xpath('.//ref'):
            refid = safe_get(ref, 'refid', '')
            if refid and not refid.startswith('@'):
                parent = ref.getparent()
                if parent is not None:
                    # 使用正确的链接格式
                    link_text = ref.text or refid
                    link = refid_to_markdown_link(refid, link_text, self)
                    # 将链接转换为纯文本（因为 markdownify 会处理）
                    ref.text = link
                    # 移除子元素
                    for child in list(ref):
                        ref.remove(child)
        
        # 递归
        for child in list(elem):
            self._convert_tags(child)
    
    def _extract_members(self, compound_def):
        """提取成员（增强版，正确处理成员信息）"""
        members = []
        for section in compound_def.xpath('.//sectiondef'):
            section_header = self._get_text(section, 'header') or safe_get(section, 'kind', 'Members').title()
            items = []
            for member in section.xpath('./memberdef'):
                try:
                    kind = safe_get(member, 'kind', 'unknown')
                    if safe_get(member, 'prot', 'public') != 'public':
                        continue
                    
                    # 正确提取成员名称
                    name_elem = member.find('name')
                    name = 'unknown'
                    if name_elem is not None and name_elem.text:
                        name = name_elem.text.strip()
                    
                    # 正确提取类型信息
                    type_elem = member.find('type')
                    type_text = self._extract_type(type_elem)
                    
                    item = {
                        'kind': kind,
                        'name': name,
                        'type': type_text,
                        'brief': self._para_to_md(member.find('briefdescription')),
                        'details': self._para_to_md(member.find('detaileddescription')),
                        'referenced_by': self._extract_referenced_by(member),
                        'graphs': self._extract_member_graphs(member),  # 新增：提取成员的图表
                    }
                    if kind == 'function':
                        item['args'] = self._get_text(member, 'argsstring') or ''
                    items.append(item)
                except Exception as e:
                    if self.verbose:
                        print(f"    ⚠️ 成员解析失败: {e}")
                    continue  # 单个成员失败不影响其他
            if items:
                members.append({'section': section_header, 'items': items})
        return members
    
    def _extract_type(self, type_elem):
        """提取类型信息（处理 ref 链接和文本）"""
        if not safe_bool(type_elem):
            return type_elem.text.strip() if type_elem is not None and type_elem.text else ''
        
        parts = []
        # 处理混合内容：文本 + ref 元素
        if type_elem.text:
            parts.append(type_elem.text.strip())
        
        for child in type_elem:
            if child.tag == 'ref':
                # 处理引用链接
                refid = safe_get(child, 'refid', '')
                link_text = child.text.strip() if child.text else refid
                if refid and not refid.startswith('@'):
                    parts.append(f'[{link_text}](#{refid})')
                else:
                    parts.append(link_text)
            elif child.text:
                parts.append(child.text.strip())
            if child.tail:
                parts.append(child.tail.strip())
        
        return ' '.join(parts).strip()
    
    def _extract_referenced_by(self, member):
        """提取 referencedby 信息（被哪些函数/变量引用）"""
        refs = []
        for refby in member.findall('.//referencedby'):
            ref_id = safe_get(refby, 'refid', '')
            ref_text = refby.text.strip() if refby.text else ''
            
            # 跳过内部引用（@开头）
            if ref_id and not ref_id.startswith('@'):
                # 使用正确的链接格式
                link = refid_to_markdown_link(ref_id, ref_text, self)
                refs.append(link)
        
        return refs
    
    def _extract_graphs(self, compound_def):
        """提取图表信息（collaborationgraph, inheritancegraph, callgraph等）并转换为 mermaid"""
        graphs = []
        
        # 处理 collaborationgraph
        collab_graph = compound_def.find('collaborationgraph')
        if collab_graph is not None:
            mermaid_code = self._convert_graphviz_to_mermaid(collab_graph, 'Collaboration Diagram', 'classDiagram')
            if mermaid_code:
                graphs.append(('Collaboration Diagram', mermaid_code))
        
        # 处理 inheritancegraph
        inherit_graph = compound_def.find('inheritancegraph')
        if inherit_graph is not None:
            mermaid_code = self._convert_graphviz_to_mermaid(inherit_graph, 'Inheritance Diagram', 'classDiagram')
            if mermaid_code:
                graphs.append(('Inheritance Diagram', mermaid_code))
        
        return graphs
    
    def _extract_member_graphs(self, member):
        """提取成员的图表（callergraph, callgraph）"""
        graphs = []
        
        # 处理 callergraph (被调用图)
        caller_graph = member.find('callergraph')
        if caller_graph is not None:
            mermaid_code = self._convert_call_graph_to_mermaid(caller_graph, 'Caller Graph')
            if mermaid_code:
                graphs.append(('Caller Graph', mermaid_code))
        
        # 处理 callgraph (调用图)
        call_graph = member.find('callgraph')
        if call_graph is not None:
            mermaid_code = self._convert_call_graph_to_mermaid(call_graph, 'Call Graph')
            if mermaid_code:
                graphs.append(('Call Graph', mermaid_code))
        
        return graphs
    
    def _convert_graphviz_to_mermaid(self, graph_elem, title, diagram_type='classDiagram'):
        """将 Doxygen 的 graphviz 格式转换为 mermaid 图表
        
        Args:
            graph_elem: XML 元素
            title: 图表标题
            diagram_type: 'classDiagram' 或 'flowchart'
        """
        try:
            nodes = graph_elem.xpath('.//node')
            
            if not nodes:
                return None
            
            lines = [f'```mermaid', f'{diagram_type}']
            
            # 收集所有节点
            node_map = {}
            for node in nodes:
                node_id = node.get('id', '')
                label_elem = node.find('label')
                label = label_elem.text.strip() if label_elem is not None and label_elem.text else f'Node_{node_id}'
                
                # 清理标签（移除空格和特殊字符）
                clean_label = re.sub(r'\s+', '_', label)
                node_map[node_id] = clean_label
                
                if diagram_type == 'classDiagram':
                    # 添加类定义
                    lines.append(f'    class {clean_label}')
                elif diagram_type == 'flowchart':
                    # 添加流程图节点
                    lines.append(f'    {clean_label}["{label}"]')
            
            # 收集所有边（关系）- Doxygen 使用 childnode 而不是 edge
            for node in nodes:
                node_id = node.get('id', '')
                from_class = node_map.get(node_id, '')
                
                # 查找 childnode 元素（表示从这个节点出发的关系）
                for childnode in node.xpath('.//childnode'):
                    to_node_id = childnode.get('refid', '')
                    relation_type = childnode.get('relation', '').lower()
                    
                    if to_node_id in node_map:
                        to_class = node_map[to_node_id]
                        
                        if diagram_type == 'classDiagram':
                            # 确定关系类型
                            if 'usage' in relation_type:
                                relation = '--*>'  # 组合/聚合
                            elif 'inheritance' in relation_type:
                                relation = '<|--'  # 继承
                            else:
                                relation = '-->'  # 默认关联
                            
                            # 获取 edgelabel（字段名）
                            edgelabels = childnode.xpath('.//edgelabel')
                            if edgelabels:
                                # 只显示前3个标签，避免太长
                                labels = [label.text.strip() for label in edgelabels[:3] if label.text]
                                if labels:
                                    label_str = ', '.join(labels)
                                    if len(edgelabels) > 3:
                                        label_str += ', ...'
                                    lines.append(f'    {from_class} {relation} {to_class} : {label_str}')
                                else:
                                    lines.append(f'    {from_class} {relation} {to_class}')
                            else:
                                lines.append(f'    {from_class} {relation} {to_class}')
                        elif diagram_type == 'flowchart':
                            # 流程图箭头
                            lines.append(f'    {from_class} --> {to_class}')
            
            lines.append('```')
            return '\n'.join(lines)
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️ 图表转换失败: {e}")
                import traceback
                traceback.print_exc()
            return None
    
    def _convert_call_graph_to_mermaid(self, graph_elem, title):
        """将 caller/callee graph 转换为 mermaid flowchart
        
        Args:
            graph_elem: XML 元素 (callergraph 或 callgraph)
            title: 图表标题
        
        Returns:
            Mermaid flowchart 代码字符串
        """
        try:
            nodes = graph_elem.xpath('.//node')
            
            if not nodes:
                return None
            
            lines = [f'```mermaid', f'flowchart TD']
            
            # 收集所有节点
            node_map = {}
            for node in nodes:
                node_id = node.get('id', '')
                label_elem = node.find('label')
                label = label_elem.text.strip() if label_elem is not None and label_elem.text else f'Node_{node_id}'
                
                # 清理标签（用于节点 ID）
                clean_label = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                # 确保以字母开头
                if clean_label and not clean_label[0].isalpha():
                    clean_label = 'N_' + clean_label
                node_map[node_id] = clean_label
                
                # 添加流程图节点
                lines.append(f'    {clean_label}["{label}"]')
            
            # 收集所有边
            for node in nodes:
                node_id = node.get('id', '')
                from_node = node_map.get(node_id, '')
                
                # 查找 edge 元素
                for edge in node.xpath('.//edge'):
                    # 获取目标节点
                    target_nodes = edge.xpath('.//targetnode')
                    if target_nodes:
                        target_node = target_nodes[0]
                        to_node_id = target_node.get('refid', '')
                        
                        if to_node_id in node_map:
                            to_node = node_map[to_node_id]
                            lines.append(f'    {from_node} --> {to_node}')
            
            lines.append('```')
            return '\n'.join(lines)
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️ 调用图转换失败: {e}")
                import traceback
                traceback.print_exc()
            return None


# ============ 生成器 ============
class MarkdownGenerator:
    def __init__(self, src_path: Path, parser=None):
        self.src_path = src_path
        self.parser = parser  # 保存 parser 引用用于链接解析
        self.pages = []
        
    def generate_page(self, refid: str, info: dict):
        kind = info.get('kind', 'unknown')
        cat = CATEGORY_MAP.get(kind, {})
        
        # 直接使用 refid 作为文件名，不再添加额外前缀
        filename = f"{refid}.md"
        
        # 简单目录分类
        if kind in ('class', 'struct', 'union'):
            rel_path = Path('classes') / filename
        elif kind == 'file':
            rel_path = Path('files') / filename
        elif kind == 'namespace':
            rel_path = Path('namespaces') / filename
        elif kind == 'dir':
            rel_path = Path('directories') / filename
        elif kind == 'group':
            rel_path = Path('groups') / filename
        elif kind == 'page':
            # page 类型直接放在根目录或 pages 子目录
            rel_path = Path('pages') / filename
        else:
            rel_path = Path(filename)
        
        full_path = self.src_path / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 构建内容
        lines = [f"# {info.get('title', 'Untitled')}\n\n"]
        if info.get('brief'):
            lines.append(f"{info['brief']}\n\n")
        if info.get('details'):
            lines.append(f"## 详细描述\n\n{info['details']}\n\n")
        
        # 添加图表（mermaid格式）
        for graph_title, graph_code in info.get('graphs', []):
            lines.append(f"## {graph_title}\n\n")
            lines.append(f"{graph_code}\n\n")
        
        # 成员
        for section in info.get('members', []):
            lines.append(f"## {section['section']}\n\n")
            for item in section['items']:
                # 构建完整的函数/变量签名
                sig_parts = []
                if item.get('type'):
                    sig_parts.append(item['type'])
                sig_parts.append(item['name'])
                if item.get('args'):
                    sig_parts.append(item['args'])
                sig = ' '.join(sig_parts)
                lines.append(f"### `{sig}`\n\n")
                
                # 添加简要描述
                if item.get('brief'):
                    lines.append(f"{item['brief']}\n\n")
                
                # 添加详细描述
                if item.get('details'):
                    lines.append(f"{item['details']}\n\n")
                
                # 添加被引用信息
                if item.get('referenced_by'):
                    refs_str = ', '.join(item['referenced_by'])
                    lines.append(f"**被引用**: {refs_str}\n\n")
                
                # 添加成员的图表（caller/callee graph）
                for graph_title, graph_code in item.get('graphs', []):
                    lines.append(f"#### {graph_title}\n\n")
                    lines.append(f"{graph_code}\n\n")
        
        full_path.write_text('\n'.join(lines), encoding='utf-8')
        
        # 记录 refid 到文件路径的映射（用于链接生成）
        if hasattr(self, 'parser') and self.parser:
            self.parser.refid_to_file[refid] = str(rel_path)
        
        self.pages.append((str(rel_path), info.get('title', 'Untitled'), cat.get('order', 99)))
        return rel_path
    
    def generate_summary(self):
        lines = ["# Summary\n\n- [🏠 首页](index.md)\n\n"]
        # 简单分组
        groups = defaultdict(list)
        for path, title, order in self.pages:
            if path in ('index.md', 'main.md'):
                continue
            cat = Path(path).parts[0] if len(Path(path).parts) > 1 else 'other'
            groups[cat].append((path, title))
        
        for cat in sorted(groups.keys()):
            cat_name = CATEGORY_MAP.get(cat, {}).get('name', cat.title())
            lines.append(f"\n# {cat_name}\n\n")
            for path, title in sorted(groups[cat], key=lambda x: x[1]):
                indent = "  " if Path(path).parent != Path('.') else ""
                lines.append(f"{indent}- [{title}]({path})\n")
        return ''.join(lines)


# ============ 主函数 ============
def convert(xml_dir: str, output_dir: str, verbose: bool = False, assets_dir: str = None):
    xml_path = Path(xml_dir).resolve()
    out_path = Path(output_dir).resolve()
    src_path = out_path / "src"
    
    # 确定 assets 目录
    if assets_dir:
        assets_path = Path(assets_dir).resolve()
    else:
        assets_path = DEFAULT_ASSETS_DIR
    
    # 构建完整的文件路径
    mermaid_files = {
        filename: assets_path / filepath
        for filename, filepath in MERMAID_FILES_TEMPLATE.items()
    }
    
    if not (xml_path / 'index.xml').exists():
        raise FileNotFoundError(f"❌ 未找到 index.xml: {xml_path}")
    
    if out_path.exists():
        shutil.rmtree(out_path)
    src_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 解析: {xml_path}")
    parser = DoxygenXMLParser(xml_path)
    parser.verbose = verbose
    parser.load_index()
    
    print(f"✍️  生成页面...")
    generator = MarkdownGenerator(src_path, parser)  # 传递 parser 引用
    
    # 第一遍：建立 refid 到文件路径的映射
    print(f"  📝 第一遍：建立引用映射...")
    for refid in parser.compounds:
        if refid in ('index', 'main'):
            continue
        kind = parser.compounds[refid].get('kind', 'unknown')
        cat = CATEGORY_MAP.get(kind, {})
        filename = f"{refid}.md"
        
        # 计算文件路径
        if kind in ('class', 'struct', 'union'):
            rel_path = Path('classes') / filename
        elif kind == 'file':
            rel_path = Path('files') / filename
        elif kind == 'namespace':
            rel_path = Path('namespaces') / filename
        elif kind == 'dir':
            rel_path = Path('directories') / filename
        elif kind == 'group':
            rel_path = Path('groups') / filename
        elif kind == 'page':
            rel_path = Path('pages') / filename
        else:
            rel_path = Path(filename)
        
        parser.refid_to_file[refid] = str(rel_path)
    
    # 第二遍：生成页面内容
    print(f"  📄 第二遍：生成页面内容...")
    
    # 处理 index/main
    for refid in ['index', 'main']:
        if refid in parser.compounds:
            info = parser.parse_compound(refid)
            if info:
                # 特殊处理：首页命名为 index.md
                rel = generator.generate_page(refid, info)
                if refid == 'index':
                    (src_path / 'index.md').write_text(
                        (src_path / rel).read_text(encoding='utf-8'), encoding='utf-8')
                print(f"  ✅ {refid}")
    
    # 处理其他
    processed = 0
    for refid in parser.compounds:
        if refid in ('index', 'main'):
            continue
        info = parser.parse_compound(refid)
        if info:
            generator.generate_page(refid, info)
            processed += 1
            if processed % 50 == 0:
                print(f"  ... {processed}/{len(parser.compounds)}")
    
    # 生成 SUMMARY
    (src_path / "SUMMARY.md").write_text(generator.generate_summary(), encoding='utf-8')
    
    # 复制 Mermaid 配置文件
    print(f"\n📦 复制 Mermaid 配置文件 (from: {assets_path})...")
    for filename, src_file in mermaid_files.items():
        if src_file.exists():
            dest_file = out_path / filename.replace('.template', '')
            shutil.copy2(src_file, dest_file)
            print(f"  ✅ {filename}")
        else:
            print(f"  ⚠️ 未找到: {src_file}")
    
    # 生成 book.toml（使用模板或默认配置）
    book_toml_template = out_path / 'book.toml.template'
    if book_toml_template.exists():
        # 使用项目中的 book.toml 作为模板
        template_content = book_toml_template.read_text(encoding='utf-8')
        # 移除 .template 后缀的文件
        book_toml_template.unlink()
        (out_path / "book.toml").write_text(template_content, encoding='utf-8')
        print(f"  ✅ 使用自定义 book.toml")
    else:
        # 生成默认 book.toml
        (out_path / "book.toml").write_text(
            f'[book]\ntitle = "API 文档"\nauthors = ["You"]\nsrc = "src"\n\n'
            f'[preprocessor.mermaid]\ncommand = "mdbook-mermaid"\nrenderer = ["html"]\n\n'
            f'[output.html]\nadditional-js = ["mermaid.min.js", "mermaid-init.js"]\n',
            encoding='utf-8'
        )
        print(f"  ✅ 生成默认 book.toml")
    
    print(f"\n🎉 完成! 转换 {processed} 个页面 → {out_path}")
    print(f"🚀 预览: cd {out_path} && mdbook serve")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Doxygen XML → mdBook (修复版)")
    parser.add_argument("xml_dir", help="Doxygen XML 目录")
    parser.add_argument("-o", "--output", default="mdbook_output", help="输出目录")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细日志")
    parser.add_argument("-a", "--assets-dir", default=None, help="Assets 目录路径（包含 mermaid.min.js, mermaid-init.js, book.toml）")
    args = parser.parse_args()
    
    try:
        convert(args.xml_dir, args.output, args.verbose, args.assets_dir)
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        if args.verbose:
            traceback.print_exc()
        exit(1)