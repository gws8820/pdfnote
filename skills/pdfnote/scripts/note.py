import json
import re
import sys
from pathlib import Path

DATA_START = '<script id="pdfnote-data" type="application/json">'
DATA_END = "</script>"
USAGE = """usage:
  note.py <file.html> set      < notes     replace notes of the pages in stdin
  note.py <file.html> show <page>          print the current note of a page
  note.py <file.html> status               print title and pages without notes
  note.py <file.html> title <new title>    change the title

stdin format: one or more blocks, each starting with a line "@@page N"."""


def data_span(html):
    start = html.index(DATA_START) + len(DATA_START)
    return start, html.index(DATA_END, start)


def parse_blocks(text):
    parts = re.split(r"^@@page\s+(\d+)\s*$", text, flags=re.M)
    if parts[0].strip():
        sys.exit('stdin must start with a line "@@page N"')
    return [(int(parts[i]), parts[i + 1].strip("\n")) for i in range(1, len(parts), 2)]


def main():
    if len(sys.argv) < 3:
        sys.exit(USAGE)
    path, cmd, args = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
    html = path.read_text(encoding="utf-8")
    start, end = data_span(html)
    data = json.loads(html[start:end])
    pages = data["pages"]

    if cmd == "set":
        blocks = parse_blocks(sys.stdin.read())
        for num, note in blocks:
            if not 1 <= num <= len(pages):
                sys.exit(f"page {num} is out of range 1-{len(pages)}")
            pages[num - 1]["note"] = note
        print(f"set: pages {', '.join(str(n) for n, _ in blocks)}")
    elif cmd == "title":
        data["title"] = " ".join(args)
        print(f"title: {data['title']}")
    elif cmd == "show":
        print(pages[int(args[0]) - 1]["note"])
        return
    elif cmd == "status":
        missing = [str(i) for i, p in enumerate(pages, start=1) if not p["note"].strip()]
        print(f"title: {data['title']}\npages: {len(pages)}\nmissing notes: {', '.join(missing) or 'none'}")
        return
    else:
        sys.exit(USAGE)

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    path.write_text(html[:start] + payload + html[end:], encoding="utf-8")


if __name__ == "__main__":
    main()
