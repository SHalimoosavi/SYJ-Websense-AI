#!/usr/bin/env python3
"""
SYJ WebSense AI
Website Scraper Module

Author: Syed Ali Hasan Moosavi
License: MIT
"""

from __future__ import annotations

import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; Mobile) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0 Safari/537.36"
)


def clean_text(text: str) -> str:
    """
    Normalize whitespace and clean extracted text.
    """
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def scrape_website(url: str) -> Dict:
    """
    Scrape a website and return structured content.

    Returns:
    {
        "title": str,
        "description": str,
        "headings": list[str],
        "paragraphs": list[str],
        "word_count": int
    }
    """

    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
            allow_redirects=True,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        raise Exception("Request timed out after 10 seconds.")

    except requests.exceptions.ConnectionError:
        raise Exception("Unable to connect to website.")

    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP Error: {e}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request Failed: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unwanted tags
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "iframe",
            "svg",
            "footer",
            "nav",
        ]
    ):
        tag.decompose()

    # Title
    title = ""
    if soup.title and soup.title.string:
        title = clean_text(soup.title.string)

    # Meta Description
    description = ""

    meta_desc = soup.find(
        "meta",
        attrs={"name": "description"},
    )

    if meta_desc and meta_desc.get("content"):
        description = clean_text(meta_desc["content"])

    # Headings
    headings: List[str] = []

    for tag_name in ["h1", "h2", "h3"]:
        for tag in soup.find_all(tag_name):
            text = clean_text(tag.get_text(" ", strip=True))

            if text and text not in headings:
                headings.append(text)

    # Paragraphs
    paragraphs: List[str] = []

    for p in soup.find_all("p"):
        text = clean_text(p.get_text(" ", strip=True))

        if len(text) > 20:
            paragraphs.append(text)

    combined_text = " ".join(headings + paragraphs)

    word_count = len(combined_text.split())

    return {
        "title": title,
        "description": description,
        "headings": headings,
        "paragraphs": paragraphs,
        "word_count": word_count,
    }


if __name__ == "__main__":
    test_url = input("Enter URL: ").strip()

    try:
        result = scrape_website(test_url)

        print("\n=== SCRAPE RESULT ===")
        print("Title:", result["title"])
        print("Description:", result["description"])
        print("Headings:", len(result["headings"]))
        print("Paragraphs:", len(result["paragraphs"]))
        print("Words:", result["word_count"])

    except Exception as e:
        print(f"Error: {e}")
