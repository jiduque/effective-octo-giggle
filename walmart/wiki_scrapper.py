from json import dump, load

import requests

from bs4 import BeautifulSoup


URL = "https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_violent_crime_rate"
YEAR, YEAR_INDEX = 2018, 4
SAVE_LOCATION = f"crime_{YEAR}.json"

DataPoints = dict[str, float]
Soup = BeautifulSoup


def main() -> None:
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")

    data_rows = get_rows(table)
    output = dict(map(
        lambda row: process_row(row, YEAR_INDEX),
        data_rows
    ))

    write(output, SAVE_LOCATION)


def process_row(row: Soup, year_index: int) -> tuple[str, float]:
    vals = row.find_all("td")
    key = vals[0].text.strip()
    val = float(vals[year_index].text.strip())
    return key, val


def get_rows(table: Soup) -> list:
    all_rows = table.find_all("tr")
    output = filter(
        lambda row: not row.find_all("th"),
        all_rows
    )
    return list(output)


def write(values: DataPoints, path: str) -> None:
    with open(path, 'w') as filehandle:
        dump(values, filehandle)


def load_stats() -> DataPoints:
    with open(SAVE_LOCATION, 'r') as filehandle:
        return load(filehandle)
    pass


if __name__ == '__main__':
    main()
