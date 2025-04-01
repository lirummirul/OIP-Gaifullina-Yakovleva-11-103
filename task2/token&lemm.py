import os
import re
import nltk
from pymorphy2 import MorphAnalyzer
from nltk.corpus import stopwords
from collections import defaultdict

nltk.download('stopwords')

morph = MorphAnalyzer()

def tokenize_text(text):
    text = re.sub(r'[^а-яА-Я\s-]', '', text)
    tokens = re.findall(r'\b[а-яА-Я-]+\b', text)
    tokens = [word.lower() for word in tokens]
    stop_words = set(stopwords.words('russian'))
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [word for word in tokens if not any(char.isdigit() for char in word)]
    return list(set(tokens))


def process_documents(input_folder, output_tokens_dir, output_lemmas_dir):
    os.makedirs(output_tokens_dir, exist_ok=True)
    os.makedirs(output_lemmas_dir, exist_ok=True)

    all_tokens = set()
    all_lemmas = defaultdict(set)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            doc_id = filename.split('.')[0]

            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
                text = f.read()

            tokens = tokenize_text(text)
            all_tokens.update(tokens)

            token_file = os.path.join(output_tokens_dir, f'{doc_id}_tokens.txt')
            with open(token_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(tokens))

            lemmatized = defaultdict(list)
            for token in tokens:
                lemma = morph.parse(token)[0].normal_form.lower()
                lemmatized[lemma].append(token)
                all_lemmas[lemma].add(token)

            lemma_file = os.path.join(output_lemmas_dir, f'{doc_id}_lemmas.txt')
            with open(lemma_file, 'w', encoding='utf-8') as f:
                for lemma, forms in lemmatized.items():
                    f.write(f"{lemma}: {' '.join(forms)}\n")

    with open(os.path.join(project_root, 'task2', 'tokens.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(all_tokens)))

    with open(os.path.join(project_root, 'task2', 'lemmatized_tokens.txt'), 'w', encoding='utf-8') as f:
        for lemma in sorted(all_lemmas.keys()):
            f.write(f"{lemma}: {' '.join(sorted(all_lemmas[lemma]))}\n")


def main():
    global project_root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_folder = os.path.join(project_root, 'task1', 'выкачка')
    output_tokens = os.path.join(project_root, 'task2', 'tokens')
    output_lemmas = os.path.join(project_root, 'task2', 'lemmas')

    process_documents(input_folder, output_tokens, output_lemmas)


if __name__ == "__main__":
    main()