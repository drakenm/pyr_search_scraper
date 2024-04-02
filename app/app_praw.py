import sys, praw
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

if env['search_text_set_len'] == '1':
    url_list = [f"{env['url_base']}{env['url_path']}{env['url_query']}"]
    search_params = [env['search_text']]
else:
    url_list = []
    search_params = []
    for i in range(0, int(env['search_text_set_len'])):
        url_list.append( f"{env['url_base']}{env['url_path']}{env[f'url_query_{i}']}" )
        search_params.append( env[f'search_text_{i}'] )
lgr.debug( f'Search Parameters: {search_params}' )

rdt = praw.Reddit(
    client_id=env['app_client_id'],
    client_secret=env['app_client_secret'],
    user_agent=env['app_user_agent']
)

for p,u in zip(search_params, url_list):
    lgr.debug( f'Search Query:\t{p}' )
    gafs = rdt.subreddit(env['subreddit'])
    Utility.do_the_thing( gafs, p, env['filter_pattern'], 20 )

lgr.debug( '======App end logging======' )
