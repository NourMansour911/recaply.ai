def has_speakers(segments):
    return any(seg.speakers for seg in segments)


def split_with_overlap(words, chunk_size, overlap):
    chunks = []

    i = 0
    while i < len(words):
        end = min(i + chunk_size, len(words))
        chunks.append(words[i:end])

        if end >= len(words):
            break

        i = end - overlap

    return chunks


def map_word_indices_to_timing(chunks, word_map):
    results = []
    cursor = 0

    for chunk in chunks:
        start_times = []
        end_times = []

        for i in range(len(chunk)):
            idx = cursor + i
            if idx >= len(word_map):
                break

            t = word_map[idx]

            if t["start"] is not None:
                start_times.append(t["start"])
            if t["end"] is not None:
                end_times.append(t["end"])

        results.append({
            "start": min(start_times) if start_times else None,
            "end": max(end_times) if end_times else None
        })

        cursor += len(chunk)

    return results