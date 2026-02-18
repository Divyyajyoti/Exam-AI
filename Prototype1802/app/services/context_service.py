def fetch_context(text_blob: str, query: str = "") -> str:
    """
    Demo-stable: just returns the blob.
    (Later you can add vector search; for investor demo stability matters.)
    """
    return (text_blob or "").strip()
