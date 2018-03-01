'''
Fetch DB files

To Do - Add Logging support

'''
import os, urllib3, zipfile
from datetime import datetime

base_directory =  os.path.dirname(os.path.abspath(__file__))
archive_directory = os.path.join(base_directory, 'ndc_textfiles')

def insist_on_db_archive():
    if not os.path.exists(archive_directory):
        os.mkdir(archive_directory)


def fetch_ndctext_db():
    url = 'https://www.accessdata.fda.gov/cder/ndctext.zip'
    db_file = os.path.join(
                    archive_directory,
                    datetime.now().strftime('ndctext_%Y%m%d-%H%M%S.zip')
                    )
    
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    of = open(db_file, 'wb')
    of.write(r.data)
    of.close()
    zf = zipfile.ZipFile(db_file)
    zf.extract('product.txt', path=base_directory)
    zf.extract('package.txt', path=base_directory)

def main():
    insist_on_db_archive()
    fetch_ndctext_db()

