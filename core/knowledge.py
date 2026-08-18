"""
==============================================================================
 SysClaw Knowledge Base Ingestion Engine (Zero-DB)
 https://github.com/dnurvianto/sysclaw
==============================================================================
Automatically ingests markdown documentation from the docs/ directory
and dynamically injects domain knowledge into the AI system context.
"""

import os
from pathlib import Path
import config

# Maximum characters allowed for injected knowledge to prevent token overflow
MAX_KNOWLEDGE_CHARS = 50000

def load_knowledge_base(docs_dir: Path = None) -> str:
    """
    Scans and reads all .md documentation files in the docs/ directory.
    Returns aggregated markdown text ready for LLM prompt injection.
    """
    if docs_dir is None:
        docs_dir = config.BASE_DIR / "docs"

    if not docs_dir.is_dir():
        return ""

    documents = []
    total_chars = 0

    try:
        docs_real_path = docs_dir.resolve()
        # Sort files deterministically (e.g. 01_arch.md, 02_network.md)
        for entry in sorted(os.listdir(docs_dir)):
            if entry.endswith(".md") and not entry.startswith((".", "_")) and not entry.endswith(".example.md"):
                file_path = (docs_dir / entry).resolve()
                # Security Check: Prevent symlink traversal out of docs/ directory
                try:
                    file_path.relative_to(docs_real_path)
                except ValueError:
                    # Symlink points outside docs directory, skip for safety
                    continue

                if file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read().strip()
                            if content:
                                doc_block = f"=== DOCUMENT: {entry} ===\n{content}\n"
                                if total_chars + len(doc_block) > MAX_KNOWLEDGE_CHARS:
                                    remaining = MAX_KNOWLEDGE_CHARS - total_chars
                                    if remaining > 100:
                                        documents.append(doc_block[:remaining] + "\n... [Truncated due to context limit]")
                                    break
                                documents.append(doc_block)
                                total_chars += len(doc_block)
                    except Exception:
                        continue
    except Exception:
        pass

    return "\n\n".join(documents)
