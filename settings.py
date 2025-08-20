# Path to the Internet Consultation (do not include the `b1` at the end)
IC_PATH = "/terrorismeverheerlijking"
# Number of pages with responses (responses are crawled from last page to page=1)
NUMBER_RESPONSE_PAGES = 1157
# Project name on DocumentCloud (project will be automatically created if it does not exist yet)
DOCUMENTCLOUD_PROJECT_TITLE = "IC Verheerlijken Terrorisme 2025-08"

# DocumentCloud does not support searching by title. So when the crawler must be rerun, e.g. after an error,
# we cannot check if a certain document has already been uploaded. And adding a document twice results in
# 2 documents on DocumentCloud - there is no `upsert` option. So we keep track of documents uploaded so far
# by writing them to a local file with name ARCHIVED_FILENAME. If you need to reprocess everything, be sure to
# delete the file first.
ARCHIVED_FILENAME = 'archived.txt'

# Errors will be written to ERROR_LOG_NAME
ERROR_LOG_NAME = 'errors.log'



DOMAIN = 'https://www.internetconsultatie.nl'
LOG_FORMATTER = "document_storage.quiet_log_formatter.QuietLogFormatter"

ITEM_PIPELINES = {
  "pipelines.DocumentCloudPipeline": 500
}

try:
    from local_settings import *
except ImportError as e:
    pass