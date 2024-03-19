from ast import Dict
import os, yaml
from os import environ as env
from pathlib import Path
class Bootstrapper:
    @classmethod
    def __init__(cls) -> None:
        env['app_root'] = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) ) )
        env['app_entry'] = os.path.abspath(f'{env["app_root"]}/app/app.py')
        env['app_conf'] = os.path.abspath(f'{env["app_root"]}/conf.yaml')
        env['app_db'] = os.path.abspath(f'{env["app_root"]}/app.db')
        env['app_log'] = os.path.abspath(f'{env["app_root"]}/app.log')
        env['app_log_name'] = 'app_logger'
        env['url_base'] = 'https://www.reddit.com'

        if os.path.exists( env['app_conf'] ):
            cls.get_conf_vars( env['app_conf'] )
        else:
            raise FileNotFoundError( f'Configuration file not found: {env["app_conf"]}' )
        
        env['url_path'] = f"/r/{env['subreddit']}/search/"
        env['url_query'] = f"?q={env['search_text']}&restrict_sr=1&sort=new"

    @classmethod
    def get_conf_vars(cls, conf_file_path: str) -> None:
        with open( conf_file_path, 'r' ) as file:
            conf_data = yaml.safe_load( file )
            env['subreddit'] = conf_data['subreddit']
            env['search_text'] = conf_data['search_text']
            env['filter_pattern'] = conf_data['filter_pattern']
            env['sms_key'] = conf_data['sms_key']
            env['sms_to'] = conf_data['sms_to']
            env['sms_from'] = conf_data['sms_from']