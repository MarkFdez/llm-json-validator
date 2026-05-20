# rag/retriever.py
#
# Recuperador de chunks relevantes usando TF-IDF + similitud coseno.
# No requiere GPU ni modelos pesados; todo en CPU con sklearn.

from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve(
    query: str,
    chunks: List[str],
    top_k: int = 3,
) -> List[str]:
    """
    Devuelve los `top_k` chunks mas relevantes para `query`
    usando TF-IDF y similitud coseno.

    Parametros
    ----------
    query  : pregunta o texto de busqueda
    chunks : fragmentos de documentos indexados
    top_k  : numero maximo de chunks a devolver

    Retorna
    -------
    Lista de hasta `top_k` strings ordenados por relevancia descendente.
    Si no hay chunks o la query esta vacia, retorna lista vacia.
    """
    if not chunks or not query.strip():
        return []

    k = min(top_k, len(chunks))

    vectorizer = TfidfVectorizer(
        strip_accents="unicode",
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
    )

    corpus = chunks + [query]
    tfidf_matrix = vectorizer.fit_transform(corpus)

    chunk_vectors = tfidf_matrix[:-1]
    query_vector  = tfidf_matrix[-1]

    scores = cosine_similarity(query_vector, chunk_vectors).flatten()

    top_indices = scores.argsort()[::-1][:k]

    return [chunks[i] for i in top_indices if scores[i] > 0.0]
