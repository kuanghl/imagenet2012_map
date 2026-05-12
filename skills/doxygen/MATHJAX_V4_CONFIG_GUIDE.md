# MathJax 4.0 配置指南

## 📋 概述

MathJax 4.0 采用了全新的组件化架构，与 v2.x 版本的配置方式有显著差异。本文档详细说明如何从 `MathJax.Hub.Config` 迁移到新的配置语法。

## 🔄 核心变更对比

### v2.x vs v4.x 配置对照表

| 功能 | MathJax v2.x | MathJax v4.x |
|------|-------------|-------------|
| **配置对象** | `MathJax.Hub.Config({...})` | `window.MathJax = {...}` |
| **输入处理** | `tex2jax` | `tex` |
| **HTML输出** | `"HTML-CSS"` | `chtml` |
| **SVG输出** | `"SVG"` | `svg` |
| **扩展加载** | `extensions: [...]` | `loader: {load: [...]}` |
| **渲染触发** | `Hub.Queue(["Typeset", ...])` | `typesetPromise([...])` |
| **动态渲染** | `Hub.Typeset(element)` | `typeset([element])` |
| **配置时机** | 可在任何时候调用 | **必须**在加载脚本前定义 |

## 🚀 快速开始

### 1. 基础配置（最小化）

```javascript
// 必须在加载 MathJax 脚本之前定义
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
    }
};
```

```html
<!-- 然后加载 MathJax -->
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"></script>
```

### 2. 完整配置示例

参见 [mathjax_config.js](./mathjax_config.js)，包含：
- Loader 配置（组件加载）
- TeX 输入处理器配置
- 输出渲染器配置（CHTML/SVG）
- 无障碍支持选项
- 启动配置

## 📦 组件化架构

MathJax 4.0 将功能拆分为独立组件，按需加载：

### 输入组件（Input Components）
- `input/tex` - TeX/LaTeX 输入
- `input/mml` - MathML 输入
- `input/asciimath` - AsciiMath 输入

### 输出组件（Output Components）
- `output/chtml` - HTML+CSS 输出（**推荐**，性能最佳）
- `output/svg` - SVG 输出（兼容性更好）

### 辅助组件（Auxiliary Components）
- `ui/menu` - 右键菜单
- `a11y/semantic-enrich` - 语义增强（无障碍）
- `a11y/explorer` - 公式探索器

### TeX 扩展包（TeX Extensions）
- `[tex]/ams` - AMS-LaTeX 符号和环境
- `[tex]/mhchem` - 化学方程式
- `[tex]/physics` - 物理符号
- `[tex]/color` - 颜色支持
- `[tex]/noerrors` - 隐藏错误
- `[tex]/noundefined` - 显示未定义宏为文本

## ⚙️ 配置详解

### 0. 完整配置示例

```javascript
window.MathJax = {
    loader: {
        load: ['input/tex', 'output/chtml']
    },
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        tags: 'ams',
        processEscapes: true,
        packages: {
            '[+]': ['ams', 'noerrors', 'noundefined']
        }
    },
    chtml: {
        scale: 1.0,
        fontURL: 'https://cdn.jsdelivr.net/npm/mathjax@4/es5/output/chtml/fonts/woff-v2'
    },
    startup: {
        typeset: true,
        pageReady: () => {
            console.log('MathJax 4.0 is ready');
            return MathJax.startup.defaultPageReady();
        }
    }
};
```

### 1. Loader 配置

```javascript
loader: {
    load: [
        'input/tex',           // 必需：TeX 输入处理器
        'output/chtml',        // 必需：输出渲染器
        
        // 可选扩展
        '[tex]/ams',           // AMS 数学符号
        '[tex]/mhchem',        // 化学方程式
        'a11y/semantic-enrich' // 无障碍支持
    ],
    
    // 自定义组件路径（国内 CDN）
    paths: {
        mathjax: 'https://cdn.jsdelivr.net/npm/mathjax@4/es5'
    }
}
```

### 2. TeX 输入配置

