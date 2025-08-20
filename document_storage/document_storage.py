import io
import logging
import threading

from documentcloud import DocumentCloud
from documentcloud.exceptions import DoesNotExistError
from settings import ARCHIVED_FILENAME, DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, DOCUMENTCLOUD_PROJECT_TITLE

lock = threading.Lock()

class DocumentStorage():
  def __init__(self):
    self.client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, loglevel=logging.INFO)
    self._ensure_project()
    self._get_archive()

  def _ensure_project(self):
    try:
      self.project = self.client.projects.get(title=DOCUMENTCLOUD_PROJECT_TITLE)
    except DoesNotExistError:
      self.project =  self.client.projects.create(
        title = DOCUMENTCLOUD_PROJECT_TITLE,
        private = False
      )

  def _get_archive(self):
    try:
      with open(ARCHIVED_FILENAME, 'r') as f:
        self.archived = f.read().splitlines()
    except FileNotFoundError as e:
      self.archived = []

    self.archive_file = open(ARCHIVED_FILENAME, 'a')

  def _add_to_archive(self, response_uuid):
    lock.acquire()

    try:
      self.archived.append(response_uuid)
      self.archive_file.write(f"{response_uuid}\n")
      self.archive_file.flush()
    finally:
      lock.release()

  def has_been_archived(self, response_uuid):
    lock.acquire()
    present = response_uuid in self.archived
    lock.release()
    return present

  def get_last_response_number(self):
    lock.acquire()
    length =  len(self.archived)
    lock.release()
    return length

  def upload_file(self, local_path, title, response_uuid, extension, meta_data, description, source, published_url, related_article):
    if self.has_been_archived(response_uuid): return

    self.client.documents.upload(
      local_path,
      original_extension = extension,
      access = 'public',
      project = self.project.id,
      title = title,
      data = meta_data,
      description = description,
      source = source,
      published_url = published_url,
      related_article = related_article
    )

    self._add_to_archive(response_uuid)

  def upload_text(self, text, title, response_uuid, meta_data, description, source, published_url, related_article):
    if self.has_been_archived(response_uuid): return

    stream = io.StringIO(text)
    stream.name = response_uuid

    self.client.documents.upload(
      stream,
      original_extension = 'txt',
      access = 'public',
      project = self.project.id,
      title = title,
      data = meta_data,
      description = description,
      source = source,
      published_url = published_url,
      related_article = related_article
    )

    self._add_to_archive(response_uuid)
