# markcraft

Your next Markdown parser in Python:
**pure Python, CommonMark-oriented, and easy to extend.**

## Why You Will Like It

- **Pure Python, no C extension burden**: simpler deployment across environments.
- **CommonMark-oriented behavior**: predictable parsing with stable token precedence.
- **Extensible architecture**: add custom block/span tokens and custom renderers.
- **More than HTML output**: ships with HTML, LaTeX, AST, and Markdown renderers.
- **Built for maintainability**: parser and renderer responsibilities stay cleanly separated.

## Installation

Install from PyPI:

```sh
pip install markcraft
```

Local development setup (`uv` + Python 3.13):

```sh
git clone https://github.com/niu2x/markcraft.git
cd markcraft
uv sync
```

## 30-Second Quick Start

### 1) Render to HTML by default

```python
import markcraft

with open("example.md", "r", encoding="utf-8") as fin:
    html = markcraft.render(fin)
```

### 2) Use a specific renderer (for example, LaTeX)

```python
import markcraft
from markcraft.renderers import LaTeXRenderer

with open("example.md", "r", encoding="utf-8") as fin:
    latex = markcraft.render(fin, LaTeXRenderer)
```

### 3) Parse explicitly when you need a Document tree

```python
import markcraft
from markcraft.renderers import MarkdownRenderer

doc = markcraft.parse("a\n\n[b]: /uri\n")

with MarkdownRenderer() as renderer:
    renderer_specific_doc = markcraft.parse("a\n\n[b]: /uri\n", renderer)
    markdown = renderer.render(renderer_specific_doc)
```

Why call `markcraft.parse(...)` twice here?

- `doc = markcraft.parse(...)` uses the default parser path and returns a generic `Document` tree.
- `markcraft.parse(..., renderer)` parses with renderer context, so renderer-specific token rules are included when needed.
- Use the first form for renderer-agnostic analysis; use the second form when your renderer adds or depends on extra syntax.

## Outputs and Extensions

### Core renderers

- `markcraft.renderers.HtmlRenderer`
- `markcraft.renderers.LaTeXRenderer`
- `markcraft.renderers.AstRenderer`
- `markcraft.renderers.MarkdownRenderer`

### Extension renderers

Import directly from extension modules:

- `markcraft.extensions.mathjax.MathJaxRenderer`
- `markcraft.extensions.pygments_renderer.PygmentsRenderer`
- `markcraft.extensions.toc_renderer.TocRenderer`
- `markcraft.extensions.github_wiki.GithubWikiRenderer`
- `markcraft.extensions.jira_renderer.JiraRenderer`
- `markcraft.extensions.xwiki20_renderer.XWiki20Renderer`
- `markcraft.extensions.scheme.SchemeRenderer`

Or import from the aggregated namespace:

- `markcraft.renderers.extensions.GithubWikiRenderer`
- `markcraft.renderers.extensions.JiraRenderer`
- `markcraft.renderers.extensions.MathJaxRenderer`
- `markcraft.renderers.extensions.PygmentsRenderer`
- `markcraft.renderers.extensions.SchemeRenderer`
- `markcraft.renderers.extensions.TocRenderer`
- `markcraft.renderers.extensions.XWiki20Renderer`

## For Contributors

Use `uv` and Python 3.13 for local development.

```sh
uv sync
uv run pytest
```

For benchmarks:

```sh
uv sync --group benchmark
uv run python tests/benchmark.py
```

More implementation details: `DEVELOPMENT.md` and `BENCHMARKING.md`.

## Contributing

Issues, discussions, and pull requests are welcome.

- For larger changes, open an issue first with context and a minimal reproduction.
- Keep code contributions focused and add tests under `tests/`.

## Versioning and License

- Licensed under MIT. See `LICENSE`.

## Project Links

- Repository: https://github.com/niu2x/markcraft
- Issues: https://github.com/niu2x/markcraft/issues
- Actions: https://github.com/niu2x/markcraft/actions
- PyPI: https://pypi.org/project/markcraft/
