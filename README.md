# markcraft

markcraft is a fast, extensible Markdown parser written in pure Python.
It targets CommonMark behavior and keeps parser internals open for custom tokens
and custom renderers.

## Why markcraft

- **Fast enough for large documents** while staying pure Python.
- **CommonMark-oriented parsing** with deterministic token precedence.
- **Extensible architecture** for custom block/span tokens and renderers.
- **Multiple built-in outputs**: HTML, LaTeX, AST, and Markdown.

## Installation

Install from PyPI:

```sh
pip install markcraft
```

For local development (uv + Python 3.13):

```sh
git clone https://github.com/niu2x/markcraft.git
cd markcraft
uv sync
```

## Quick Start

### Python API

```python
import markcraft

with open("example.md", "r", encoding="utf-8") as fin:
    html = markcraft.render(fin)
```

Use another renderer:

```python
import markcraft
from markcraft.renderers.latex import LaTeXRenderer

with open("example.md", "r", encoding="utf-8") as fin:
    latex = markcraft.render(fin, LaTeXRenderer)
```

Structured namespaces are also available:

```python
from markcraft.renderers import HtmlRenderer

with HtmlRenderer() as renderer:
    doc = renderer.parse("# hello\n")
    html = renderer.render(doc)
```

Explicit parse entrypoints are available when you want parsing to be intentional:

```python
import markcraft
from markcraft.renderers import MarkdownRenderer

doc = markcraft.parse("a\n\n[b]: /uri\n")

with MarkdownRenderer() as renderer:
    renderer_specific_doc = markcraft.parse("a\n\n[b]: /uri\n", renderer)
    markdown = renderer.render(renderer_specific_doc)
```

## Output Formats

### Core renderers

- `markcraft.renderers.HtmlRenderer`
- `markcraft.renderers.LaTeXRenderer`
- `markcraft.renderers.AstRenderer`
- `markcraft.renderers.MarkdownRenderer`

### Contrib renderers

- `markcraft.extensions.mathjax.MathJaxRenderer`
- `markcraft.extensions.pygments_renderer.PygmentsRenderer`
- `markcraft.extensions.toc_renderer.TocRenderer`
- `markcraft.extensions.github_wiki.GithubWikiRenderer`
- `markcraft.extensions.jira_renderer.JiraRenderer`
- `markcraft.extensions.xwiki20_renderer.XWiki20Renderer`
- `markcraft.extensions.scheme.SchemeRenderer`
- `markcraft.renderers.extensions.GithubWikiRenderer`
- `markcraft.renderers.extensions.JiraRenderer`
- `markcraft.renderers.extensions.MathJaxRenderer`
- `markcraft.renderers.extensions.PygmentsRenderer`
- `markcraft.renderers.extensions.SchemeRenderer`
- `markcraft.renderers.extensions.TocRenderer`
- `markcraft.renderers.extensions.XWiki20Renderer`

## Documentation Map

- `README.md`: project overview, install, and usage.
- `DEVELOPMENT.md`: architecture, token model, renderer model, and extension points.
- `BENCHMARKING.md`: benchmark method, reproducibility, and optimization guidance.

## Development

Common commands:

```sh
uv sync
uv run pytest
uv run python tests/benchmark.py
uv build
```

For benchmark dependencies (`markdown`, `mistune`, `commonmark`), run:

```sh
uv sync --group benchmark
```

## Contributing

Open an issue with context and a minimal reproduction before large changes.
For code contributions, keep commits focused and include tests in `tests/`.

## Versioning and License

- Current version is defined in `src/markcraft/__init__.py`.
- Released under the MIT License. See `LICENSE`.

## Project Links

- Repository: https://github.com/niu2x/markcraft
- Issues: https://github.com/niu2x/markcraft/issues
- Actions: https://github.com/niu2x/markcraft/actions
