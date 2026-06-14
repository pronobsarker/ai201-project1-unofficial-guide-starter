import os
import re

def load_and_chunk_documents(data_folder="data"):
    """
    Loads all .txt files from the data folder, splits them by
    section label, prepends the dorm name to every chunk, and
    returns a list of chunk dictionaries.
    """
    chunks = []

    for filename in os.listdir(data_folder):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(data_folder, filename)

        with open(filepath, "r") as f:
            content = f.read()

        # Extract dorm name from the first line (DORM: Name)
        dorm_name = "Unknown Dorm"
        dorm_match = re.search(r'DORM:\s*(.+)', content)
        if dorm_match:
            dorm_name = dorm_match.group(1).strip()

        # Extract source
        source = filename
        source_match = re.search(r'SOURCE:\s*(.+)', content)
        if source_match:
            source = source_match.group(1).strip()

        # Split into sections by label
        section_pattern = r'(REVIEW \d+:|PROS:|CONS:|BEST FOR:)'
        parts = re.split(section_pattern, content)

        # Pair each label with its content
        i = 1
        while i < len(parts) - 1:
            label = parts[i].strip()
            text = parts[i + 1].strip()

            if text:
                # Prepend dorm name so every chunk knows its source
                chunk_text = f"{dorm_name} — {label} {text}"

                chunks.append({
                    "text": chunk_text,
                    "source": filename,
                    "dorm_name": dorm_name
                })
            i += 2

    return chunks


if __name__ == "__main__":
    chunks = load_and_chunk_documents()

    print(f"Total chunks created: {len(chunks)}\n")
    print("=" * 60)
    print("5 SAMPLE CHUNKS:")
    print("=" * 60)

    # Print 5 evenly spaced sample chunks
    step = len(chunks) // 5
    for i in range(0, min(5, len(chunks))):
        chunk = chunks[i * step]
        print(f"\nChunk #{i * step + 1}")
        print(f"Dorm:   {chunk['dorm_name']}")
        print(f"Source: {chunk['source']}")
        print(f"Text:   {chunk['text'][:300]}")
        print("-" * 60)