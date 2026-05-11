# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sempICP2.0'
copyright = '2026, Semptian Co., Ltd.'
author = 'Semptian Co., Ltd.'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'breathe',
]
highlight_language = 'c++'  # 现在，所有未指定语言的代码块都将按 C++ 高亮

# Import required modules early (before any function calls)
import os
import sys
import re
from pathlib import Path

# Breathe configuration
breathe_projects = {
    "sempICP": "../../doxygen/xml"
}
breathe_default_project = "sempICP"

# Auto-detect language domain based on project type
# This function analyzes the actual files that Doxygen will process
def detect_language_domain():
    """
    Detect the primary language domain by analyzing source files.
    
    This function reads INPUT and EXCLUDE from Doxyfile to determine
    which directories and files Doxygen will actually process,
    ensuring accurate language detection.
    
    Doxygen supports many languages (C, C++, Java, Python, Fortran, VHDL, etc.),
    but Breathe primarily works with C/C++ through Doxygen XML.
    
    For multi-language projects, we detect the dominant language and configure
    Breathe accordingly. Other languages documented by Doxygen will still appear
    in the XML and can be referenced in RST files.
    """
    # from pathlib import Path
    
    conf_dir = Path(__file__).parent.resolve()
    sphinx_dir = conf_dir.parent
    assets_dir = sphinx_dir.parent
    
    # Try to find project root
    doxygen_skill_dir = assets_dir.parent
    if doxygen_skill_dir.name == 'doxygen' and doxygen_skill_dir.parent.name == 'skills':
        project_root = doxygen_skill_dir.parent.parent.parent
    else:
        project_root = assets_dir.parent
    
    # Read Doxyfile to get INPUT and EXCLUDE
    doxyfile_path = project_root / 'Doxyfile'
    input_dirs = []
    exclude_patterns = []
    
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
        
        # Extract INPUT (handle multi-line with backslash continuation)
        # Match from INPUT = to the next non-continued line
        match_input = re.search(r'^\s*INPUT\s*=\s*((?:.+\\\s*)*(?:.+))$', clean_content, re.MULTILINE)
        if match_input:
            input_str = match_input.group(1).strip()
            # Handle multi-line values with backslash continuation
            # First, remove backslash-newline sequences
            input_str = input_str.replace('\\\n', ' ').replace('\\', '')
            # Split by whitespace
            input_dirs = [d.strip() for d in input_str.split() if d.strip()]
        
        # Extract EXCLUDE (handle multi-line with backslash continuation)
        match_exclude = re.search(r'^\s*EXCLUDE\s*=\s*((?:.+\\\s*)*(?:.+))$', clean_content, re.MULTILINE)
        if match_exclude:
            exclude_str = match_exclude.group(1).strip()
            # Handle multi-line values with backslash continuation
            exclude_str = exclude_str.replace('\\\n', ' ').replace('\\', '')
            # Split by whitespace
            exclude_patterns = [p.strip().rstrip('/') for p in exclude_str.split() if p.strip()]
    
    # If no INPUT found, use default directories
    if not input_dirs:
        input_dirs = ['.', 'Src', 'src', 'Source', 'source', 'App', 'Drv', 'Lib', 
                      'include', 'tests', 'Udd', 'Utils']
    
    # Define file patterns for different languages
    # These match Doxygen's FILE_PATTERNS configuration
    language_patterns = {
        'cpp': ['*.cpp', '*.hpp', '*.cxx', '*.hxx', '*.cc', '*.c++', '*.cppm', '*.c++m',
                '*.ii', '*.ixx', '*.ipp', '*.i++', '*.inl', '*.hh', '*.h++'],
        'c': ['*.c'],  # Don't count .h here, will be added separately
        'java': ['*.java'],
        'python': ['*.py', '*.pyw'],
        'fortran': ['*.f90', '*.f95', '*.f03', '*.f08', '*.f18', '*.f', '*.for'],
        'csharp': ['*.cs'],
        'php': ['*.php', '*.php4', '*.php5', '*.phtml', '*.inc'],
        'objective-c': ['*.m', '*.mm'],
        'vhdl': ['*.vhd', '*.vhdl'],
        'idl': ['*.idl', '*.ddl', '*.odl'],
        'dlang': ['*.d'],
        'lex': ['*.l'],
    }
    
    # Count files for each language
    language_counts = {lang: 0 for lang in language_patterns.keys()}
    h_file_count = 0  # Count .h files separately
    
    print(f"\nScanning directories from Doxyfile INPUT: {input_dirs}", file=sys.stderr)
    if exclude_patterns:
        print(f"Excluding patterns: {exclude_patterns}", file=sys.stderr)
    
    for input_dir_name in input_dirs:
        # Handle relative paths
        if Path(input_dir_name).is_absolute():
            src_dir = Path(input_dir_name)
        else:
            src_dir = project_root / input_dir_name
        
        if not src_dir.exists():
            print(f"  Warning: INPUT directory not found: {src_dir}", file=sys.stderr)
            continue
        
        print(f"  Scanning: {src_dir}", file=sys.stderr)
        
        for lang, patterns in language_patterns.items():
            for pattern in patterns:
                try:
                    matches = list(src_dir.rglob(pattern))
                    
                    # Filter out excluded patterns
                    if exclude_patterns:
                        filtered_matches = []
                        for match in matches:
                            excluded = False
                            match_str = str(match.relative_to(project_root)) if match.is_relative_to(project_root) else str(match)
                            for exc_pattern in exclude_patterns:
                                # Check if path starts with the exclude pattern (for directories)
                                if match_str.startswith(exc_pattern + '/') or match_str == exc_pattern:
                                    excluded = True
                                    break
                                # Also check if any parent directory matches
                                for parent in match.parents:
                                    try:
                                        parent_str = str(parent.relative_to(project_root))
                                        if parent_str == exc_pattern or parent_str.startswith(exc_pattern + '/'):
                                            excluded = True
                                            break
                                    except ValueError:
                                        pass
                                if excluded:
                                    break
                            if not excluded:
                                filtered_matches.append(match)
                        matches = filtered_matches
                    
                    language_counts[lang] += len(matches)
                except Exception as e:
                    print(f"  Warning: Error scanning {pattern} in {src_dir}: {e}", file=sys.stderr)
        
        # Count .h files (shared between C and C++)
        try:
            h_matches = list(src_dir.rglob('*.h'))
            if exclude_patterns:
                filtered_h = []
                for match in h_matches:
                    excluded = False
                    match_str = str(match.relative_to(project_root)) if match.is_relative_to(project_root) else str(match)
                    for exc_pattern in exclude_patterns:
                        # Check if path starts with the exclude pattern (for directories)
                        if match_str.startswith(exc_pattern + '/') or match_str == exc_pattern:
                            excluded = True
                            break
                        # Also check if any parent directory matches
                        for parent in match.parents:
                            try:
                                parent_str = str(parent.relative_to(project_root))
                                if parent_str == exc_pattern or parent_str.startswith(exc_pattern + '/'):
                                    excluded = True
                                    break
                            except ValueError:
                                pass
                        if excluded:
                            break
                    if not excluded:
                        filtered_h.append(match)
                h_matches = filtered_h
            h_file_count += len(h_matches)
        except Exception as e:
            print(f"  Warning: Error scanning *.h in {src_dir}: {e}", file=sys.stderr)
    
    # Add .h files to both C and C++ counts
    language_counts['c'] += h_file_count
    language_counts['cpp'] += h_file_count
    
    # Debug output
    print("\n=== Language Detection Summary ===", file=sys.stderr)
    for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {lang:12s}: {count:4d} files", file=sys.stderr)
    print("================================\n", file=sys.stderr)
    sys.stderr.flush()
    
    # Determine primary domain
    # Priority: C++ > C > others (since Breathe works best with C/C++)
    cpp_total = language_counts['cpp']
    c_total = language_counts['c']
    
    if cpp_total > c_total:
        primary_domain = 'cpp'
    else:
        primary_domain = 'c'
    
    print(f"Primary language domain: {primary_domain.upper()}", file=sys.stderr)
    print(f"Note: Other languages (Java, Python, etc.) are supported via Doxygen XML\n", file=sys.stderr)
    sys.stderr.flush()
    
    return primary_domain

