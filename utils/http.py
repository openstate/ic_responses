from tempfile import NamedTemporaryFile

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class FileResource:
    def __init__(self, media_file):
        self.data = None
        self.existed = None
        self.content_type = None
        self.file_size = None
        self.revision_path = None
        self.from_cache = False
        self.media_file = media_file

    def read(self):
        self.data = self.media_file.read()
        self.media_file.seek(0, 0)
        return self.data


class HttpRequestSimple:
    _http_session = None

    @property
    def http_session(self):
        """Returns a :class:`requests.Session` object. A new session is
        created if it doesn't already exist."""
        http_session = getattr(self, '_http_session', None)

        if not http_session:
            urllib3.disable_warnings()
            session = requests.Session()
            session.headers['User-Agent'] = 'Open State'

            http_retry = Retry(total=3, status_forcelist=[500, 503],
                                     backoff_factor=.4)
            http_adapter = HTTPAdapter(max_retries=http_retry)
            session.mount('http://', http_adapter)

            self._http_session = session

        return self._http_session

    def download_url(self, url):
        tm = 15
        http_resp = self.http_session.get(url, stream=True, timeout=(3, tm), verify=False)
        http_resp.raise_for_status()

        # Create a temporary file to store the media item, write the file
        # to disk if it is larger than 1 MB.
        media_file = NamedTemporaryFile(delete=True)

        # When a partial fetch is requested, request up to two MB
        content_length = http_resp.headers.get('content-length')

        retrieved_bytes = 0
        for chunk in http_resp.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive chunks
                media_file.write(chunk)
                retrieved_bytes += len(chunk)

        media_file.flush()


        # If the server doens't provide a content-length, determine the size by looking at the retrieved content
        if not content_length:
            media_file.seek(0, 2)
            content_length = media_file.tell()
        if not content_length:
            content_length = 0

        media_file.seek(0, 0)

        resource = FileResource(media_file)
        resource.content_type = http_resp.headers.get('content-type')
        resource.file_size = content_length
        return resource
