# Responses crawler for Internet Consultatie

This crawler will collect all responses to the Internet Consultatie specified by
`IC_PATH` in `settings.py` and will store them in `DocumentCloud` in a
project with title specified by `DOCUMENTCLOUD_PROJECT_TITLE` in `settings.py`.

## Important links

  - [Internet Consultatie](https://www.internetconsultatie.nl)
  - [Document Cloud](www.documentcloud.org/projects)

## Installation and usage

  - Clone project
  - Copy `local_settings.py.example` to `local_settings.py` and set values
  - Change `IC_PATH` and `DOCUMENTCLOUD_PROJECT_TITLE`
  - If desired, change names of `ARCHIVED_FILENAME` and `ERROR_LOG_NAME`
  - Build and run using `docker compose -f docker-compose.yml up --build -d`

If you must reprocess all responses, make sure to delete the file denoted by `ARCHIVED_FILENAME` first.

## Debugging

The loglevel for `DocumentCloud` is set to `INFO` and can be changed in `document_storage.py`.

`Scrapy` automatically logs the items that have been scraped. We suppress that using `QuietLogFormatter`.
If you do want to log all items, uncomment the line for `LOG_SCRAPED_ITEMS` in `ICResponsesSpider`.
