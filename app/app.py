from email import errors
from bs4 import BeautifulSoup as soup
import requests, sys, re, os, hashlib, sqlite3
import urllib.parse as urlparse
from lib._logger import Log_Init
from lib._bootstrapper import Bootstrapper as Boot
from os import environ as env, write
from lib._database import Database_Manager

try:
    Boot()
except Exception as e:
    print( f'Logging uninitialized...' )
    print( f'Error bootstrapping: {e}' )
    print( f'Exiting' )
    sys.exit(1)

lgr = Log_Init( logger_name=env['app_log_name'], app_log_path=env['app_log'] ).getLogger()

lgr.debug( '======App begin logging======' )
lgr.debug( f'APP ROOT: {env["app_root"]}' )
lgr.debug( f'APP ENTRY: {env["app_entry"]}' )

url = f"{env['url_base']}{env['url_path']}{env['url_query']}"
lgr.debug( f'URL: {url}' )

r = requests.get( url, headers={'User-agent': 'Mozilla/5.0'} )

def get_hash( data:tuple ) -> str:
    str_to_hash = ''
    for v in data:
        str_to_hash += str(v)
    return hashlib.sha256( str_to_hash.encode( encoding='utf-8', errors='strict' ) ).hexdigest()

def matchFound( needle:re.Pattern, haystack:str ) -> bool:
    if not needle: return False
    # if not re.compile( r'(\(|\[)?' + env['filter_pattern'], re.IGNORECASE ).search( text ):
    if not needle.search( haystack ):
        # lgr.debug( f'Text does not contain {needle.pattern}: {haystack}' )
        return False
    return True

if r.status_code == 200:
    lgr.debug( 'Request successful' )
    page = soup( r.content, 'html.parser' )
    search_result = page.find_all( attrs={"data-testid":"post-title-text"} )
    lgr.debug( f'Found {len(search_result)} search results' )

    dbm = Database_Manager( sqlite3.connect( env['app_db'] ) )

    for index, item in enumerate(search_result):
        if not item:
            lgr.debug( 'No title found' )
            continue
        text = item.text.strip()
        href = item['href']
        filter_text_re = re.compile( r'' + env['filter_pattern'] )
        search_text_re = re.compile( r'' + env['search_text'], re.IGNORECASE )

        if not matchFound( filter_text_re, text ) or not matchFound( search_text_re, text ): continue

        hash = get_hash( (text, href) )
        # check if hash exists in db
        if dbm.select_column( table='results', column='hash', data=hash ):
            lgr.debug( f'{index}\tText: {text}' )
            lgr.debug( f'>\t>\t> Already exists in db' )
            continue
        dbm.add_result( hash, text, href )

        lgr.debug( f'{index}\tText: {text}' )
        lgr.debug( f'\t\tHREF: {href}' )