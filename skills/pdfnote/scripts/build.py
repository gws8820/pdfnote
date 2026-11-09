import base64
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
SCALE = 2
JPEG_QUALITY = 85
XHTML = "{http://www.w3.org/1999/xhtml}"

try:
    import fitz
except ImportError:
    fitz = None


def to_data_url(jpeg_bytes):
    return "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes).decode("ascii")


def text_line(x0, y0, x1, y1, text, baseline):
    return [round(x0, 1), round(y0, 1), round(x1 - x0, 1), round(y1 - y0, 1), text, round(baseline - y0, 1)]


def fitz_page_text(page):
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            dx, dy = line["dir"]
            text = "".join(span["text"] for span in line["spans"])
            if dx <= 0 or abs(dy) > 0.01 or not text.strip():
                continue
            lines.append(text_line(*line["bbox"], text, line["spans"][0]["origin"][1]))
    return {"w": round(page.rect.width, 1), "h": round(page.rect.height, 1), "lines": lines}


def load_with_fitz(pdf_path):
    with fitz.open(pdf_path) as doc:
        return [
            (to_data_url(page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE)).tobytes("jpeg", jpg_quality=JPEG_QUALITY)), fitz_page_text(page))
            for page in doc
        ]


def load_with_poppler(pdf_path):
    if not shutil.which("pdftoppm") or not shutil.which("pdftotext"):
        sys.exit("PyMuPDF (fitz) or poppler-utils (pdftoppm, pdftotext) is required")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["pdftoppm", "-jpeg", "-jpegopt", f"quality={JPEG_QUALITY}", "-r", str(int(72 * SCALE)), str(pdf_path), f"{tmp}/p"],
            check=True,
        )
        files = sorted(Path(tmp).glob("p-*.jpg"), key=lambda p: int(p.stem.split("-")[-1]))
        images = [to_data_url(f.read_bytes()) for f in files]
    out = subprocess.run(["pdftotext", "-bbox-layout", str(pdf_path), "-"], check=True, capture_output=True, text=True).stdout
    texts = []
    for page in ET.fromstring(out).iter(XHTML + "page"):
        lines = []
        for line in page.iter(XHTML + "line"):
            text = " ".join(word.text or "" for word in line.iter(XHTML + "word"))
            if not text.strip():
                continue
            x0, y0, x1, y1 = (float(line.get(k)) for k in ("xMin", "yMin", "xMax", "yMax"))
            lines.append(text_line(x0, y0, x1, y1, text, y0 + (y1 - y0) * 0.8))
        texts.append({"w": float(page.get("width")), "h": float(page.get("height")), "lines": lines})
    return list(zip(images, texts))


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: build.py <input.pdf> <output.html> [title]")
    pdf_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) == 4 else pdf_path.stem

    pages = load_with_fitz(pdf_path) if fitz else load_with_poppler(pdf_path)
    data = {"title": title, "pages": [{"image": image, "note": "", "text": text} for image, text in pages]}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__PDFNOTE_DATA__", payload), encoding="utf-8")
    print(f"pages: {len(pages)}, size: {out_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
