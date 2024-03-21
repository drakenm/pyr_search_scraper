from lib._logger import Log_Init
from bs4 import BeautifulSoup as soup
import hashlib, re, requests, sqlite3, sys
from lib._database import Database_Manager
from os import environ as env
class Utility:
    lgr = Log_Init( logger_name=env['app_log_name'], app_log_path=env['app_log'] ).getLogger()

    @staticmethod
    def get_hash( data:tuple ) -> str:
        str_to_hash = ''
        for v in data:
            str_to_hash += str(v)
        return hashlib.sha256( str_to_hash.encode( encoding='utf-8', errors='strict' ) ).hexdigest()

    @staticmethod
    def matchFound( needle:re.Pattern, haystack:str ) -> bool:
        if not needle: return False
        if not needle.search( haystack ):
            return False
        return True

    @staticmethod
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
            Utility.lgr.error( f'Failed to send SMS: {e}' )
            return f'Failed to send SMS: {e}'
        if r.status_code != 200:
            Utility.lgr.error( f'Failed to send SMS: {r.status_code}' )
            Utility.lgr.error( f'Response: {r.text}' )
        return r.text
    
    @staticmethod
    def do_the_thing( search_text:str, url:str, filter_pattern:str ) -> None:
        r = requests.get( url, headers={'User-agent': 'Mozilla/5.0'} )

        if r.status_code != 200:
            Utility.lgr.error( f'Request failed with status code: {r.status_code}' )
            sys.exit(1)

        Utility.lgr.debug( 'Request successful' )
        page = soup( r.content, 'html.parser' )
        search_result = page.find_all( attrs={"data-testid":"post-title-text"} )
        Utility.lgr.debug( f'Found {len(search_result)} search results' )

        dbm = Database_Manager( sqlite3.connect( env['app_db'] ) )

        aldi_finds:dict = {}

        for index, item in enumerate(search_result):
            if not item:
                Utility.lgr.debug( 'No title found' )
                continue
            title = item.get_text(strip=True, separator=" ").strip()
            href = item['href']
            filter_text_re = re.compile( r'' + env['filter_pattern'] )
            search_text_re = re.compile( r'' + env['search_text'], re.IGNORECASE )

            if not Utility.matchFound( filter_text_re, title ) or not Utility.matchFound( search_text_re, title ): continue

            hash = Utility.get_hash( (title, href) )
            # check if hash exists in db
            if dbm.select_column( table='results', column='hash', data=hash ):
                Utility.lgr.debug( f'{index}. Already exists in db...' )
                Utility.lgr.debug( f'\t {hash}' )
                Utility.lgr.debug( f'\t {title}' )
                Utility.lgr.debug( f'\t {href}' )
                continue

            Utility.lgr.info(f'{index}. New result found!' )
            Utility.lgr.info( f'\t {hash}' )
            Utility.lgr.info( f'\t {title}' )
            Utility.lgr.info( f'\t {href}' )

            result_url = f"{env['url_base']}{href}"


            Utility.lgr.debug( f'\tSearch Result Item URL: {result_url}' )
            result_get = requests.get( result_url, headers={'User-agent': 'Mozilla/5.0'} )
            result_page = soup( result_get.content, 'html.parser' )
            price_text_re = re.compile( r'\$\d{1,6}' )
            result_content = result_page.find_all( string=price_text_re )
            
            if len(result_content) > 0:
                Utility.lgr.info( f'Found {len(result_content)} results containing a dollar sign ($)...' )
                for index, item in enumerate(result_content):
                    body_snippet:str = item.get_text(strip=True, separator=" ").lower().strip()
                    if len(result_content) == 1:
                        Utility.lgr.debug( "\tOnly one result found...")
                        Utility.lgr.debug( f'\tprice snippet is most likely:' )
                        Utility.lgr.debug( f'\t\t> {body_snippet}' )
                        price_snippet = body_snippet
                    elif len(result_content) > 1 and Utility.matchFound( search_text_re, body_snippet ):
                        Utility.lgr.debug( f'\tprice snippet is most likely:' )
                        Utility.lgr.debug( f'\t\t> {body_snippet}' )
                        price_snippet = body_snippet
                try:
                    price_snippet
                except NameError:
                    Utility.lgr.debug( f'No price snippet found...' )
                    price_snippet = 'Price not found'
            aldi_finds[hash] = {'title': title, 'url': result_url, 'price': price_snippet}
            dbm.add_result( hash, title, result_url, price_snippet )

        for k, v in aldi_finds.items():
            Utility.lgr.info( f'Found {v["title"]} at {v["url"]} for {v["price"]}' )
            Utility.lgr.debug("building sms message...")
            message = f"New Ad Posted for a {env['search_text']}:\n\n{v['title']}\n\n{v['url']}\n\nPrice: {v['price']}"
            Utility.lgr.debug( f"{message}" )
            if env['sms_key']:
                # Utility.lgr.debug( f"Not sending SMS for now..." )
                Utility.lgr.debug( f"Sending SMS..." )
                Utility.send_sms( env['sms_key'], message )