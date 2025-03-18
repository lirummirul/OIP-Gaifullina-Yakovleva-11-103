import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://lapkins.ru/dog/"

output_folder = "выкачка"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

index_file = "index.txt"

# Уже посещенные страницы
visited_urls = set()

# Еще не посещенные страницы
urls_to_visit = [base_url]

def download_page(url, index, index_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Сохраняем HTML-код страницы в текстовый файл
        filename = os.path.join(output_folder, f"page_{index}.txt")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        # Также записываем ссылку на страницу в index
        with open(index_file, "a", encoding="utf-8") as idx_file:
            idx_file.write(f"{index}: {url}\n")

        print(f"Страница {index} успешно скачана: {url}")

        # Возвращаем все ссылки на странице, исключая те, которые содержат "porodi"
        # Потому что там просто сгруппированные списки пород, текста мало
        return [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True) if "porodi" not in a['href']]

    except requests.RequestException as e:
        print(f"Ошибка при скачивании страницы {url}: {e}")
        return []

index = 1

# Проходим 100 страниц
while urls_to_visit and index <= 100:
    current_url = urls_to_visit.pop(0)
    if current_url not in visited_urls:
        visited_urls.add(current_url)   # После посещения страницы добавляем ее в множество посещенных
        new_urls = download_page(current_url, index, index_file)
        urls_to_visit.extend(new_urls)
        index += 1
        time.sleep(1)  # Делаем паузу в 1 секунду, чтобы не перегружать сервер и нас не забанили

print("Все страницы скачаны.")
