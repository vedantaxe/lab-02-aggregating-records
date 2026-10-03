import json
from pathlib import Path

import requests


SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
OUTPUT = Path("summary.json")


def fetch_records(url):
    """Download the records and return them as Python objects."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not download records: {exc}") from exc


def shows_per_genre(records):
    """Count how many shows belong to each genre."""
    genre_counts = {}

    for show in records:
        genres = show.get("genres", [])

        if not isinstance(genres, list):
            continue

        for genre in genres:
            if isinstance(genre, str) and genre.strip():
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return genre_counts


def average_rating_by_language(records):
    """Calculate the average rating for each language."""
    ratings_by_language = {}

    for show in records:
        language = show.get("language")
        rating = show.get("rating", {}).get("average")

        if not isinstance(language, str) or not language.strip():
            continue

        if not isinstance(rating, (int, float)):
            continue

        ratings_by_language.setdefault(language, []).append(rating)

    return {
        language: round(sum(ratings) / len(ratings), 2)
        for language, ratings in ratings_by_language.items()
    }


def shows_per_decade(records):
    """Count how many shows premiered in each decade."""
    decades = set()

    for show in records:
        premiered = show.get("premiered")

        if not isinstance(premiered, str) or len(premiered) < 4:
            continue

        try:
            year = int(premiered[:4])
        except ValueError:
            continue

        decade = (year // 10) * 10
        decades.add(decade)

    return {
        decade: sum(
            1
            for show in records
            if isinstance(show.get("premiered"), str)
            and len(show.get("premiered")) >= 4
            and show.get("premiered")[:4].isdigit()
            and (int(show.get("premiered")[:4]) // 10) * 10 == decade
        )
        for decade in sorted(decades)
    }


def build_summary(records):
    """Combine all aggregations into one summary dictionary."""
    return {
        "source_url": SOURCE_URL,
        "record_count": len(records),
        "shows_per_genre": shows_per_genre(records),
        "average_rating_by_language": average_rating_by_language(records),
        "shows_per_decade": shows_per_decade(records),
    }


def write_summary(summary, path):
    """Write the summary dictionary to a JSON file."""
    path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


def main():
    """Run the program from download to JSON output."""
    try:
        records = fetch_records(SOURCE_URL)

        if not isinstance(records, list):
            raise RuntimeError("Downloaded data is not a list of records.")

        if len(records) < 50:
            raise RuntimeError(
                f"Expected at least 50 records, but received {len(records)}."
            )

        summary = build_summary(records)
        write_summary(summary, OUTPUT)

        print(f"Downloaded {len(records)} records.")
        print(f"Summary written to {OUTPUT}.")

    except RuntimeError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()