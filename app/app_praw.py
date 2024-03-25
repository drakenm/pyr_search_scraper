import sys, praw, re
from lib._logger import Log_Init
from lib._bootstrapper import Bootstrapper as Boot
from os import environ as env

try:
    Boot(sys.argv)
except FileNotFoundError as e:
    print( f'Logging uninitialized...' )
    print( f'Error bootstrapping: {e}' )
    print( f'Exiting' )
    sys.exit(1)

from lib._utility import Utility

lgr = Log_Init( logger_name=env['app_log_name'], app_log_path=env['app_log'] ).getLogger()

lgr.debug( '======App begin logging======' )
lgr.debug( f'APP ROOT: {env["app_root"]}' )
lgr.debug( f'APP ENTRY: {env["app_entry"]}' )

if env['search_text_set_len'] == '1':
    url_list = [f"{env['url_base']}{env['url_path']}{env['url_query']}"]
    search_params = [env['search_text']]
else:
    url_list = []
    search_params = []
    for i in range(0, int(env['search_text_set_len'])):
        url_list.append( f"{env['url_base']}{env['url_path']}{env[f'url_query_{i}']}" )
        search_params.append( env[f'search_text_{i}'] )
lgr.debug( f'URL(s): {url_list}' )

rdt = praw.Reddit(
    client_id=env['app_client_id'],
    client_secret=env['app_client_secret'],
    user_agent=env['app_user_agent']
)

for p,u in zip(search_params, url_list):
    lgr.debug( f'Param: {p}' )
    lgr.debug( f'URL: {u}' )
    gafs = rdt.subreddit(env['subreddit'])
    raw_search_param = p.strip('"')
    filter_text_re = re.compile( env['filter_pattern'], re.IGNORECASE )
    price_text_re = re.compile( r'\$\d{1,6}' )
    new_line_re = re.compile( r'\n' )
    search_text_re = re.compile( r'' + raw_search_param, re.IGNORECASE )
    for i in gafs.search(p, sort='new', limit=5):
        id = i.id
        title = i.title
        url = i.url
        if Utility.matchFound( filter_text_re, i.title ) and Utility.matchFound( search_text_re, i.title ):
            print(i.id, ":", i.title, ":", i.url)
            keyword_index = i.selftext.find(raw_search_param)
            left_newline = i.selftext.rfind( '\n', 0, keyword_index )
            right_newline = i.selftext.find( '\n', keyword_index, len(i.selftext))
            price_snippet = i.selftext[left_newline+1:right_newline]
            print( f'keyword index: {keyword_index}' )
            print( f'left newline: {left_newline}' )
            print( f'right newline: {right_newline}' )
            print( f'Price: {price_snippet}' )
            # works well but what is a dollar sign doesn't exist in the derived price snippet?
            if not Utility.matchFound( price_text_re, price_snippet ):
                print( f'Price snippet does NOT contain a dollar sign...' )
                print( f'Looking after the string for a dollar sign...' )
                adjusted_keyword_index = i.selftext.find('$', right_newline, len(i.selftext))
                adjusted_left_newline = i.selftext.rfind( '\n', 0, adjusted_keyword_index )
                adjusted_right_newline = i.selftext.find( '\n', adjusted_keyword_index, len(i.selftext))
                adjusted_price_snippet = i.selftext[left_newline+1:adjusted_right_newline]
                print( f'adjusted keyword index: {adjusted_keyword_index}' )
                print( f'adjusted left newline: {adjusted_left_newline}' )
                print( f'adjusted right newline: {adjusted_right_newline}' )
                print( f'adjusted price snippet: {adjusted_price_snippet}' )

    aldi_finds[id] = {'title': title, 'url': url, 'price': price_snippet}
    dbm.add_result( id, title, url, price_snippet )

lgr.debug( '======App end logging======' )
