import os
import math
import json
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(PROJECT_ROOT, 'task1', 'выкачка')
INDEX_FILE = os.path.join(PROJECT_ROOT, 'task1', 'index.txt')
TFIDF_TOKENS_DIR = os.path.join(PROJECT_ROOT, 'task4', 'tfidf_tokens')
INVERTED_INDEX_PATH = os.path.join(PROJECT_ROOT, 'task3', 'inverted_index.json')
TOTAL_DOCS = 100


def load_links():
    links = {}
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(':', 1)
            if len(parts) == 2:
                doc_id = parts[0].strip()
                url = parts[1].strip()
                try:
                    links[int(doc_id)] = url
                except ValueError:
                    continue
    return links


def load_inverted_index():
    with open(INVERTED_INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tfidf_vectors():
    vectors = {}
    for filename in os.listdir(TFIDF_TOKENS_DIR):
        if filename.endswith('.txt'):
            doc_id = int(filename.split('_')[-1].split('.')[0])
            vectors[doc_id] = {}
            with open(os.path.join(TFIDF_TOKENS_DIR, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        term, idf, tfidf = parts
                        vectors[doc_id][term] = float(tfidf)
    return vectors


class VectorSearchEngine:
    def __init__(self):
        self.links = load_links()
        self.inverted_index = load_inverted_index()
        self.tfidf_vectors = load_tfidf_vectors()
        self.all_terms = self._get_all_terms()

    def _get_all_terms(self):
        terms = set()
        for doc_id in self.tfidf_vectors:
            terms.update(self.tfidf_vectors[doc_id].keys())
        return sorted(terms)

    def query_to_vector(self, query_text):
        tokens = [w.lower() for w in query_text.split() if w.isalpha()]
        lemmas = tokens  # Замените на вашу лемматизацию

        lemma_counts = Counter(lemmas)
        query_vector = np.zeros(len(self.all_terms))

        for i, term in enumerate(self.all_terms):
            if term in lemma_counts:
                tf = lemma_counts[term] / len(lemmas)
                # Получаем документы для термина из JSON (уже в правильном формате)
                doc_count = len(self.inverted_index.get(term, []))
                idf = math.log(TOTAL_DOCS / (doc_count + 1e-10))
                query_vector[i] = tf * idf
        return query_vector

    def search(self, query_text, top_n=10):
        query_vec = self.query_to_vector(query_text)
        scores = []

        for doc_id in range(1, TOTAL_DOCS + 1):
            doc_vec = np.zeros(len(self.all_terms))
            for i, term in enumerate(self.all_terms):
                doc_vec[i] = self.tfidf_vectors.get(doc_id, {}).get(term, 0)

            norm_query = np.linalg.norm(query_vec)
            norm_doc = np.linalg.norm(doc_vec)
            if norm_query > 0 and norm_doc > 0:
                similarity = np.dot(query_vec, doc_vec) / (norm_query * norm_doc)
            else:
                similarity = 0
            scores.append((doc_id, similarity))

        scores = [(doc_id, score) for doc_id, score in scores if score > 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]

    def print_results(self, scores):
        if not scores:
            print("Ничего не найдено")
            return

        print(f"Топ 10 документов, найдено: {len(scores)}")
        for doc_id, score in scores:
            print(f"Документ {doc_id} (сходство: {score:.4f}): {self.links.get(doc_id, 'ссылка не найдена')}")


if __name__ == "__main__":
    engine = VectorSearchEngine()

    print("=== Векторная поисковая система ===")
    while True:
        query = input("\nВведите поисковый запрос (или -1 для выхода): ").strip()
        if query.lower() == '-1':
            break

        results = engine.search(query)
        engine.print_results(results)
