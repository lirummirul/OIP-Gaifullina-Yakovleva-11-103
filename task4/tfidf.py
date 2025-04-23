import os
import math
from collections import defaultdict

# Пути к файлам
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs_folder = os.path.join(project_root, 'task1', 'выкачка')
tokens_folder = os.path.join(project_root, 'task2', 'tokens')
lemmas_folder = os.path.join(project_root, 'task2', 'lemmas')

# Создаем папки для результатов
output_tokens = os.path.join(project_root, 'task4', 'tfidf_tokens')
output_lemmas = os.path.join(project_root, 'task4', 'tfidf_lemmas')
os.makedirs(output_tokens, exist_ok=True)
os.makedirs(output_lemmas, exist_ok=True)


def load_tokens(filename):
    """Загрузка токенов из файла"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]


def load_lemmas(filename):
    """Загрузка лемм из файла"""
    lemmas = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(': ')
            if len(parts) == 2:
                lemma, forms = parts
                lemmas[lemma] = forms.split()
    return lemmas


def count_doc_frequencies(folder):
    """Подсчет частоты документов, содержащих термин/лемму"""
    doc_freq = defaultdict(int)

    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
                content = f.read().lower()
                terms = set()

                if 'lemmas' in folder:
                    # Для лемм собираем все формы
                    for line in content.split('\n'):
                        if ':' in line:
                            lemma = line.split(':')[0]
                            terms.add(lemma)
                else:
                    # Для токенов просто строки
                    terms.update(line.strip() for line in content.split('\n') if line.strip())

                for term in terms:
                    doc_freq[term] += 1

    return doc_freq


def calculate_tf_idf():
    """Основная функция для расчета TF-IDF"""
    # Подсчитываем частоту документов для токенов и лемм
    total_docs = 100
    token_doc_freq = count_doc_frequencies(tokens_folder)
    lemma_doc_freq = count_doc_frequencies(lemmas_folder)

    # Вычисляем IDF для всех токенов и лемм
    token_idf = {term: math.log(total_docs / (freq + 1)) for term, freq in token_doc_freq.items()}
    lemma_idf = {lemma: math.log(total_docs / (freq + 1)) for lemma, freq in lemma_doc_freq.items()}

    # Обрабатываем каждый документ
    for doc_file in os.listdir(docs_folder):
        if doc_file.endswith('.txt'):
            doc_id = doc_file.replace('page_', '').replace('.txt', '')

            # Чтение токенов документа
            token_file = os.path.join(tokens_folder, f'page_{doc_id}_tokens.txt')
            if os.path.exists(token_file):
                with open(token_file, 'r', encoding='utf-8') as f_tokens:
                    words = [line.strip() for line in f_tokens if line.strip()]
                    total_terms = len(words)
            else:
                words = []
                total_terms = 0

            # Обработка токенов
            token_file = os.path.join(tokens_folder, f'page_{doc_id}_tokens.txt')
            if os.path.exists(token_file):
                tokens = load_tokens(token_file)
                token_counts = defaultdict(int)
                for word in words:
                    if word in tokens:
                        token_counts[word] += 1

                # Запись TF-IDF для токенов
                with open(os.path.join(output_tokens, f'tfidf_tokens_{doc_id}.txt'), 'w', encoding='utf-8') as f_out:
                    for token in tokens:
                        tf = token_counts.get(token, 0) / total_terms
                        idf = token_idf.get(token, 0)
                        tfidf = tf * idf
                        f_out.write(f"{token} {idf} {tfidf}\n")

            # Обработка лемм
            lemma_file = os.path.join(lemmas_folder, f'page_{doc_id}_lemmas.txt')
            if os.path.exists(lemma_file):
                lemmas = load_lemmas(lemma_file)  # Загружаем леммы и их формы
                lemma_counts = defaultdict(int)

                # Считаем, сколько раз формы леммы встречаются среди токенов
                for lemma, forms in lemmas.items():
                    for form in forms:
                        # Количество вхождений формы леммы в список токенов
                        lemma_counts[lemma] += words.count(form)

                # Запись TF-IDF для лемм
                with open(os.path.join(output_lemmas, f'tfidf_lemmas_{doc_id}.txt'), 'w', encoding='utf-8') as f_out:
                    for lemma in lemmas:
                        tf = lemma_counts.get(lemma, 0) / total_terms
                        idf = lemma_idf.get(lemma, 0)
                        tfidf = tf * idf
                        f_out.write(f"{lemma} {idf} {tfidf}\n")


if __name__ == "__main__":
    calculate_tf_idf()