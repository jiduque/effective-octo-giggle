from typing import Union
from json import loads
from os import stat

import requests
import pandas as pd


CURR_STORES = 3568  # Total number of stores
MAX_ITER = 8862  # Max number of store number to go up to
BASE_URL = "https://www.walmart.com/store"
SAVE_NAME = "walmart_data.csv"


# Some timed out, so I just got them manually
MISSING_POINTS = [
    {
        "postalCode": 76645,
        "address": "401 Coke Ave",
        "city": "Hillsboro",
        "state": "TX",
        "startHr": "00:00",
        "endHr": "24:00",
        "storeNumber": 211
    },
    {
        "postalCode": 76135,
        "address": "6364 Lake Worth Blvd",
        "city": "Lake Worth",
        "state": "TX",
        "startHr": "00:00",
        "endHr": "24:00",
        "storeNumber": 717
    }
]


DataFrame = pd.DataFrame
StupidThing = Union[dict, int, None]


def main() -> None:
    data = get_walmart_store_data(CURR_STORES, MAX_ITER)
    data.drop(['country', 'streetAddress'], axis=1, inplace=True)
    data = data.append(MISSING_POINTS, ignore_index=True)
    data.to_csv(SAVE_NAME)


def get_info(text: str, key: str) -> dict:
    key = f'"{key}":' + "{"
    n = len(key) - 1
    start = text.find(key)
    i = 1
    while text[start + i] != "}":
        i += 1
    return loads(text[start+n:(start + i + 1)])


def get_store_info(store_number: int) -> StupidThing:
    url = f"{BASE_URL}/{store_number}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    if not all(map(lambda x: x in response.text, ["address", "dailyHours"])):
        with open('could_not_parse.txt', "a+") as file:
            init_string = f"{store_number}"
            if stat('could_not_parse.txt').st_size != 0:
                init_string = "," + init_string
            file.write(init_string)
        return 1
    
    output = get_info(response.text, "address")
    hour_info = get_info(response.text, "dailyHours")
      
    if "startHr" not in hour_info or "endHr" not in hour_info:
        with open('could_not_parse.txt', "a+") as file:
            init_string = f"{store_number}"
            if stat('could_not_parse.txt').st_size != 0:
                init_string = "," + init_string
            file.write(init_string)
        return 1
    
    output["startHr"] = hour_info["startHr"]
    output["endHr"] = hour_info["endHr"]
    output["storeNumber"] = store_number
    
    return output
    

def get_walmart_store_data(total_stores: int, max_iter: int = 10000) -> DataFrame:
    n_stores, store_num = 0, 1
    all_values = []
    while n_stores < total_stores and store_num <= max_iter:
        store_info = get_store_info(store_num)
        if store_info is not None:
            if isinstance(store_info, dict):
                all_values.append(store_info)
            n_stores += 1
        store_num += 1
    return pd.DataFrame(all_values)


if __name__ == '__main__':
    main()
