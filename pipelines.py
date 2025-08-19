from document_storage.document_storage import DocumentStorage
from utils.error_log import ErrorLog
from utils.http import HttpRequestSimple

class DocumentCloudPipeline:
  def __init__(self):
      self.document_storage = DocumentStorage()

  def process_item(self, item, spider):
    meta_data = {
       "name": item['name'],
       "place": item['place'],
       "timestamp": item.get_timestamp(),
       "url": item['url']
    }
    filename = item.get_filename()

    if len(item['attachments']) > 0:
      if len(item['attachments']) > 1:
        message = f'{filename}: more than 1 attachment not supported'
        ErrorLog().write(message)
        raise Exception(message)

      meta_data["extra_text"] = item['text'][:300] # 300 is max length for json value for DocumentCloud
      file_resource = HttpRequestSimple().download_url(item['attachments'][0])
      extension = None
      if file_resource.content_type == 'application/pdf':
        extension = 'pdf'
      else:
        message = f"{filename}: unsupported content type {file_resource.content_type}"
        ErrorLog().write(message)
        raise Exception(message)

      self.document_storage.upload_file(file_resource.media_file.name, filename, extension, meta_data)
    else:
      self.document_storage.upload_text(item['text'], filename, meta_data)

    return item