"""
Завдання 2
Напишіть Python-скрипт, який завантажує текст із заданої URL-адреси, аналізує 
частоту використання слів у тексті за допомогою парадигми MapReduce і візуалізує 
топ-слова з найвищою частотою використання у тексті.
"""

import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter
from matplotlib import pyplot as plt
import requests

def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        return None

# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word):
    return word, 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

# Виконання MapReduce
def map_reduce(text, search_words=None):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word in search_words]

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

# Функція для візуалізації
def visualize_top_words(result, top_n=10, bar_color='blue'):
    top_words = Counter(result).most_common(top_n)
    words, frequencies = zip(*top_words)
    plt.figure(figsize=(10, 5))
    plt.barh(words, frequencies, color=bar_color)
    plt.xlabel('Частота')
    plt.ylabel('Слова')
    plt.title('Топ {} найчастіше вживаних слів'.format(top_n))
    plt.gca().invert_yaxis()
    plt.show()

if __name__ == '__main__':
    url = "https://gutenberg.net.au/ebooks01/0100021.txt" 
    text = get_text(url)
    if text:
        search_words = None  # Можна вказати конкретні слова для пошуку
        result = map_reduce(text, search_words)
        print("Результат підрахунку слів:", result)
        visualize_top_words(result)
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")