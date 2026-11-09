---
name: pdfnote
description: Turn a PDF (lecture slides, textbook chapters, papers) into a PDFNote study page - a single HTML file with each PDF page on the left and an explanation note for that page on the right - and keep editing it later. Use when the user shares a PDF and asks for notes, page-by-page explanations, a study guide, "make notes", "explain each page", "노트 만들어", "해설 달아줘", or mentions PDFNote.
---

# PDFNote

One self-contained HTML file shows every PDF page next to a markdown note for that page. The scripts in `scripts/` build the file and write notes into it. You only write the note text: never write generator scripts, JSON files, or HTML yourself.

`S` below means this skill's `scripts` directory.

## Where files live

- **Input PDF**: a file the user attached or a path the user gave. In claude.ai chat, attachments are under `/mnt/user-data/uploads/`.
- **Output HTML**: in claude.ai chat, write to `/mnt/user-data/outputs/`. Elsewhere (Claude Code, Cowork), write next to the input PDF unless the user names another folder.
- Name the output after the title, for example `Operating Systems Ch3.html`.

`OUT` below means the output HTML path chosen by these rules.

## Requirements

`build.py` needs either PyMuPDF (`fitz`) or poppler-utils (`pdftoppm`, `pdftotext`). If it exits with a message that neither is available, tell the user to install one and stop:

```bash
pip install pymupdf            # or
sudo apt install poppler-utils # or: brew install poppler
```

## Create a note file

1. Build the HTML from the PDF. This renders all pages with empty notes and prints the page count:

   ```bash
   python3 S/build.py "input.pdf" "OUT" "Title"
   ```

2. Read the PDF content. Use the PDF attached to the conversation when you can see it. If a page is not visible to you, extract its text with `pdftotext -f N -l N input.pdf -`.
3. Write notes about 10 pages per command. Run these commands one after another, never in parallel: each `set` rewrites the whole file. Each page starts with a line `@@page N`, followed by the note in plain markdown. The quoted heredoc needs no escaping:

   ```bash
   python3 S/note.py "OUT" set <<'EOF'
   @@page 1
   # What a process is
   A **process** is a program in execution. $T = t_{save} + t_{load}$
   @@page 2
   # Context switch
   ...
   EOF
   ```

4. Run `python3 S/note.py "OUT" status` and fill any pages listed under `missing notes`.
5. Send the HTML file to the user. Reply with one or two sentences only; do not repeat the notes in the chat.

## Follow-up requests

Change a note only when the user explicitly asks for a change. Otherwise answer in the chat and leave the file untouched. Classify each follow-up request into one of three cases:

| Case | Signals | Action | Chat reply |
|---|---|---|---|
| Chat answer (default) | A question with no edit verb ("what is", "why", "how", "what's the difference", "I don't get it"; "뭐야", "왜", "어떻게", "차이가 뭐야", "이해가 안 돼"), even when it names a page; a question that names no page; a question spanning several pages; a question about the note file itself (progress, missing pages) | Do not run `set`. Do not send the HTML | A full answer in the chat |
| Note edit | An edit verb ("add", "put in", "update", "fix", "change", "rewrite", "remove"; "추가해", "넣어", "반영해", "고쳐", "바꿔", "다시 써", "빼", "정리해서 넣어"); the user points out an error in a note ("page 12 is wrong", "12페이지 이거 틀렸어"); the user pastes content with a page number and no question | Revise the note (steps below) and send the updated HTML | One sentence naming the revised page and what changed |
| Both | A question plus an edit verb ("explain it and add it to the note", "설명해주고 노트에도 넣어") | Answer in the chat, then revise the note | The full answer, then one sentence naming the revised page |

Examples:

```
"Why does a context switch on page 12 cost time?"  -> chat answer, file unchanged
"12페이지 문맥 교환 왜 오버헤드 생겨?"             -> chat answer, file unchanged
"TLB랑 page table 차이 뭐야?"                      -> chat answer, file unchanged
"Add the overhead causes to page 12"               -> note edit on page 12
"12페이지에 오버헤드 원인 추가해"                  -> note edit on page 12
"@12 lecturer said: registers are saved, then ..." -> note edit on page 12 (pasted content)
"18p 설명해주고 노트에도 넣어"                     -> chat answer + note edit on page 18
```

When a request is still unclear after this table, answer in the chat; do not edit.

### Revising a note

1. Read the current note with `python3 S/note.py "OUT" show N`.
2. Rewrite the note so it reflects the requested change or the pasted content: correct, expand, or reorganize the existing text where it belongs. Do not tack it on at the end as a separate section.
3. Replace the note with `set`, then send the updated HTML file to the user:

   ```bash
   python3 S/note.py "OUT" set <<'EOF'
   @@page 12
   (full revised note)
   EOF
   ```

### Chat answers

- Write in the user's language. Follow the math and range notation of the Explanation rules (`$...$`, "-" for ranges).
- Mentioning page numbers is allowed in the chat.
- Do not search the web to add examples or code that are not in the material, unless the user asks for outside material.

### File handling

- The file to edit is the HTML created earlier in the conversation. If it is gone, ask the user to share the HTML, copy it to the output location, and edit the copy.
- `python3 S/note.py "OUT" title New title` changes the title. Changing the title counts as a note edit and needs an explicit request.

## Explanation rules

Write in the user's language: the language the user writes requests in, unless they ask for another. Explain the content of each page so that someone meeting the topic for the first time can understand it.

Focus on:
- Key concepts, terms, and formulas
- What important terms and formulas mean and how they are used
- What tables and graphs show

Exclude:
- Any mention that this is "a page", "a slide", or "this document"
- Page numbers, position, or other meta information
- For pages without substantive content (cover, table of contents, overview), write only one or two lines about what the material covers
- Do not search the web to add examples or code that are not in the material

Format:
- Start every note with a "# " title; use no other heading level except "### "
- After the title, write a short introductory paragraph
- Use "### " only when a subheading is needed
- Use "- " bullets only for lists of items
- Use a markdown table only for tabular data
- Bold only key terms with ** ** and do not overuse it
- Write math as LaTeX in `$...$` (inline) or `$$...$$` (display)
- Write ranges with "-", never "~" (for example, 1-10)
- Do not put a divider (---) at the start or end of a note
