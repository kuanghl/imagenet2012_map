#!/usr/bin/env python3
"""
doxygen_tools.py - Doxygen helper script.

Commands:
    install <dest_dir>          Copy Doxyfile, .assets, and this script to destination.
    build                       Run doxygen using Doxyfile in current directory.
    serve [--port PORT] [--open] Build and serve HTML.
    sphinx-build                Build Sphinx documentation from Doxygen XML.
    sphinx-serve [--port PORT] [--open] Build and serve Sphinx documentation.
    sphinx-gen-structure        Generate hierarchical directory structure from Doxygen XML.

Environment Setup:
    Before using sphinx commands, set up Python environment:
    
    # Create virtual environment
    python3 -m venv .venv
    
    # Activate virtual environment (Linux/MacOS)
    source .venv/bin/activate
    
    # Activate virtual environment (Windows)
    .venv\\Scripts\\activate
    
    # Install dependencies
    pip install sphinx breathe sphinx-rtd-theme
"""

import sys
import os
import shutil
import subprocess
import argparse
import re
import webbrowser
import xml.etree.ElementTree as ET
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from collections import defaultdict


def get_project_root():
    """
    Detect project root directory.
    
    The script can be in two locations:
    1. Original: .agents/skills/doxygen/doxygen_tools.py
    2. Installed: <project_root>/doxygen_tools.py
    
    Returns the project root directory path.
    """
    script_dir = Path(__file__).parent.resolve()
    
    # Check if this is the installed location (script is in project root)
    # Key indicators: Doxyfile exists AND .assets directory exists in same location
    if (script_dir / 'Doxyfile').exists() and (script_dir / '.assets').exists():
        # This could be either installed location or original location
        # Check if there's a parent .agents directory (indicates original location)
        if script_dir.name == 'doxygen' and script_dir.parent.name == 'skills':
            # This is the original location: .agents/skills/doxygen
            # Navigate up: doxygen -> skills -> .agents -> project_root
            potential_root = script_dir.parent.parent.parent
            if (potential_root / 'Doxyfile').exists():
                return potential_root
        else:
            # This is the installed location: script is directly in project root
            return script_dir
    
    # Check if this is the original location (.agents/skills/doxygen)
    # by checking the directory structure
    if script_dir.name == 'doxygen' and script_dir.parent.name == 'skills':
        potential_root = script_dir.parent.parent.parent
        if (potential_root / 'Doxyfile').exists():
            return potential_root
    
    # Fallback: assume current working directory is project root
    return Path.cwd().resolve()