language_domain = detect_language_domain()
print(f"Using language domain: {language_domain}", file=sys.stderr)
sys.stderr.flush()

# Breathe domain configuration for multi-language support
# Doxygen generates XML for all supported languages, but Breathe primarily
# renders C/C++ documentation. Other languages can be referenced using
# standard Sphinx directives or custom RST markup.
breathe_domain_by_extension = {
    # C/C++ family (primary support)
    "h": language_domain,
    "hh": "cpp",
    "hpp": "cpp",
    "hxx": "cpp",
    "h++": "cpp",
    "c": language_domain,
    "cc": "cpp",
    "cpp": "cpp",
    "cxx": "cpp",
    "c++": "cpp",
    "cppm": "cpp",
    "c++m": "cpp",
    
    # Other languages (via Doxygen XML, rendered as generic content)
    "java": "cpp",      # Java classes rendered similarly to C++
    "py": "cpp",        # Python modules rendered as generic
    "pyw": "cpp",
    "cs": "cpp",        # C# classes
    "php": "cpp",       # PHP classes
    "php4": "cpp",
    "php5": "cpp",
    "phtml": "cpp",
    "m": "cpp",         # Objective-C
    "mm": "cpp",        # Objective-C++
    "f90": "cpp",       # Fortran
    "f95": "cpp",
    "f03": "cpp",
    "f08": "cpp",
    "f18": "cpp",
    "f": "cpp",
    "for": "cpp",
    "vhd": "cpp",       # VHDL
    "vhdl": "cpp",
    "idl": "cpp",       # IDL
    "ddl": "cpp",
    "odl": "cpp",
    "d": "cpp",         # D language
    "l": "cpp",         # Lex
    "ii": "cpp",        # C++ implementation files
    "ixx": "cpp",
    "ipp": "cpp",
    "i++": "cpp",
    "inl": "cpp",       # Inline files
}

