"""Keep source headings attached to every paragraph; never discard short sections."""
import hashlib
import re

from crestline.config import ROOT


def load_chunks():
    chunks = []
    for domain in ("hr", "marketing", "product"):
        for path in sorted((ROOT / "docs" / domain).glob("*.txt")):
            text = path.read_text()
            title = text.splitlines()[0]
            section = title
            for paragraph in re.split(r"\n\s*\n", text):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                first = paragraph.splitlines()[0]
                if re.match(r"^\d+\.", first) or first.isupper():
                    section = first
                # Preserve all text, including headings, and split long sections with overlap.
                for offset in range(0, len(paragraph), 1100):
                    body = paragraph[max(0, offset - 120):offset + 1100]
                    source = f"docs/{domain}/{path.name}"
                    chunk_id = hashlib.sha256(f"{source}:{section}:{offset}:{body}".encode()).hexdigest()[:20]
                    chunks.append({"id": chunk_id, "domain": domain, "source": source,
                                   "section": section, "content": f"{title}\n{body}"})
    return chunks
