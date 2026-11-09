# PDFNote

PDFNote turns a PDF such as lecture slides, a textbook chapter, or a paper into one self-contained HTML study page. Every PDF page is shown on the left, and an explanation note for that page is shown on the right. Claude writes the notes for a first-time reader of the topic, covering key concepts, terms, formulas, tables, and graphs, and you can keep refining them in the same conversation.

## What it does

- Renders every page of your PDF as an image and embeds it in a single HTML file
- Writes a markdown note per page, with math rendered as LaTeX
- Answers your questions about the material in the chat without touching the notes
- Edits a page's note only when you explicitly ask for a change

## Install

```
/plugin install pdfnote --marketplace gws8820/pdfnote
```

## Usage

Attach or point to a PDF and ask for notes:

```
Make study notes for this PDF
이 PDF로 노트 만들어줘
```

Ask questions, which are answered in the chat and leave the file unchanged:

```
Why does a context switch on page 12 cost time?
TLB랑 page table 차이 뭐야?
```

Ask for an edit, which updates that page's note and gives you the new HTML:

```
Add the overhead causes to page 12
12페이지 이거 틀렸어, 레지스터만 저장하는 게 아니야
18p 설명해주고 노트에도 넣어
```

## Requirements

The build script needs Python 3 and one of these:

```bash
pip install pymupdf             # PyMuPDF
sudo apt install poppler-utils  # or: brew install poppler
```

claude.ai chat already provides these.

## Data and network

- Your PDF is processed locally by the bundled Python scripts. The plugin itself does not upload the PDF or the notes anywhere.
- The generated HTML file, when opened in a browser, loads these public libraries from cdnjs.cloudflare.com: KaTeX 0.16.9 (math rendering), marked 16.3.0 (markdown rendering), and the Pretendard 1.3.9 font. No other network requests are made.

## Files

- `skills/pdfnote/SKILL.md`: instructions Claude follows
- `skills/pdfnote/scripts/build.py`: renders the PDF into the HTML file with empty notes
- `skills/pdfnote/scripts/note.py`: reads and writes per-page notes in the HTML file (`set`, `show`, `status`, `title`)
- `skills/pdfnote/assets/template.html`: the page viewer template

## License

MIT
