from document_storage.document_storage import DocumentStorage
from settings import DOMAIN, IC_PATH
from utils.error_log import ErrorLog
from utils.http import HttpRequestSimple

class DocumentCloudPipeline:
  def __init__(self):
      self.document_storage = DocumentStorage()

  def log_error(self, message):
      ErrorLog().write(message)

  def process_item(self, item, spider):
    meta_data = {
       "name": item['name'],
       "place": item['place'],
       "timestamp": item.get_timestamp()
    }
    title = f"{item['response_number']:05d} - {item['name']} - {item['place']}"
    response_uuid = item.get_response_uuid()
    description = item.get_description()
    source = "Internet Consultatie 'Wetsvoorstel strafbaarstelling verheerlijken van terrorisme en openbare steunbetuiging aan terroristische organisaties'"
    published_url = item['url']
    related_article = f"{DOMAIN}{IC_PATH}"

    if len(item['attachments']) > 0:
      if len(item['attachments']) > 1:
        message = f'{response_uuid}: more than 1 attachment not supported'
        self.log_error(message)
        raise Exception(message)

      meta_data["extra_text"] = item['text'][:300] # 300 is max length for json value for DocumentCloud
      file_resource = HttpRequestSimple().download_url(item['attachments'][0])
      extension = None
      if file_resource.content_type == 'application/pdf':
        extension = 'pdf'
      else:
        message = f"{response_uuid}: unsupported content type {file_resource.content_type}"
        self.log_error(message)
        raise Exception(message)

      self.document_storage.upload_file(file_resource.media_file.name, title, response_uuid, extension, meta_data, \
                                        description, source, published_url, related_article)
    else:
      self.document_storage.upload_text(item['text'], title, response_uuid, meta_data, \
                                        description, source, published_url, related_article)

    return item