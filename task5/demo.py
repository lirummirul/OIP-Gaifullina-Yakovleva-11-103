from flask import Flask, render_template, request
import os
import math
import json
from collections import defaultdict, Counter
import numpy as np

app = Flask(__name__)

# Конфигурация (оставляем ваш существующий код)
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


# Создаем экземпляр поисковика при запуске приложения
search_engine = VectorSearchEngine()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_engine.search(query, top_n=10)

        # Форматируем результаты для вывода в HTML
        formatted_results = []
        for doc_id, score in results:
            formatted_results.append({
                'id': doc_id,
                'score': f"{score:.4f}",
                'url': search_engine.links.get(doc_id, 'ссылка не найдена')
            })

        return render_template('results.html',
                               query=query,
                               results=formatted_results,
                               found=len(formatted_results))

    return render_template('index.html')


if __name__ == '__main__':
    # Создаем папку для шаблонов, если ее нет
    os.makedirs(os.path.join(app.root_path, 'templates'), exist_ok=True)

    # Создаем простые HTML-шаблоны
    with open(os.path.join(app.root_path, 'templates', 'index.html'), 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Поисковая система</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .search-box { display: flex; margin-bottom: 20px; }
        input[type="text"] { flex-grow: 1; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; background: #4285f4; color: white; border: none; cursor: pointer; }
        .result { margin-bottom: 15px; padding: 10px; border: 1px solid #eee; }
        .score { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <h1>Поисковая система</h1>
    <form method="POST">
        <div class="search-box">
            <input type="text" name="query" placeholder="Введите поисковый запрос..." required>
            <button type="submit">Искать</button>
        </div>
    </form>
</body>
</html>''')

    with open(os.path.join(app.root_path, 'templates', 'results.html'), 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Результаты поиска</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .search-box { display: flex; margin-bottom: 20px; }
        input[type="text"] { flex-grow: 1; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; background: #4285f4; color: white; border: none; cursor: pointer; }
        .result { margin-bottom: 15px; padding: 10px; border: 1px solid #eee; }
        .score { color: #666; font-size: 14px; }
        .back-link { display: block; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Результаты поиска</h1>
    <form method="POST">
        <div class="search-box">
            <input type="text" name="query" value="{{ query }}" required>
            <button type="submit">Искать</button>
        </div>
    </form>

    <p>Найдено результатов: {{ found }}</p>

    {% for result in results %}
    <div class="result">
        <h3><a href="{{ result.url }}" target="_blank">Документ {{ result.id }}</a></h3>
        <div class="score">Сходство: {{ result.score }}</div>
    </div>
    {% endfor %}

    <a href="/" class="back-link">Новый поиск</a>
</body>
</html>''')

    app.run(debug=True)
