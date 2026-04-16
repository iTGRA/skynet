from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup


@dataclass
class PageDocument:
    url: str
    title: str
    text: str


def fetch_page(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def extract_text(html: str, url: str) -> PageDocument:
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.get_text(strip=True) if soup.title else url
    text = soup.get_text(' ', strip=True)
    return PageDocument(url=url, title=title, text=text)


def iter_documents(urls: Iterable[str]) -> Iterable[PageDocument]:
    for url in urls:
        html = fetch_page(url)
        yield extract_text(html, url)


def main() -> None:
    urls = [
        'https://sfsi.ru/',
    ]
    for document in iter_documents(urls):
        print(document.url)
        print(document.title)
        print(document.text[:500])
        print('-' * 80)


if __name__ == '__main__':
    main()
