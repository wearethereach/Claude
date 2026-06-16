# AI Search 2026 Guide — generator

Swiss-minimalist bilingual PDF guide (SEO / GEO / AEO with AI in 2026).

## Rebuild
Requires Python 3, `reportlab`, the Inter font (extras/ttf) and JetBrains Mono.
Fonts are expected under `/tmp/fonts/...` (see paths at top of `build_guide.py`).

```
pip install reportlab
python3 build_guide.py   # writes AI-Search-2026-Guide-{EN,RU}.pdf
```

- `build_guide.py` — layout engine (yellow #FFF55F, black Inter, green #00A85A accent, mono corner captions).
- `content_en.py` / `content_ru.py` — editable content (no emoji; emphasis is done via type + green accent).

Data sourced via web research (Jun 2026): Exposure Ninja, Position Digital,
Digital Applied, Backlinko, Frase, AuthorityTech, Omnibound, Nick Lafferty.
