import sys
from lib._logger import Log_Init
from lib._bootstrapper import Bootstrapper as Boot
from os import environ as env

try:
    Boot(sys.argv)
except Exception as e:
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

for p,u in zip(search_params, url_list):
    # Utility.do_the_thing(p, u, env['filter_pattern'])
    lgr.debug( f'Param: {p}' )
    lgr.debug( f'URL: {u}' )

lgr.debug( '======App end logging======' )