```javascript
tex: {
    // ===== 分隔符配置 =====
    inlineMath: [
        ['$', '$'],           // 单美元符号（行内）
        ['\\(', '\\)']       // 圆括号（传统 LaTeX）
    ],
    displayMath: [
        ['$$', '$$'],         // 双美元符号（块级）
        ['\\[', '\\]']       // 方括号（传统 LaTeX）
    ],
    
    // ===== 公式编号 =====
    tags: 'ams',              // 'ams' (AMS风格), 'all' (全部编号), 'none' (无编号)
    tagSide: 'right',         // 标签位置：'left' 或 'right'
    tagIndent: '0.8em',      // 标签缩进
    
    // ===== 处理选项 =====
    processEscapes: true,     // 处理 \$ 转义（保留字面量 $）
    processEnvironments: true, // 处理 \begin{...}\end{...}
    processRefs: true,        // 处理 \ref{...} 引用
    
    // ===== 扩展包 =====
    packages: {
        '[+]': [              // [+] 表示添加到默认包列表
            'ams',            // AMS-LaTeX
            'noerrors',       // 不显示错误
            'noundefined'     // 未定义宏显示为文本
        ]
    },
    
    // ===== 自定义宏 =====
    macros: {
        RR: '{\\mathbb{R}}',                    // \RR → ℝ
        bold: ['{\\mathbf{#1}}', 1],            // \bold{x} → x (粗体)
        set: ['\\{ #1 \\}', 1]                  // \set{x} → {x}
    }
}
```

### 3. 输出渲染器配置

#### CHTML（HTML+CSS）配置

```javascript
chtml: {
    scale: 1.0,               // 全局缩放因子（1.0 = 100%）
    minScale: 0.5,            // 最小缩放（防止过小）
    mtextInheritFont: false,  // \text{} 是否继承页面字体
    merrorInheritFont: true,  // 错误消息是否继承页面字体
    fontURL: 'https://cdn.jsdelivr.net/npm/mathjax@4/es5/output/chtml/fonts/woff-v2',
    matchFontHeight: true     // 匹配周围文本的字体高度
}
```

#### SVG 配置（备选）

```javascript
svg: {
    scale: 1.0,
    fontCache: 'global',      // 'global', 'local', 'none'
    internalSpeechTitles: true, // SVG 内部语音标题
    titleID: 0                // 标题 ID 起始值
}
```

### 4. 无障碍配置

```javascript
options: {
    ignoreHtmlClass: 'tex2jax_ignore',   // 跳过此类元素
    processHtmlClass: 'tex2jax_process', // 仅处理此类元素
    renderActions: {
        addMenu: [150, '', ''],          // 禁用右键菜单
        addAssistiveMml: [160, '', '']   // 启用辅助 MathML（屏幕阅读器）
    }
}
```

### 5. 启动配置

```javascript
startup: {
    typeset: true,            // 页面加载时自动渲染
    pageReady: () => {
        console.log('MathJax 4.0 is ready');
        return MathJax.startup.defaultPageReady();
    }
}
```

## 🔧 Doxygen 集成

### 方法 1：HTML_HEADER

在 `Doxyfile` 中配置：

```
HTML_HEADER = path/to/header.html
```

在 `header.html` 中：

```html
<head>
<!-- MathJax 4.0 Configuration -->
<script>
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        tags: 'ams'
    }
};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"></script>
</head>
```

### 方法 2：HTML_EXTRA_FILES

在 `Doxyfile` 中配置：

```
HTML_EXTRA_FILES = path/to/mathjax_config.js
```

然后在 `HTML_HEADER` 中引用：

```html
<script src="$relpath^mathjax_config.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"></script>
```

## 🎯 常见场景配置

### 场景 1：仅使用 $ 和 $$ 分隔符

```javascript
window.MathJax = {
    tex: {
        inlineMath: [['$', '$']],
        displayMath: [['$$', '$$']],
        processEscapes: true  // 允许 \$ 转义
    }
};
```

### 场景 2：启用化学方程式

```javascript
window.MathJax = {
    loader: {
        load: ['input/tex', 'output/chtml', '[tex]/mhchem']
    },
    tex: {
        packages: {
            '[+]': ['mhchem']
        }
    }
};
```

使用：`\ce{H2O + CO2 -> H2CO3}`

### 场景 3：启用物理符号