def find_doxygen_config(config_file='Doxyfile'):
    """Extract OUTPUT_DIRECTORY and HTML_OUTPUT from Doxyfile."""
    output_dir = None
    html_output = 'html'
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"{config_file} not found in current directory.")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments (both # and ##)
    lines = []
    for line in content.splitlines():
        if '#' in line:
            line = line.split('#')[0]
        lines.append(line)
    clean_content = '\n'.join(lines)
    
    match_od = re.search(r'^\s*OUTPUT_DIRECTORY\s*=\s*(.+?)\s*$', clean_content, re.MULTILINE)
    if match_od:
        output_dir = match_od.group(1).strip().strip('"').strip("'")
    match_ho = re.search(r'^\s*HTML_OUTPUT\s*=\s*(.+?)\s*$', clean_content, re.MULTILINE)
    if match_ho:
        html_output = match_ho.group(1).strip().strip('"').strip("'")
    
    if output_dir is None:
        output_dir = '.'
    if html_output is None or html_output == '':
        html_output = 'html'
    
    html_index = Path(output_dir) / html_output / 'index.html'
    return html_index.resolve()


def run_doxygen():
    """Execute 'doxygen Doxyfile'."""
    if not os.path.exists('Doxyfile'):
        print("Error: Doxyfile not found in current directory.", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(['doxygen', 'Doxyfile'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"doxygen failed with error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'doxygen' command not found. Please install doxygen.", file=sys.stderr)
        sys.exit(1)


def serve_docs(port=3001, open_browser=False):
    """Build documentation and serve it (manual Ctrl+C to stop)."""
    # Step 1: Build
    print("Building documentation with doxygen...")
    run_doxygen()
    
    # Step 2: Locate index.html
    try:
        index_path = find_doxygen_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    serve_dir = index_path.parent
    if not serve_dir.exists():
        print(f"Error: HTML output directory not found: {serve_dir}. Build may have failed.", file=sys.stderr)
        sys.exit(1)
    
    os.chdir(serve_dir)
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            return super().do_GET()
    
    try:
        server = HTTPServer(('', port), CustomHandler)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {port} is already in use. Please choose a different port using --port.", file=sys.stderr)
            sys.exit(1)
        else:
            raise
    
    url = f'http://localhost:{port}'
    print(f"Serving documentation at {url}")
    print("Press Ctrl+C to stop the server.")
    if open_browser:
        webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server (Ctrl+C).")
        server.shutdown()


def install_files(dest_dir, doxyfile_name='Doxyfile'):
    """
    Copy Doxyfile, .assets, and this script to dest_dir.
    
    Args:
        dest_dir: Destination directory
        doxyfile_name: Name of the Doxyfile to install (default: 'Doxyfile').
                      If specified as 'sempICP', will install 'Doxyfile.sempICP' as 'Doxyfile'.
    """
    script_dir = Path(__file__).parent.resolve()
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which Doxyfile to use
    if doxyfile_name == 'Doxyfile':
        doxyfile_src = script_dir / 'Doxyfile'
    else:
        # Support custom Doxyfile names like 'Doxyfile.sempICP'
        doxyfile_src = script_dir / f'Doxyfile.{doxyfile_name}'
        if not doxyfile_src.exists():
            print(f"Warning: {doxyfile_src} not found, falling back to Doxyfile", file=sys.stderr)
            doxyfile_src = script_dir / 'Doxyfile'
    
    items = [
        (doxyfile_src, dest_dir / "Doxyfile"),
        (script_dir / ".assets", dest_dir / ".assets"),
        (script_dir / "doxygen_tools.py", dest_dir / "doxygen_tools.py"),
    ]
    for src, dst in items:
        if src.is_file():
            shutil.copy2(src, dst)
            print(f"Copied file: {src} -> {dst}")
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Copied directory: {src} -> {dst}")
        else:
            print(f"Warning: source not found: {src}", file=sys.stderr)
    
    if sys.platform != "win32":
        dest_script = dest_dir / "doxygen_tools.py"
        if dest_script.exists():
            dest_script.chmod(dest_script.stat().st_mode | 0o111)
            print(f"Set executable permission on {dest_script}")
    
    print(f"\nInstallation complete. Files installed to {dest_dir}")


def find_doxygen_xml(config_file='Doxyfile'):
    """Extract XML_OUTPUT directory from Doxyfile."""
    xml_output = 'xml'
    output_dir = '.'
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"{config_file} not found in current directory.")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    lines = []
    for line in content.splitlines():
        if '#' in line:
            line = line.split('#')[0]
        lines.append(line)
    clean_content = '\n'.join(lines)
    
    match_od = re.search(r'^\s*OUTPUT_DIRECTORY\s*=\s*(.+?)\s*$', clean_content, re.MULTILINE)
    if match_od:
        output_dir = match_od.group(1).strip().strip('"').strip("'")
    
    match_xo = re.search(r'^\s*XML_OUTPUT\s*=\s*(.+?)\s*$', clean_content, re.MULTILINE)
    if match_xo:
        xml_output = match_xo.group(1).strip().strip('"').strip("'")
    
    xml_path = Path(output_dir) / xml_output
    return xml_path.resolve()


def build_sphinx():
    """Build Sphinx documentation from Doxygen XML."""
    # Step 1: Check if Doxygen XML exists
    try:
        xml_path = find_doxygen_xml()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not xml_path.exists():
        print(f"Error: Doxygen XML output directory not found: {xml_path}", file=sys.stderr)
        print("Please run 'doxygen Doxyfile' first to generate XML documentation.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found Doxygen XML at: {xml_path}")
    
    # Step 2: Build Sphinx
    # Detect project root (works for both original and installed locations)
    project_root = get_project_root()
    
    # Sphinx source is in .assets/sphinx/source (relative to script location)
    script_dir = Path(__file__).parent.resolve()
    sphinx_source_dir = script_dir / '.assets' / 'sphinx' / 'source'
    
    if not sphinx_source_dir.exists():
        print(f"Error: Sphinx source directory not found: {sphinx_source_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Get OUTPUT_DIRECTORY from Doxyfile and append /sphinx
    doxyfile_path = project_root / 'Doxyfile'
    output_base = None
    
    if doxyfile_path.exists():
        with open(doxyfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments
        lines = []
        for line in content.splitlines():
            if '#' in line:
                line = line.split('#')[0]
            lines.append(line)
        clean_content = '\n'.join(lines)
        
        match_od = re.search(r'^\s*OUTPUT_DIRECTORY\s*=\s*(.+?)\s*$', clean_content, re.MULTILINE)
        if match_od:
            output_base = match_od.group(1).strip().strip('"').strip("'")
    
    if output_base is None:
        output_base = 'docs/doxygen'
    
    # Construct sphinx output path: OUTPUT_DIRECTORY/sphinx
    sphinx_output = Path(output_base) / 'sphinx'
    if not sphinx_output.is_absolute():
        sphinx_output = project_root / sphinx_output
    sphinx_output = sphinx_output.resolve()
    
    # Create output directory if it doesn't exist
    sphinx_output.mkdir(parents=True, exist_ok=True)
    
    print(f"Building Sphinx documentation...")
    print(f"Source: {sphinx_source_dir}")
    print(f"Output: {sphinx_output}")
    
    try:
        subprocess.run(
            ['sphinx-build', '-b', 'html', str(sphinx_source_dir), str(sphinx_output)],
            check=True
        )
        print(f"\nSphinx build complete! Output: {sphinx_output}")
    except subprocess.CalledProcessError as e:
        print(f"Sphinx build failed with error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'sphinx-build' command not found.", file=sys.stderr)
        print("Please set up Python environment and install dependencies:", file=sys.stderr)
        print("  1. python3 -m venv .venv", file=sys.stderr)
        print("  2. source .venv/bin/activate", file=sys.stderr)
        print("  3. pip install sphinx breathe sphinx-rtd-theme", file=sys.stderr)
        sys.exit(1)


def serve_sphinx_docs(port=3002, open_browser=False):
    """Build and serve Sphinx documentation."""
    # Step 1: Build Sphinx
    print("Building Sphinx documentation...")
    build_sphinx()
    
    # Step 2: Locate index.html (output is in docs/doxygen/sphinx)
    project_root = get_project_root()
    doxyfile_path = project_root / 'Doxyfile'
    output_base = None
    
    if doxyfile_path.exists():
        with open(doxyfile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments
        lines = []
        for line in content.splitlines():
            if '#' in line:
                line = line.split('#')[0]
            lines.append(line)
        clean_content = '\n'.join(lines)
        
        match_od = re.search(r'^\s*OUTPUT_DIRECTORY\s*=\s*(.+?)\s*$', clean_content, re.MULTILINE)
        if match_od:
            output_base = match_od.group(1).strip().strip('"').strip("'")
    
    if output_base is None:
        output_base = 'docs/doxygen'
    
    html_dir = Path(output_base) / 'sphinx'
    if not html_dir.is_absolute():
        html_dir = project_root / html_dir
    html_dir = html_dir.resolve()
    
    if not html_dir.exists():
        print(f"Error: Sphinx HTML output directory not found: {html_dir}", file=sys.stderr)
        sys.exit(1)
    
    os.chdir(html_dir)
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            return super().do_GET()
    
    try:
        server = HTTPServer(('', port), CustomHandler)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {port} is already in use. Please choose a different port using --port.", file=sys.stderr)
            sys.exit(1)
        else:
            raise
    
    url = f'http://localhost:{port}'
    print(f"Serving Sphinx documentation at {url}")
    print("Press Ctrl+C to stop the server.")
    if open_browser:
        webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server (Ctrl+C).")
        server.shutdown()


def generate_sphinx_structure():
    """
    Generate hierarchical Sphinx directory structure from Doxygen XML.
    
    This creates organized RST files grouped by source files:
    - C headers (.h)
    - C sources (.c)
    - C++ headers (.hpp, .hxx)
    - C++ sources (.cpp, .cc)
    - Java files (.java)
    - Python files (.py)
    - Other files
    """
    # Detect project root
    project_root = get_project_root()
    
    # Find Doxygen XML directory
    try:
        xml_path = find_doxygen_xml()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not xml_path.exists():
        print(f"Error: Doxygen XML output directory not found: {xml_path}", file=sys.stderr)
        print("Please run 'doxygen Doxyfile' first to generate XML documentation.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found Doxygen XML at: {xml_path}")
    
    # Determine Sphinx source directory
    script_dir = Path(__file__).parent.resolve()
    sphinx_source = script_dir / '.assets' / 'sphinx' / 'source'
    
    if not sphinx_source.exists():
        print(f"Error: Sphinx source directory not found: {sphinx_source}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Sphinx source directory: {sphinx_source}")
    print(f"\nGenerating hierarchical structure...")
    print(f"This will create organized RST files grouped by source files.")
    print()
    
    # Run the generator
    try:
        _generate_structure_internal(xml_path, sphinx_source)
        
        print(f"\n✓ Structure generation complete!")
        print(f"\nGenerated directories:")
        print(f"  - {sphinx_source}/c_headers/")
        print(f"  - {sphinx_source}/c_sources/")
        print(f"  - {sphinx_source}/cpp_headers/")
        print(f"  - {sphinx_source}/cpp_sources/")
        print(f"  - {sphinx_source}/java_files/")
        print(f"  - {sphinx_source}/python_files/")
        print(f"  - {sphinx_source}/other_files/")
        print(f"\nNext steps:")
        print(f"  1. Review the generated RST files")
        print(f"  2. Run 'python3 doxygen_tools.py sphinx-build' to rebuild documentation")
        print(f"  3. Customize the generated files as needed")
        
    except Exception as e:
        print(f"Error: Structure generation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _generate_structure_internal(xml_dir: Path, output_dir: Path):
    """
    Internal function to generate Sphinx structure from Doxygen XML.
    This is the merged functionality from generate_sphinx_structure_v2.py
    """
    index_xml = xml_dir / 'index.xml'
    
    if not index_xml.exists():
        print(f"Error: {index_xml} not found")
        sys.exit(1)
    
    # Parse index.xml
    print(f"Parsing {index_xml}...")
    tree = ET.parse(index_xml)
    root = tree.getroot()
    
    files_data = {}  # filename -> {classes, functions, macros, ...}
    namespaces = {}
    groups = {}
    
    file_count = 0
    for compound in root.findall('compound'):
        kind = compound.get('kind')
        refid = compound.get('refid')
        name_elem = compound.find('name')
        name = name_elem.text if name_elem is not None else ''
        
        if kind == 'file':
            files_data[name] = {
                'refid': refid,
                'classes': [],
                'functions': [],
                'macros': [],
                'enums': [],
                'typedefs': [],
                'variables': []
            }
            file_count += 1
        elif kind == 'namespace':
            namespaces[refid] = name
        elif kind == 'group':
            groups[refid] = name
    
    print(f"Found {file_count} files")
    print(f"Found {len(namespaces)} namespaces")
    print(f"Found {len(groups)} groups")
    
    # Create directory structure
    dirs = [
        'c_sources',      # C 源文件 (.c)
        'c_headers',      # C 头文件 (.h)
        'cpp_sources',    # C++ 源文件 (.cpp, .cc, .cxx)
        'cpp_headers',    # C++ 头文件 (.hpp, .hxx, .hh)
        'java_files',     # Java 文件
        'python_files',   # Python 文件
        'other_files',    # 其他语言
    ]
    for d in dirs:
        dir_path = output_dir / d
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Created directory structure")
    
    # Parse file details
    print("\nParsing file details...")
    
    def parse_file_details(filename: str, refid: str):
        """Parse single file details"""
        xml_file = xml_dir / f'{refid}.xml'
        if not xml_file.exists():
            return
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Find all member definitions
            for sectiondef in root.findall('.//sectiondef'):
                kind = sectiondef.get('kind')
                
                for memberdef in sectiondef.findall('memberdef'):
                    member_kind = memberdef.get('kind')
                    name_elem = memberdef.find('name')
                    if name_elem is None:
                        continue
                    
                    member_name = name_elem.text
                    
                    # Extract brief description
                    brief_desc = ''
                    brief_elem = memberdef.find('briefdescription')
                    if brief_elem is not None:
                        brief_desc = ''.join(brief_elem.itertext()).strip()
                    
                    info = {
                        'name': member_name,
                        'brief': brief_desc,
                        'kind': member_kind
                    }
                    
                    # Categorize and store
                    if member_kind in ('function',):
                        files_data[filename]['functions'].append(info)
                    elif member_kind in ('class', 'struct'):
                        files_data[filename]['classes'].append(info)
                    elif member_kind == 'define':
                        files_data[filename]['macros'].append(info)
                    elif member_kind == 'enum':
                        files_data[filename]['enums'].append(info)
                    elif member_kind == 'typedef':
                        files_data[filename]['typedefs'].append(info)
                    elif member_kind == 'variable':
                        files_data[filename]['variables'].append(info)
        
        except Exception as e:
            print(f"Warning: Error parsing {xml_file}: {e}")
    
    # Parse each file's details
    for filename, data in files_data.items():
        parse_file_details(filename, data['refid'])
    
    # Helper functions
    def categorize_file(filename: str) -> str:
        """Categorize file by extension"""
        ext = Path(filename).suffix.lower()
        
        if ext in ['.c']:
            return 'c_sources'
        elif ext in ['.h']:
            return 'c_headers'
        elif ext in ['.cpp', '.cc', '.cxx', '.c++']:
            return 'cpp_sources'
        elif ext in ['.hpp', '.hxx', '.hh', '.h++']:
            return 'cpp_headers'
        elif ext in ['.java']:
            return 'java_files'
        elif ext in ['.py', '.pyw']:
            return 'python_files'
        else:
            return 'other_files'
    
    def generate_file_rst(filename: str, data: dict) -> str:
        """Generate RST content for a single file"""
        # Title
        title = filename
        rst = f"{title}\n{'=' * len(title)}\n\n"
        
        # File description
        rst += f"**文件**: `{filename}`\n\n"
        
        # Use doxygenfile directive to show complete file documentation
        rst += f""".. doxygenfile:: {filename}
   :project: sempICP

"""
        
        # If has classes/structs, add detailed list
        if data['classes']:
            rst += f"\n**类和结构** ({len(data['classes'])})\n"
            rst += "-" * 40 + "\n\n"
            for cls in data['classes']:
                rst += f".. doxygen{cls['kind']}:: {cls['name']}\n\n"
        
        # If has functions, add detailed list
        if data['functions']:
            rst += f"\n**函数** ({len(data['functions'])})\n"
            rst += "-" * 40 + "\n\n"
            for func in data['functions'][:20]:  # Limit to first 20
                # Only use the function name, not the brief description
                rst += f".. doxygenfunction:: {func['name']}\n\n"
            
            if len(data['functions']) > 20:
                rst += f"*... 还有 {len(data['functions']) - 20} 个函数*\n\n"
        
        # If has macros, add list
        if data['macros']:
            rst += f"\n**宏定义** ({len(data['macros'])})\n"
            rst += "-" * 40 + "\n\n"
            for macro in data['macros'][:15]:
                rst += f"- ``{macro['name']}``"
                if macro['brief']:
                    rst += f" - {macro['brief']}"
                rst += "\n"
            
            if len(data['macros']) > 15:
                rst += f"\n*... 还有 {len(data['macros']) - 15} 个宏*\n"
            rst += "\n"
        
        # If has enums, add list
        if data['enums']:
            rst += f"\n**枚举** ({len(data['enums'])})\n"
            rst += "-" * 40 + "\n\n"
            for enum in data['enums']:
                rst += f".. doxygenenum:: {enum['name']}\n\n"
        
        return rst
    
    def generate_category_index(category: str, display_name: str, files_dict: dict) -> str:
        """Generate category index page"""
        # Use proper underline length
        # RST requires underline to match title length visually
        # For safety, use at least the byte length divided by average Chinese char width (2)
        underline_len = max(len(display_name), len(display_name.encode('utf-8')))
        rst = f"{display_name}\n{'=' * underline_len}\n\n"
        
        if not files_dict:
            rst += "暂无文件。\n"
            return rst
        
        # Sort by filename
        sorted_files = sorted(files_dict.keys())
        
        # Add toctree
        rst += f".. toctree::\n   :maxdepth: 1\n   :glob:\n\n   {category}/*\n\n"
        
        # File list
        rst += f"文件列表 ({len(sorted_files)})\n"
        rst += "-" * 40 + "\n\n"
        
        for filename in sorted_files:
            data = files_dict[filename]
            # Count items
            items = []
            if data['classes']:
                items.append(f"{len(data['classes'])} 类")
            if data['functions']:
                items.append(f"{len(data['functions'])} 函数")
            if data['macros']:
                items.append(f"{len(data['macros'])} 宏")
            
            summary = ", ".join(items) if items else "空文件"
            rst += f"- :doc:`{category}/{Path(filename).stem}` - **{filename}** ({summary})\n"
        
        rst += "\n"
        return rst
    
    def generate_main_index(categories: dict) -> str:
        """Generate main category index"""
        rst = """API 文档（按文件组织）
========================

本文档按源文件组织，每个文件包含其中定义的所有类、函数、宏等。

.. toctree::
   :maxdepth: 2
   :caption: 按语言分类

"""
        
        # Add categories with content
        category_order = [
            ('c_headers', 'C 头文件'),
            ('c_sources', 'C 源文件'),
            ('cpp_headers', 'C++ 头文件'),
            ('cpp_sources', 'C++ 源文件'),
            ('java_files', 'Java 文件'),
            ('python_files', 'Python 文件'),
            ('other_files', '其他文件'),
        ]
        
        for category, display_name in category_order:
            if category in categories:
                rst += f"   {category}\n"
        
        rst += "\n"
        return rst
    
    # Group files by category
    print("Generating RST files...")
    categories = defaultdict(dict)
    for filename, data in files_data.items():
        category = categorize_file(filename)
        categories[category][filename] = data
    
    # Generate RST for each file
    total_files = 0
    for category, files_dict in categories.items():
        category_dir = output_dir / category
        
        for filename, data in files_dict.items():
            rst_content = generate_file_rst(filename, data)
            
            # Use filename (without extension) as RST filename
            rst_filename = Path(filename).stem + '.rst'
            output_file = category_dir / rst_filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rst_content)
            
            total_files += 1
    
    print(f"Generated {total_files} file documentation pages")
    
    # Generate category indexes
    category_names = {
        'c_sources': 'C 源文件 (.c)',
        'c_headers': 'C 头文件 (.h)',
        'cpp_sources': 'C++ 源文件 (.cpp, .cc)',
        'cpp_headers': 'C++ 头文件 (.hpp, .hxx)',
        'java_files': 'Java 文件',
        'python_files': 'Python 文件',
        'other_files': '其他文件',
    }
    
    for category, display_name in category_names.items():
        if category in categories:
            index_content = generate_category_index(
                category, 
                display_name, 
                categories[category]
            )
            index_file = output_dir / f"{category}.rst"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
            print(f"Generated index: {category}.rst ({len(categories[category])} files)")
    
    # Generate main index
    main_index = generate_main_index(categories)
    with open(output_dir / 'api_by_file.rst', 'w', encoding='utf-8') as f:
        f.write(main_index)
    
    print(f"\n✓ Generation complete!")
    print(f"  Total files documented: {total_files}")
    print(f"  Categories: {len(categories)}")


def main():
    parser = argparse.ArgumentParser(description="Doxygen Tools - manage Doxygen documentation generation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # install
    install_parser = subparsers.add_parser("install", help="Install Doxyfile, .assets and this script to destination")
    install_parser.add_argument("dest_dir", help="Destination directory")
    install_parser.add_argument("--name", type=str, default='Doxyfile', 
                               help="Doxyfile name to install (default: 'Doxyfile'). "
                                    "Use '--name sempICP' to install 'Doxyfile.sempICP' as 'Doxyfile'")
    
    # build
    subparsers.add_parser("build", help="Run doxygen using Doxyfile in current directory")
    
    # serve
    serve_parser = subparsers.add_parser("serve", help="Build and serve generated HTML documentation")
    serve_parser.add_argument("--port", type=int, default=3001, help="Port number (default: 3001)")
    serve_parser.add_argument("--open", action="store_true", help="Automatically open browser")
    
    # sphinx-build
    subparsers.add_parser("sphinx-build", help="Build Sphinx documentation from Doxygen XML")
    
    # sphinx-serve
    sphinx_serve_parser = subparsers.add_parser("sphinx-serve", help="Build and serve Sphinx documentation")
    sphinx_serve_parser.add_argument("--port", type=int, default=3002, help="Port number (default: 3002)")
    sphinx_serve_parser.add_argument("--open", action="store_true", help="Automatically open browser")
    
    # sphinx-gen-structure
    subparsers.add_parser("sphinx-gen-structure", help="Generate hierarchical directory structure from Doxygen XML")
    
    args = parser.parse_args()
    
    if args.command == "install":
        install_files(args.dest_dir, doxyfile_name=args.name)
    elif args.command == "build":
        run_doxygen()
    elif args.command == "serve":
        serve_docs(port=args.port, open_browser=args.open)
    elif args.command == "sphinx-build":
        build_sphinx()
    elif args.command == "sphinx-serve":
        serve_sphinx_docs(port=args.port, open_browser=args.open)
    elif args.command == "sphinx-gen-structure":
        generate_sphinx_structure()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()