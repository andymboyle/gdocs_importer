import gdata.docs.service
import gdata.spreadsheet.service
import os
import tempfile
import csv


def get_spreadsheet(account, password, key, gid=0):
    gd_client = gdata.docs.service.DocsService()
    gd_client.email = account
    gd_client.password = password
    gd_client.source = "Private Spreadsheet Downloader"
    gd_client.ProgrammaticLogin()

    spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
    spreadsheets_client.email = gd_client.email
    spreadsheets_client.password = gd_client.password
    spreadsheets_client.source = "Private Spreadsheet Downloader"
    spreadsheets_client.ProgrammaticLogin()

    file_path = tempfile.mktemp(suffix='.csv')
    uri = 'https://docs.google.com/feeds/documents/private/full/%s' % key
    try:
        entry = gd_client.GetDocumentListEntry(uri)
        docs_auth_token = gd_client.GetClientLoginToken()
        gd_client.SetClientLoginToken(
            spreadsheets_client.GetClientLoginToken())
        gd_client.Export(entry, file_path)
        gd_client.SetClientLoginToken(docs_auth_token)
        return csv.reader(file(file_path).readlines())
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass
