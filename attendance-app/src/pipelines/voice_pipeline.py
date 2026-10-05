"""
Voice pipeline using librosa + scipy — no webrtcvad / resemblyzer needed.
Uses MFCC-based speaker embeddings (mean + std of 40 MFCCs = 80-d vector).
Public API is identical to the old resemblyzer-based version.
"""

import io
import numpy as np
import streamlit as st


def _mfcc_embedding(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Return an 80-d embedding: [mean(MFCCs), std(MFCCs)] over 40 coefficients."""
    import librosa
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    embedding = np.concatenate([mfccs.mean(axis=1), mfccs.std(axis=1)])
    norm = np.linalg.norm(embedding)
    return embedding / norm if norm > 1e-9 else embedding


def get_voice_embedding(audio_bytes: bytes):
    """
    Extract an 80-d speaker embedding from raw audio bytes.
    Returns a list (JSON-serialisable) or None on failure.
    """
    try:
        import librosa
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        if len(audio) < sr * 0.3:          # less than 0.3 s → skip
            return None
        return _mfcc_embedding(audio, sr).tolist()
    except Exception as e:
        st.warning(f"Voice embedding failed: {e}")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold: float = 0.82):
    """
    Cosine-similarity match against stored embeddings.
    Returns (student_id, score) or (None, 0.0).
    """
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_emb = np.array(new_embedding)
    best_sid, best_score = None, -1.0

    for sid, stored in candidates_dict.items():
        if stored:
            stored_emb = np.array(stored)
            score = float(np.dot(new_emb, stored_emb) /
                          (np.linalg.norm(new_emb) * np.linalg.norm(stored_emb) + 1e-9))
            if score > best_score:
                best_score = score
                best_sid = sid

    return (best_sid, best_score) if best_score >= threshold else (None, best_score)


def process_bulk_audio(audio_bytes: bytes, candidates_dict: dict, threshold: float = 0.82):
    """
    Split audio into voiced segments with librosa and identify each speaker.
    Returns {student_id: best_score}.
    """
    try:
        import librosa
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        # Split on silence
        intervals = librosa.effects.split(audio, top_db=30)

        results = {}
        for start, end in intervals:
            if (end - start) < sr * 0.5:    # skip very short segments
                continue
            segment = audio[start:end]
            emb = _mfcc_embedding(segment, sr)
            sid, score = identify_speaker(emb.tolist(), candidates_dict, threshold)
            if sid and (sid not in results or score > results[sid]):
                results[sid] = score

        return results
    except Exception as e:
        st.error(f"Bulk audio error: {e}")
        return {}