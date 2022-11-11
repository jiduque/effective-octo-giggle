from string import ascii_lowercase
from multiprocessing import Pool
from json import dump, load

import requests

from bs4 import BeautifulSoup


BASE_URL = "https://scrabble.merriam.com/words/start-with/"
DESTINATION = "scrabble_words.json"


def main() -> None:
    output = []

    with Pool(5) as p:
        results = p.map(get_words_starting_with, ascii_lowercase)
        for words in results:
            output.extend(words)

        write(output, DESTINATION)


def get_words_starting_with(letter: str) -> list[str]:
    output = []
    url = f"{BASE_URL}/{letter}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    relevant_divs = soup.find_all("div", class_="wres_slideable")
    for div in relevant_divs:
        list_elements = div.find_all("li")
        words = list(
            filter(
                lambda w: 2 <= len(w) <= 7,
                map(
                    lambda li: li.text.strip(),
                    list_elements
                )
            )
        )
        output.extend(words)
    return output


def write(values: list[str], path: str) -> None:
    with open(path, 'w') as filehandle:
        dump(values, filehandle)


def load_words() -> list[str]:
    with open(DESTINATION, 'r') as filehandle:
        return load(filehandle)


if __name__ == '__main__':
    main()
