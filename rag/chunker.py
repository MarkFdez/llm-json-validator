# rag/chunker.py
#
# Divide documentos de texto en fragmentos (chunks) con solapamiento.
# Entrada : lista de strings (uno por documento)
# Salida  : lista de strings (chunks)

from typing import List


def chunk_documents(
    docs: List[str],
    chunk_size: int = 300,
    overlap: int = 50,
) -> List[str]:
    """
    Divide cada documento en chunks de `chunk_size` caracteres con
    `overlap` caracteres de solapamiento entre chunks consecutivos.

    Parametros
    ----------
    docs       : lista de textos a fragmentar
    chunk_size : longitud maxima de cada chunk en caracteres
    overlap    : caracteres compartidos entre chunks adyacentes

    Retorna
    -------
    Lista plana de chunks (strings). Chunks vacios se descartan.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser mayor que 0")
    if overlap < 0:
        raise ValueError("overlap no puede ser negativo")
    if overlap >= chunk_size:
        raise ValueError("overlap debe ser menor que chunk_size")

    step = chunk_size - overlap
    chunks: List[str] = []

    for doc in docs:
        text = doc.strip()
        if not text:
            continue
        if len(text) <= chunk_size:
            chunks.append(text)
            continue
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += step

    return chunks
