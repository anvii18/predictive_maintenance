import os
from pathlib import Path

import pathway as pw

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("FAILUREGUARD_DATA_DIR", str(BASE_DIR / "data")))
DOCUMENTS_DIR = Path(os.getenv("FAILUREGUARD_DOCUMENTS_DIR", str(BASE_DIR / "documents")))
OUTPUT_FILE = DATA_DIR / "documents_index.jsonl"


class DocSchema(pw.Schema):
    data: bytes
    path: str


def run():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DOCUMENTS_DIR.is_dir():
        raise FileNotFoundError(f"Documents directory not found: {DOCUMENTS_DIR}")

    print(f"Pathway document watcher watching {DOCUMENTS_DIR}", flush=True)
    documents = pw.io.fs.read(
        str(DOCUMENTS_DIR),
        format="binary",
        mode="streaming",
        with_metadata=True,
    )
    processed = documents.select(
        path=pw.this._metadata["path"],
        content=pw.apply(
            lambda data: data.decode("utf-8", errors="ignore"),
            pw.this.data,
        ),
    )
    pw.io.jsonlines.write(processed, str(OUTPUT_FILE))
    print("Pathway document watcher running.", flush=True)
    pw.run()


if __name__ == "__main__":
    run()
