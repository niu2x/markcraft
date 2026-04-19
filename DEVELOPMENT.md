# Developer Guide

This guide explains how markcraft parses Markdown and where to extend it.

## Local Environment

This project uses `uv` for environment and dependency management.

```sh
uv sync
```

The repository targets Python 3.13 (see `.python-version`).

## Architecture Overview

The parse/render pipeline is:

1. Read Markdown input.
2. Build a `Document` tree of block and span tokens.
3. Render the tree with a renderer class.

The convenience API is:

```python
markcraft.render(iterable, renderer=HtmlRenderer)
```

It creates a renderer context, parses into `Document`, then renders.

For clearer module boundaries, the project now also exposes:

- `markcraft.parser`: parser-oriented imports and helper functions.
- `markcraft.renderers`: renderer-oriented imports (core + extensions).
- `markcraft.tokens`: token-oriented imports (base/core/span/latex/block).

## Token Model

### Block tokens

Block tokens represent structural regions, for example:

- `Document`
- `Paragraph`
- `Heading`
- `List`
- `Quote`

### Span tokens

Span tokens represent inline content, for example:

- `RawText`
- `Emphasis`
- `Strong`
- `Link`
- `InlineCode`

Span tokens can only contain span tokens.
Block tokens may contain block tokens and/or span tokens depending on type.

## Renderer Model

Renderers traverse the token tree and emit output for a target format.
Core renderers include HTML, LaTeX, AST, and Markdown.

Each renderer typically implements methods named like `render_heading`,
`render_paragraph`, etc., plus defaults inherited from base classes.

## Writing a Custom Renderer

1. Subclass an existing renderer (often `HtmlRenderer` or `BaseRenderer`).
2. Override token-specific `render_*` methods.
3. Pass your renderer class to `markcraft.render(...)`.

## Adding Custom Tokens

Typical flow:

1. Define token class and parsing rules.
2. Ensure precedence and matching behavior are correct.
3. Add rendering behavior in your renderer.
4. Add tests that isolate edge cases.

When changing token precedence, always verify interactions with emphasis,
links, code spans, and escaping rules.

## Testing and Validation

Run:

```sh
uv run pytest
```

For parser behavior changes, add minimal tests in `tests/` and include both
positive and edge-case coverage.

## Source Map

- `src/markcraft/parser/`: parser namespace facade for tokens/tokenizers/document parsing.
- `src/markcraft/parser/state.py`: parser stream/buffer utility classes.
- `src/markcraft/renderers/`: renderer namespace facade for core and extension renderers.
- `src/markcraft/markdown_primitives.py`: markdown-rendering helper tokens/fragments.
- `src/markcraft/tokens/`: unified token namespace.
- `src/markcraft/tokens/base.py`: shared token base class.
- `src/markcraft/tokens/core.py`: delimiter/link matching and core parse helpers.
- `src/markcraft/tokens/span.py`: span token definitions and span registry.
- `src/markcraft/tokens/latex.py`: LaTeX-only span token extensions.
- `src/markcraft/tokens/block/`: block token definitions and block registry.
- `src/markcraft/tokens/block/base.py`: shared block-token base class.
- `src/markcraft/tokens/block/document.py`: document root token.
- `src/markcraft/tokens/block/headings.py`: heading token implementations.
- `src/markcraft/tokens/block/quote_paragraph.py`: quote and paragraph parsing.
- `src/markcraft/tokens/block/code_blocks.py`: indented/fenced code block parsing.
- `src/markcraft/tokens/block/lists.py`: list and list-item parsing.
- `src/markcraft/tokens/block/tables.py`: table token implementations.
- `src/markcraft/tokens/block/extras.py`: footnotes, thematic break, HTML blocks.
- `src/markcraft/parser/block_tokenizer.py`: block tokenization pipeline.
- `src/markcraft/parser/span_tokenizer.py`: span tokenization pipeline.
- `src/markcraft/renderers/base.py`: renderer base behavior.
