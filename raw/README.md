# Raw Archive

This is the substrate. Every claim in [the PURSUE master report](../pursue-release-01/README.md) and the [FBI master report](../fbi-62hq83894/README.md) ultimately resolves to a file in here.

---

## What's here

### `fbi-62hq83894-ocr/`

OCR'd Markdown transcripts of FBI 62-HQ-83894, the FBI flying-discs case file (1944–1973), as released in PURSUE Release 01 on May 8, 2026.

```text
fbi-62hq83894-ocr/
├── 001-65_HS1-834228961_62-HQ-83894_Section_10/   # post-Blue Book, civilian correspondence
├── 002-65_HS1-834228961_62-HQ-83894_Section_2/    # 1947 origin year
├── 003-65_HS1-834228961_62-HQ-83894_Section_3/
├── 004-65_HS1-834228961_62-HQ-83894_Section_4/
├── 005-65_HS1-834228961_62-HQ-83894_Section_5/    # the dense 1949–1950 disinformation cluster
├── 006-65_HS1-834228961_62-HQ-83894_Section_6/
└── manifest.jsonl                                  # one line per page conversion
```

Page files use zero-padded numbers (`page-0001.md`, `page-0002.md`, ...) so lexical order matches page order. Each page has YAML frontmatter:

```yaml
---
source_title: "..."
source_file: "..."
source_url: "..."
asset_type: "pdf"
dataset_row: 1
page: 1
page_count: 184
model: "gemini-3.1-flash-lite"
generated_at: "..."
---
```

`manifest.jsonl` records one JSON line per page conversion, including the source file, page number, output path, character count, status, and any error.

These transcripts were generated using gemini-3.1-flash-lite OCR. They are not perfect, some pages are heavily redacted or photo-degraded and return `[illegible]` tokens. Where a case writeup quotes the file, it quotes the OCR'd text; where the OCR is suspect, the writeup notes that.

### `pursue-metadata/`

The release inventory:

- `uap-csv.csv`, the full 162-row PURSUE Release 01 catalog (120 PDFs, 28 videos, 14 images).
- `pdf_manifest.tsv`, the corrected 120-PDF manifest used for the OCR pipeline.

---

## What's *not* here

The original PDFs and videos themselves are not in this repo. They are too large (2.3 GiB total across 162 files) and they are publicly hosted by the US Government:

- **Primary:** [war.gov/UFO/](https://www.war.gov/UFO/)
- **Mirror:** [github.com/DenisSergeevitch/UFO-USA](https://github.com/DenisSergeevitch/UFO-USA)

If you want the raw PDFs, pull from there. The metadata in `pursue-metadata/uap-csv.csv` includes file URLs.

---

## Provenance

The OCR conversion pipeline lives at [github.com/DenisSergeevitch/UFO-USA](https://github.com/DenisSergeevitch/UFO-USA). This repo's `fbi-62hq83894-ocr/` tree is a snapshot of the converted FBI sections taken on 2026-05-10.

The `pursue-metadata/` files are a snapshot of the 162-row catalog at the same date.

If new sections are converted upstream, this repo will track them.

---

## License

US Government records (FBI files, AARO documents, war.gov-hosted material) are public domain in the United States. The OCR'd text is a derived work of those documents and inherits their public-domain status.
