"""Load the synthetic corpus with provenance metadata.

Every document carries its filename, type, and section spans, so every
chunk — and therefore every search result — can cite exactly where it
came from. Provenance is a load-time property, not something bolted
onto results later.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


@dataclass
class Section:
    name: str
    start: int
    end: int


@dataclass
class Doc:
    file: str          # e.g. "copybooks/CUSTREC.cpy"
    type: str          # copybook | runbook | incident
    text: str
    sections: list[Section] = field(default_factory=list)

    def section_at(self, offset: int) -> str:
        for s in self.sections:
            if s.start <= offset < s.end:
                return s.name
        return self.sections[-1].name if self.sections else ""


def _sections_md(text: str) -> list[Section]:
    heads = [(m.start(), m.group(1).strip())
             for m in re.finditer(r"^##\s+(.+)$", text, re.M)]
    if not heads:
        return [Section("(whole document)", 0, len(text))]
    out: list[Section] = []
    if heads[0][0] > 0:
        out.append(Section("(title)", 0, heads[0][0]))
    for i, (start, name) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        out.append(Section(name, start, end))
    return out


def _sections_cpy(text: str) -> list[Section]:
    recs = [(m.start(), m.group(1).strip())
            for m in re.finditer(r"^\s+01\s+([A-Z0-9-]+)", text, re.M)]
    if not recs:
        return [Section("(whole copybook)", 0, len(text))]
    out: list[Section] = []
    if recs[0][0] > 0:
        out.append(Section("(header)", 0, recs[0][0]))
    for i, (start, name) in enumerate(recs):
        end = recs[i + 1][0] if i + 1 < len(recs) else len(text)
        out.append(Section(name, start, end))
    return out


_TYPE_BY_DIR = {"copybooks": "copybook", "runbooks": "runbook", "incidents": "incident"}


def load_corpus(root: Path = CORPUS_DIR) -> list[Doc]:
    docs: list[Doc] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".cpy"}:
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        dtype = _TYPE_BY_DIR.get(rel.split("/")[0], "doc")
        sections = _sections_cpy(text) if path.suffix == ".cpy" else _sections_md(text)
        docs.append(Doc(file=rel, type=dtype, text=text, sections=sections))
    return docs
