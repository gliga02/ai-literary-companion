import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

os.makedirs(RAW_DATA_DIR, exist_ok=True)



BOOKS = {
    "crime_and_punishment.txt": "https://gutenberg.org/cache/epub/2554/pg2554.txt",
    "great_expectations.txt": "https://gutenberg.org/cache/epub/1400/pg1400.txt",
    "the_count_of_monte_christo": "https://gutenberg.org/cache/epub/1184/pg1184.txt",
}

def download_book(filename: str, url: str) -> None:
    path = os.path.join(RAW_DATA_DIR, filename)

    print(f"Downloading {filename} from {url}...")
    urllib.request.urlretrieve(url, path)
    print(f"Saved to {path}")


def main():
    for filename, url in BOOKS.items():
        download_book(filename, url)


if __name__ == "__main__":
    main()
