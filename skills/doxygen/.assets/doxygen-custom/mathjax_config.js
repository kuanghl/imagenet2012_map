// MathJax 4.0 Configuration for Doxygen
// This file is included via MATHJAX_CODEFILE in Doxyfile
// It will be merged with Doxygen's default MathJax configuration

window.MathJax = {
    // Merge with Doxygen's default options
    options: {
        ignoreHtmlClass: 'tex2jax_ignore',
        processHtmlClass: 'tex2jax_process'
    },
    
    // TeX input processor configuration
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        tags: 'ams',              // 'ams', 'none', or 'all'
        processEscapes: true,     // Handle \$ as literal dollar sign
        packages: {
            '[+]': ['ams', 'noerrors', 'noundefined']
        }
    }
};

