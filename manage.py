import logging
import click

from documentcloud import DocumentCloud
from settings import DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, DOCUMENTCLOUD_PROJECT_TITLE

def _clean_value(value):
  return value.replace('"', '')

@click.group()
def cli():
   pass

@cli.command()
def get_missing():
  client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, loglevel=logging.INFO)
  project = client.projects.get(title=DOCUMENTCLOUD_PROJECT_TITLE)
  result = client.documents.all(project=project.id, per_page = 100)

  all_response_numbers = []
  for doc in result:
    response_number = int(doc.title.split(" ")[0])
    all_response_numbers.append(response_number)

  compare = range(1, 11562)
  diff = set(compare) - set(all_response_numbers)
  print(f"Diff: {diff}")

@cli.command()
def generate_overview():
  client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, loglevel=logging.INFO)
  project = client.projects.get(title=DOCUMENTCLOUD_PROJECT_TITLE)
  result = client.documents.all(project=project.id, per_page=100, ordering="title")

  with open('overview.csv', 'w') as f:
    for doc in result:
      url = _clean_value(doc.published_url)
      name = _clean_value(doc.data['name'][0])
      place = _clean_value(doc.data['place'][0])
      timestamp = _clean_value(doc.data['timestamp'][0])
      row = f'"{url}","{name}","{place}","{timestamp}"'
      f.write(f"{row}\n")

if __name__ == '__main__':
    cli()
