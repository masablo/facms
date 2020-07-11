from itemadapter import ItemAdapter

import json
import sqlite3
from datetime import datetime
from scrapy.exceptions import DropItem
from facms.spiders import GoogleApi as gapi
from facms.spiders import FOLDER_ID


class DatabasePipeline:

    CHECK_TABLE = '''
        SELECT count(*) FROM sqlite_master
        WHERE type='table' and name='article'
    '''

    CREATE_TABLE = '''
        CREATE TABLE article (
            key text primary key,
            title text,
            author text,
            kind text,
            tag text,
            section text,
            date text
        )
    '''
    INSERT = '''
        INSERT INTO article (
            key,
            title,
            author,
            kind,
            tag,
            section,
            date
        ) VALUES (
            ?,?,?,?,?,?,?
        )
    '''
    # DIRNAME = os.path.dirname(__file__)
    DATABASE_NAME = 'articles.db'
    conn = None

    def __init__(self):
        self.conn = sqlite3.connect(self.DATABASE_NAME)
        self.cursor = self.conn.cursor()
        if self.cursor.execute(self.CHECK_TABLE).fetchone()[0] == 0:
            self.cursor.execute(self.CREATE_TABLE)

    def process_item(self, item, spider):
        if spider.name == 'facms':
            try:
                self.cursor.execute(
                    self.INSERT,(
                        item['key'],
                        item['title'],
                        item['author'],
                        item['kind'],
                        item['tag'],
                        item['section'],
                        item['date']
                    )
                )
                self.conn.commit()
            except sqlite3.Error as e:
                print('sqlite3.Error occurred:', e.args[0])
        else:
            raise DropItem('spider not found')
        return item

    # def open__spider(self, spider):
    #      self.conn = sqlite3.connect(self.DATABASE_NAME)

    def close__spider(self, spider):
        self.conn.close()


class SpreadsheetPipeline:

    articles = []

    def open__spider(self, spider):
        pass

    def _make_sheet_in_drive(self, name):
        file_metadata = {
            'name': name,
            'parents': [FOLDER_ID],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        serviceDrive = gapi.get_service(api_name='drive',
                                        api_version='v3',
                                        scopes=['https://www.googleapis.com/auth/drive',
                                                'https://www.googleapis.com/auth/drive.file',
                                                'https://www.googleapis.com/auth/drive.appdata'])
        return serviceDrive.files().create(body=file_metadata, fields='id').execute()

    def _add_data_to_sheet(self, sheet, data):
        body = {
            'range': 'A1',
            'majorDimension': 'ROWS',
            'values': data
        }
        serviceSheet = gapi.get_service(api_name='sheets',
                                        api_version='v4',
                                        scopes=['https://www.googleapis.com/auth/spreadsheets'])
        resource = serviceSheet.spreadsheets().values()
        resource.append(spreadsheetId=sheet.get('id'),
            range='A1', valueInputOption='USER_ENTERED', body=body).execute()

    def process_item(self, item, spider):
        self.articles.append(list(item.values()))
        return item

    def close_spider(self, spider):
        self.articles.insert(0, ['key', 'title', 'author', 'kind', 'tag', 'section', 'date'])
        name = datetime.today.strftime('%Y-%m-%d')
        sheet = self._make_sheet_in_drive(name)
        self._add_data_to_sheet(sheet, self.articles)
