# Lab 02 - Aggregating Records

This program downloads TV show records from the TVMaze public API and summarizes the data using several aggregations. The summary is useful for seeing how shows are distributed across genres, languages, ratings, and premiere decades.

## Data source

The program uses the TVMaze API:

https://api.tvmaze.com/shows?page=0

Each record represents one TV show. The selected API page returned 240 show records when this program was run.

## Setup

```text
python -m venv .venv
source .venv/bin/activate
