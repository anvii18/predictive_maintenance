import pathway as pw
import json
import os

print("✅ Pathway Document Watcher Starting...")
print("👀 Watching documents/ folder for live changes...")

class DocSchema(pw.Schema):
    data: bytes
    path: str

def run():
    os.makedirs("data", exist_ok=True)

    # Pathway watches documents folder in streaming mode
    # When any file changes, Pathway reacts automatically
    documents = pw.io.fs.read(
        "documents/",
        format="binary",
        mode="streaming",
        with_metadata=True
    )

    # Extract text and filename from each document
    processed = documents.select(
        path=pw.this._metadata["path"],
        content=pw.apply(
            lambda data: data.decode("utf-8", errors="ignore"),
            pw.this.data
        )
    )

    # Write to JSONL so backend can read it
    pw.io.jsonlines.write(
        processed,
        "data/documents_index.jsonl"
    )

    print("🚀 Document watcher running!")
    print("📝 Any changes to documents/ will be detected instantly")
    pw.run()

if __name__ == "__main__":
    run()