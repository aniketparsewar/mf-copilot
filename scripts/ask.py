"""Ask the copilot one question (or loop interactively with no argument).

    python scripts/ask.py "What does file status 39 mean?"
    python scripts/ask.py --debug "Why did the batch fail in March?"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.chunking import chunk_corpus
from src.copilot import CHUNKING, answer
from src.corpus import load_corpus
from src.index import Index


def main() -> None:
    debug = "--debug" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--debug"]
    docs = load_corpus()
    index = Index(chunk_corpus(docs, CHUNKING))

    def ask(q: str) -> None:
        out = answer(index, q)
        print(f"\n{out['answer']}")
        if out["invalid_citations"]:
            print(f"  !! invalid citations: {out['invalid_citations']}")
        if debug:
            print(f"  [gate] top_cos={out['top_cos']} refused={out['refused']}")
            for r in out["retrieved"]:
                print(f"  [retrieved] {r['file']} :: {r['section']} "
                      f":: score {r['score']}")

    if args:
        ask(" ".join(args))
    else:
        print("Copilot ready. Ctrl-C to exit.")
        while True:
            try:
                ask(input("\n> "))
            except (EOFError, KeyboardInterrupt):
                break


if __name__ == "__main__":
    main()
