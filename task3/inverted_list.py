import os
import json

def boolean_search(query, inverted_index):
    query = query.lower()
    tokens = []
    current_token = ""
    for char in query:
        if char in "()":
            if current_token:
                tokens.append(current_token.strip())
                current_token = ""
            tokens.append(char)
        elif char in " ":
            if current_token:
                tokens.append(current_token.strip())
                current_token = ""
        else:
            current_token += char
    if current_token:
        tokens.append(current_token.strip())

    tokens = [token for token in tokens if token]

    def shunting_yard(tokens):
        output = []
        operators = []
        precedence = {"not": 3, "and": 2, "or": 1}

        for token in tokens:
            if token in precedence:
                while (operators and operators[-1] != "(" and
                       precedence.get(operators[-1], 0) >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            elif token == "(":
                operators.append(token)
            elif token == ")":
                while operators[-1] != "(":
                    output.append(operators.pop())
                operators.pop()
            else:
                output.append(token)

        while operators:
            output.append(operators.pop())

        return output

    def evaluate(rpn):
        stack = []
        for token in rpn:
            if token == "and":
                right = stack.pop()
                left = stack.pop()
                stack.append(left & right)
            elif token == "or":
                right = stack.pop()
                left = stack.pop()
                stack.append(left | right)
            elif token == "not":
                operand = stack.pop()
                all_docs = set(range(1, 101))
                stack.append(all_docs - operand)
            else:
                stack.append(inverted_index.get(token, set()))
        return stack.pop()

    try:
        rpn = shunting_yard(tokens)
        result = evaluate(rpn)
        return sorted(result)
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return set()


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_file = os.path.join(project_root, 'task3', 'inverted_index.json')

    with open(index_file, 'r', encoding='utf-8') as f:
        inverted_index = {k: set(v) for k, v in json.load(f).items()}

    while True:
        query = input("Введите запрос (или '-1' для выхода): ").strip()
        if query.lower() == '-1':
            break

        result = boolean_search(query, inverted_index)
        print(f"Результат поиска: {result}")


if __name__ == "__main__":
    main()


# собака [1...100]
# тебе [52, 84]
# утром [14, 22, 29, 32, 36, 39, 51, 52, 62, 71, 87]
# Брюссельский [36, 52]
# собака AND тебе [52, 84]
# тебе OR утром [14, 22, 29, 32, 36, 39, 51, 52, 62, 71, 84, 87]
# NOT тебе AND Брюссельский [36]
# собака AND (тебе OR утром) [14, 22, 29, 32, 36, 39, 51, 52, 62, 71, 84, 87]
# собака AND (тебе OR утром) NOT Брюссельский [14, 22, 29, 32, 39, 51, 62, 71, 84, 87]