```javascript
window.MathJax = {
    loader: {
        load: ['input/tex', 'output/chtml', '[tex]/physics']
    },
    tex: {
        packages: {
            '[+]': ['physics']
        }
    }
};
```

使用：`\dv{f}{x}`, `\grad`, `\div`, `\curl`

### 场景 4：禁用自动渲染（手动控制）

```javascript
window.MathJax = {
    startup: {
        typeset: false  // 禁用自动渲染
    }
};

// 页面加载后手动触发
document.addEventListener('DOMContentLoaded', () => {
    MathJax.typesetPromise();
});
```

### 场景 5：动态内容渲染

```javascript
// 插入新内容后重新渲染
const element = document.getElementById('content');
element.innerHTML = 'New formula: $E = mc^2$';

// 异步渲染
MathJax.typesetPromise([element])
    .then(() => console.log('Rendering complete'))
    .catch(err => console.error('Rendering failed:', err));
```

## 🐛 常见问题

### Q1: 公式不显示？

**检查清单：**
1. ✅ 配置是否在加载脚本**之前**定义？
2. ✅ CDN 地址是否正确？
3. ✅ 浏览器控制台是否有错误？
4. ✅ 分隔符是否匹配配置？

**解决方案：**
```javascript
// 确保顺序正确
<script>
window.MathJax = { /* config */ };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"></script>
```

### Q2: $ 符号被误解析？

**解决方案：**
```javascript
tex: {
    processEscapes: true  // 启用转义
}
```

使用 `\$` 表示字面量美元符号。

### Q3: 渲染速度慢？

**优化建议：**
1. 使用 `output/chtml` 而非 `output/svg`（更快）
2. 只加载需要的扩展包
3. 使用 `defer` 属性加载脚本
4. 考虑本地部署 MathJax

### Q4: 特殊符号缺失？

**解决方案：**
```javascript
loader: {
    load: ['[tex]/ams']  // 加载 AMS 扩展
},
tex: {
    packages: {
        '[+]': ['ams']
    }
}
```

### Q5: 从 v2.x 迁移 API 调用？

**对照表：**

| v2.x API | v4.x API | 说明 |
|----------|----------|------|
| `MathJax.Hub.Config()` | `window.MathJax = {}` | 配置方式改变 |
| `Hub.Queue(["Typeset", Hub, elem])` | `typesetPromise([elem])` | 异步渲染 |
| `Hub.Typeset(elem)` | `typeset([elem])` | 同步渲染 |
| `Hub.Register.StartupHook()` | `startup.pageReady()` | 启动钩子 |

## 📊 性能对比

| 指标 | MathJax v2.x | MathJax v4.x | 提升 |
|------|-------------|-------------|------|
| 文件大小 | ~600KB | ~40-150KB | ↓ 75-93% |
| 渲染速度 | 基准 | +50% | ↑ 50% |
| 内存占用 | 基准 | -25% | ↓ 25% |
| 首次加载 | 慢 | 快 | ↑ 显著 |

## 🔗 参考资源

- [MathJax 4.0 官方文档](https://docs.mathjax.org/en/latest/)
- [MathJax GitHub](https://github.com/mathjax/MathJax)
- [配置选项完整列表](https://docs.mathjax.org/en/latest/options/index.html)
- [TeX 扩展包列表](https://docs.mathjax.org/en/latest/input/tex/extensions/index.html)
- [迁移指南 v2→v3→v4](https://docs.mathjax.org/en/latest/upgrading/v2.html)

## 📝 总结

MathJax 4.0 的核心变化：
1. **组件化架构** - 按需加载，减小体积
2. **配置前置** - 必须在加载脚本前定义
3. **API 现代化** - Promise-based，异步友好
4. **性能优化** - 渲染速度提升 50%，体积减少 75%

迁移步骤：
1. 将 `MathJax.Hub.Config()` 改为 `window.MathJax = {}`
2. 更新配置键名（`tex2jax` → `tex`，`"HTML-CSS"` → `chtml`）
3. 使用 `loader.load` 替代 `extensions`
4. 更新 API 调用（`Hub.Queue` → `typesetPromise`）

---

**版本**: 1.0  
**最后更新**: 2026-05-12  
**适用版本**: MathJax 4.0+