# Optional: Configure Breathe output format
breathe_show_define_initializer = True
breathe_show_enumvalue_initializer = True

# ============================================================================
# MULTI-LANGUAGE SUPPORT DOCUMENTATION
# ============================================================================
#
# This configuration enables Sphinx to document multi-language projects via
# Doxygen XML. Here's how it works:
#
# 1. DOXYGEN'S ROLE:
#    - Doxygen parses source code in 20+ languages (C, C++, Java, Python,
#      Fortran, VHDL, PHP, C#, Objective-C, D, IDL, Lex, etc.)
#    - It generates unified XML output regardless of source language
#    - See Doxyfile FILE_PATTERNS for the complete list
#
# 2. BREATHE'S ROLE:
#    - Breathe reads Doxygen XML and converts it to Sphinx format
#    - Primary support: C/C++ (full rendering with proper formatting)
#    - Secondary support: Other languages (rendered as generic content)
#
# 3. USAGE IN RST FILES:
#
#    For C/C++ files:
#    -----------------
#    .. doxygenfile:: myfile.h
#       :project: sempICP
#
#    .. doxygenclass:: MyClass
#       :project: sempICP
#       :members:
#
#    .. doxygenfunction:: my_function
#       :project: sempICP
#
#    For other languages (Java, Python, etc.):
#    -----------------------------------------
#    # Option A: Use doxygenfile directive (shows entire file)
#    .. doxygenfile:: MyClass.java
#       :project: sempICP
#
#    # Option B: Reference specific entities by name
#    .. doxygenclass:: com.example.MyClass
#       :project: sempICP
#
#    # Option C: Use standard Sphinx directives for better formatting
#    .. py:class:: MyClass
#
#       Description from docstring.
#
#    .. py:function:: my_function(arg1, arg2)
#
#       Function description.
#
# 4. LANGUAGE DETECTION:
#    - The detect_language_domain() function scans your project
#    - It counts files by extension to determine primary language
#    - Output is shown during build (check stderr)
#
# 5. CUSTOMIZATION:
#    - Edit language_patterns dict to add/remove languages
#    - Modify src_dirs to include your project's source directories
#    - Adjust breathe_domain_by_extension for custom mappings
#
# ============================================================================

# If breathe projects path is not found, show warning
# This script can be in two locations:
# 1. Original: .agents/skills/doxygen/.assets/sphinx/source/conf.py
# 2. Installed: <project_root>/.assets/sphinx/source/conf.py

def detect_project_root():
    """Detect project root by looking for Doxyfile."""
    # conf.py location
    conf_dir = Path(__file__).parent.resolve()  # .../sphinx/source
    sphinx_dir = conf_dir.parent  # .../sphinx
    assets_dir = sphinx_dir.parent  # .../.assets
    
    # Try Case 2 first: Original location - .agents/skills/doxygen/.assets
    # This is more specific and should be checked first
    doxygen_skill_dir = assets_dir.parent  # .../doxygen
    if doxygen_skill_dir.name == 'doxygen' and doxygen_skill_dir.parent.name == 'skills':
        # This looks like the original location
        skills_dir = doxygen_skill_dir.parent  # .../skills
        agents_dir = skills_dir.parent  # .../.agents
        potential_root = agents_dir.parent  # project root
        if (potential_root / 'Doxyfile').exists():
            return potential_root
    
    # Try Case 1: Installed location - .assets is in project root
    potential_root = assets_dir.parent  # Could be project root
    if (potential_root / 'Doxyfile').exists():
        # Make sure this is not the original location by checking directory structure
        if not (potential_root.name == 'doxygen' and potential_root.parent.name == 'skills'):
            return potential_root
    
    # Fallback: use current working directory
    return Path.cwd().resolve()

project_root = detect_project_root()
doxyfile_path = project_root / 'Doxyfile'

if doxyfile_path.exists():
    # Try to extract OUTPUT_DIRECTORY from Doxyfile
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
        output_dir = match_od.group(1).strip().strip('"').strip("'")
        xml_path = Path(output_dir) / 'xml'
        if not xml_path.is_absolute():
            xml_path = doxyfile_path.parent / xml_path
        breathe_projects["sempICP"] = str(xml_path.resolve())

xml_path = Path(breathe_projects["sempICP"])
if not xml_path.exists():
    print(f"Warning: Doxygen XML output directory not found: {xml_path}", file=sys.stderr)
    print("Please run 'doxygen Doxyfile' first to generate XML documentation.", file=sys.stderr)
    print(f"Expected path: {xml_path}", file=sys.stderr)

templates_path = ['_templates']
exclude_patterns = []

language = 'zh'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
}
