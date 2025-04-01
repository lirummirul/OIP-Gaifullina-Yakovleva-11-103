import os
import json
from collections import defaultdict

def read_tokens(filename):
    tokens = set()
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            token = line.strip()
            if token:
                tokens.add(token)
    return tokens

def build_inverted_index(folder_path, tokens):
    inverted_index = defaultdict(set)
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            doc_id = int(filename.replace("page_", "").replace(".txt", ""))
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                text = file.read()
                for token in tokens:
                    if token in text:
                        inverted_index[token].add(doc_id)
    return inverted_index

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(project_root, 'task1', 'выкачка')
    tokens_file = os.path.join(project_root, 'task2', 'tokens.txt')
    output_file = os.path.join(project_root, 'task3', 'inverted_index.json')

    tokens = read_tokens(tokens_file)

    inverted_index = build_inverted_index(folder_path, tokens)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({k: list(v) for k, v in inverted_index.items()}, file, ensure_ascii=False, indent=4)

    print(f"Инвертированный индекс сохранён в файл: {output_file}")

if __name__ == "__main__":
    main()