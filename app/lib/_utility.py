from lib._logger import Log_Init
import hashlib, re, requests, sqlite3, praw
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
    def do_the_thing( subreddit:praw.models.SubredditHelper, search_param:str, filter_pattern:str, return_limit:int=5 ) -> None:
        dbm = Database_Manager( sqlite3.connect( env['app_db'] ) )
        aldi_finds:dict = {}
        raw_search_param = search_param.strip('"')
        search_text_re = re.compile( r'' + raw_search_param, re.IGNORECASE )
        filter_text_re = re.compile( filter_pattern, re.IGNORECASE )
        price_text_re = re.compile( r'\$\d{1,6}' )

        for i in subreddit.search(search_param, sort='new', limit=return_limit):
            id, title, url, post = i.id, i.title, i.url, i.selftext
            if not Utility.matchFound( filter_text_re, i.title ) or not Utility.matchFound( search_text_re, i.title ): continue
                # Utility.lgr.debug( f'Keyword or filter not found in title...' )
            # if Utility.matchFound( filter_text_re, i.title ) and Utility.matchFound( search_text_re, i.title ):
            # check if id exists in db
            if dbm.select_column( table='results', column='id', data=id ):
                Utility.lgr.debug( f'\t{title}' )
                Utility.lgr.debug( f'\t{id} already exists in db...' )
                continue
            Utility.lgr.info(f'\tNew id found:\t{id}' )
            Utility.lgr.debug( f'\t{title}' )
            Utility.lgr.debug( f'\t{url}' )
            keyword_index = post.find(raw_search_param)
            left_newline = post.rfind( '\n', 0, keyword_index )
            right_newline = post.find( '\n', keyword_index, len(post))
            price_snippet = post[left_newline+1:right_newline]
            Utility.lgr.debug( f'\t\tkeyword index: {keyword_index}' )
            Utility.lgr.debug( f'\t\tleft newline: {left_newline}' )
            Utility.lgr.debug( f'\t\tright newline: {right_newline}' )
            Utility.lgr.info( f'\t\tPrice: {price_snippet}' )
            # works well but what is a dollar sign doesn't exist in the derived price snippet?
            if not Utility.matchFound( price_text_re, price_snippet ):
                Utility.lgr.debug( f'\t\t\tPrice snippet does NOT contain a dollar sign...' )
                Utility.lgr.debug( f'\t\t\tLooking after the string for a dollar sign...' )
                adjusted_keyword_index = post.find('$', right_newline, len(post))
                adjusted_left_newline = post.rfind( '\n', 0, adjusted_keyword_index )
                adjusted_right_newline = post.find( '\n', adjusted_keyword_index, len(post))
                adjusted_price_snippet = post[left_newline+1:adjusted_right_newline]
                Utility.lgr.debug( f'\t\t\tadjusted keyword index: {adjusted_keyword_index}' )
                Utility.lgr.debug( f'\t\t\tadjusted left newline: {adjusted_left_newline}' )
                Utility.lgr.debug( f'\t\t\tadjusted right newline: {adjusted_right_newline}' )
                Utility.lgr.info( f'\t\t\tadjusted price snippet: {adjusted_price_snippet}' )
            aldi_finds[id] = {'title': title, 'url': url, 'price': price_snippet}
            dbm.add_result( id, title, url, price_snippet )

        if env['sms_send'] == 'y':
            for k, v in aldi_finds.items():
                Utility.lgr.debug("\t\t\tBuilding sms message...")
                message = f"New Ad Posted for a {search_param}:\n\n{v['title']}\n\n{v['url']}\n\nPrice: {v['price']}"
                if env['sms_key']:
                    Utility.lgr.debug( f"\t\t\tSending SMS..." )
                    Utility.send_sms( env['sms_key'], message )
        else:
            Utility.lgr.debug( f'\t\t\tSMS not enabled...' )
