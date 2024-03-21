from bs4 import BeautifulSoup as soup
import requests, sys, re, hashlib, sqlite3
from lib._logger import Log_Init
from lib._bootstrapper import Bootstrapper as Boot
from os import environ as env
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

def send_sms( key:str, message:str ) -> str:
    url = f"https://sandbox.dialpad.com/api/v2/sms?apikey={key}"
    payload = {
        'from_number': env['sms_from'],
        'to_numbers': [env['sms_to']],
        'text': message
    }
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    try:
        r = requests.post( url, json=payload, headers=headers )
    except Exception as e:
        lgr.error( f'Failed to send SMS: {e}' )
        return f'Failed to send SMS: {e}'
    if r.status_code != 200:
        lgr.error( f'Failed to send SMS: {r.status_code}' )
        lgr.error( f'Response: {r.text}' )
    return r.text

if r.status_code != 200:
    lgr.error( f'Request failed with status code: {r.status_code}' )
    sys.exit(1)

lgr.debug( 'Request successful' )
page = soup( r.content, 'html.parser' )
search_result = page.find_all( attrs={"data-testid":"post-title-text"} )
lgr.debug( f'Found {len(search_result)} search results' )

dbm = Database_Manager( sqlite3.connect( env['app_db'] ) )

aldi_finds:dict = {}

for index, item in enumerate(search_result):
    if not item:
        lgr.debug( 'No title found' )
        continue
    title = item.get_text(strip=True, separator=" ").strip()
    href = item['href']
    filter_text_re = re.compile( r'' + env['filter_pattern'] )
    search_text_re = re.compile( r'' + env['search_text'], re.IGNORECASE )

    if not matchFound( filter_text_re, title ) or not matchFound( search_text_re, title ): continue

    hash = get_hash( (title, href) )
    # check if hash exists in db
    if dbm.select_column( table='results', column='hash', data=hash ):
        lgr.debug( f'{index}. Already exists in db...' )
        lgr.debug( f'\t {hash}' )
        lgr.debug( f'\t {title}' )
        lgr.debug( f'\t {href}' )
        continue

    lgr.info(f'{index}. New result found!' )
    lgr.info( f'\t {hash}' )
    lgr.info( f'\t {title}' )
    lgr.info( f'\t {href}' )

    result_url = f"{env['url_base']}{href}"


    lgr.debug( f'\tSearch Result Item URL: {result_url}' )
    result_get = requests.get( result_url, headers={'User-agent': 'Mozilla/5.0'} )
    result_page = soup( result_get.content, 'html.parser' )
    price_text_re = re.compile( r'\$\d{1,6}' )
    result_content = result_page.find_all( string=price_text_re )
    
    if len(result_content) > 0:
        lgr.info( f'Found {len(result_content)} results containing a dollar sign ($)...' )
        for index, item in enumerate(result_content):
            body_snippet:str = item.get_text(strip=True, separator=" ").lower().strip()
            if len(result_content) == 1:
                lgr.debug( "\tOnly one result found...")
                lgr.debug( f'\tprice snippet is most likely:' )
                lgr.debug( f'\t\t> {body_snippet}' )
                price_snippet = body_snippet
            elif len(result_content) > 1 and matchFound( search_text_re, body_snippet ):
                lgr.debug( f'\tprice snippet is most likely:' )
                lgr.debug( f'\t\t> {body_snippet}' )
                price_snippet = body_snippet
        try:
            price_snippet
        except NameError:
            lgr.debug( f'No price snippet found...' )
            price_snippet = 'Price not found'
    aldi_finds[hash] = {'title': title, 'url': result_url, 'price': price_snippet}
    dbm.add_result( hash, title, result_url, price_snippet )

for k, v in aldi_finds.items():
    lgr.info( f'Found {v["title"]} at {v["url"]} for {v["price"]}' )
    lgr.debug("building sms message...")
    message = f"New Ad Posted for a {env['search_text']}:\n\n{v['title']}\n\n{v['url']}\n\nPrice: {v['price']}"
    lgr.debug( f"{message}" )
    if env['sms_key']:
        # lgr.debug( f"Not sending SMS for now..." )
        lgr.debug( f"Sending SMS..." )
        send_sms( env['sms_key'], message )


lgr.debug( '======App end logging======' )
