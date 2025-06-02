import re

def chunk_diff(patch):
    """
    Extracts both added and removed lines from a unified diff patch.
    Returns two lists: added_chunks and removed_chunks
    """
    added_chunks = []
    removed_chunks = []

    if not patch:
        return added_chunks, removed_chunks

    lines = patch.split('\n')
    added_chunk = []
    removed_chunk = []
    added_lines = []
    removed_lines = []

    old_line = new_line = 0

    for line in lines:
        # Start of a diff hunk
        if line.startswith('@@'):
            if added_chunk:
                added_chunks.append({
                    "lines": added_lines,
                    "code": "\n".join(added_chunk)
                })
                added_chunk = []
                added_lines = []

            if removed_chunk:
                removed_chunks.append({
                    "lines": removed_lines,
                    "code": "\n".join(removed_chunk)
                })
                removed_chunk = []
                removed_lines = []

            match = re.match(r"@@ -(\d+),?\d* \+(\d+),?\d* @@", line)
            if match:
                old_line = int(match.group(1))
                new_line = int(match.group(2))
        elif line.startswith('+') and not line.startswith('+++'):
            added_chunk.append(line[1:])
            added_lines.append(new_line)
            new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed_chunk.append(line[1:])
            removed_lines.append(old_line)
            old_line += 1
        else:
            # Context line
            if added_chunk:
                added_chunks.append({
                    "lines": added_lines,
                    "code": "\n".join(added_chunk)
                })
                added_chunk = []
                added_lines = []
            if removed_chunk:
                removed_chunks.append({
                    "lines": removed_lines,
                    "code": "\n".join(removed_chunk)
                })
                removed_chunk = []
                removed_lines = []
            old_line += 1
            new_line += 1

    # Final pending chunks
    if added_chunk:
        added_chunks.append({
            "lines": added_lines,
            "code": "\n".join(added_chunk)
        })
    if removed_chunk:
        removed_chunks.append({
            "lines": removed_lines,
            "code": "\n".join(removed_chunk)
        })

    return added_chunks, removed_chunks
