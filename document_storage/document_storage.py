import io
import logging

from documentcloud import DocumentCloud
from documentcloud.exceptions import DoesNotExistError
from .settings import DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD

class DocumentStorage():
  PROJECT_TITLE = "IC Verheerlijken Terrorisme 2025-08"
  ARCHIVED_FILENAME = 'archived.txt'

  def __init__(self):
    self.client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, loglevel=logging.DEBUG)
    self._ensure_project()
    self._get_archive()

  def _ensure_project(self):
    try:
      self.project = self.client.projects.get(title=self.PROJECT_TITLE)
    except DoesNotExistError:
      self.project =  self.client.projects.create(
        title = self.PROJECT_TITLE,
        private = False
      )

  def _get_archive(self):
    try:
      with open(self.ARCHIVED_FILENAME, 'r') as f:
        self.archived = f.read().splitlines()
    except FileNotFoundError as e:
      self.archived = []

    self.archive_file = open(self.ARCHIVED_FILENAME, 'a')

  def _add_to_archive(self, filename):
    self.archived.append(filename)
    self.archive_file.write(f"{filename}\n")
    self.archive_file.flush()

  def has_been_archived(self, filename):
    return filename in self.archived

  def upload_file(self, local_path, filename, extension, meta_data):
    if self.has_been_archived(filename): return

    self.client.documents.upload(
      local_path,
      original_extension = extension,
      access = 'public',
      project = self.project.id,
      title = filename,
      data = meta_data
    )

    self._add_to_archive(filename)

  def upload_text(self, text, filename, meta_data):
    if self.has_been_archived(filename):
      print(f"\n\n FILE {filename} has already been archived")
      return

    stream = io.StringIO(text)
    stream.name = filename

    self.client.documents.upload(
      stream,
      original_extension = 'txt',
      access = 'public',
      project = self.project.id,
      data = meta_data
    )

    self._add_to_archive(filename)
