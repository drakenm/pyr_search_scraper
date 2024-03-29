import os, yaml
from os import environ as env
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
        
    @classmethod
    def get_conf_vars(cls, conf_file_path: str) -> None:
        with open( conf_file_path, 'r' ) as file:
            conf_data = yaml.safe_load( file )
        env['subreddit'] = conf_data['subreddit']
        env['url_path'] = f"/r/{env['subreddit']}/search/"
        if len(conf_data['search_text']) == 0:
            raise ValueError( f'No search text found in configuration file: {conf_file_path}' )
        if len(conf_data['search_text']) == 1:
            env['search_text'] = conf_data['search_text']
            env[f'url_query'] = f"?q={conf_data['search_text']}&sort=new"
        else:
            env['search_text_len'] = str(len(conf_data['search_text']))
            for i,v in conf_data['search_text'].enumerate():
                env[f'url_query_{i}'] = f"?q={v}&sort=new"
                env[f'search_text_{i}'] = v
        env['filter_pattern'] = conf_data['filter_pattern']
        env['sms_key'] = conf_data['sms_key']
        env['sms_to'] = conf_data['sms_to']
        env['sms_from'] = conf_data['sms_from']