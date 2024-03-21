from ast import Dict
import os, yaml
from os import environ as env
from pathlib import Path
from urllib.parse import quote_plus
class Bootstrapper:
    @classmethod
    def __init__(cls, cli_args) -> None:
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
        
        Bootstrapper.parse_cli_args( cli_args )
        Bootstrapper.validate_env_vars()

    @classmethod
    def get_conf_vars(cls, conf_file_path: str) -> None:
        with open( conf_file_path, 'r' ) as file:
            conf_data = yaml.safe_load( file )
        env['subreddit'] = conf_data['subreddit']
        env['url_path'] = f"/r/{env['subreddit']}/search/"
        if len(conf_data['search_text']) == 0:
            raise ValueError( f'No search text found in configuration file: {conf_file_path}' )
        if len(conf_data['search_text']) == 1:
            env['search_text_set_len'] = '1'
            env['search_text'] = conf_data['search_text']
            env[f'url_query'] = f"?q={quote_plus(conf_data['search_text'])}&sort=new"
        else:
            env['search_text_set_len'] = str(len(conf_data['search_text']))
            for idx,v in enumerate(conf_data['search_text']):
                env[f'url_query_{idx}'] = f"?q={quote_plus(v)}&sort=new"
                env[f'search_text_{idx}'] = v
        env['filter_pattern'] = conf_data['filter_pattern']
        env['sms_key'] = conf_data['sms_key']
        env['sms_to'] = conf_data['sms_to']
        env['sms_from'] = conf_data['sms_from']

    @classmethod
    def parse_arg(cls, arg:str, i:int) -> tuple[str,str]:
        arg_name, arg_value = arg.split('=')
        return (arg_name, arg_value)
    
    @classmethod
    def parse_cli_args(cls, args:list[str]) -> None:
        if len(args) <= 1:
            # raise ValueError(f'No cli arguments provided...')
            print('No cli arguments provided...')
            return
        else:
            for idx, arg in enumerate(args):
                if idx == 0: continue
                if arg.find('=') == -1:
                    # raise Exception( f'Malformed cli argument: {arg}, Expected Syntax: key=value' )
                    print(f'Malformed cli argument: {arg}, Expected Syntax: key=value')
                    print(f'Discarding argument {idx}: {arg}')
                    continue
                try:
                    cls.assign_arg(cls.parse_arg(arg, idx))
                except Exception as e:
                    print(f'Error parsing argument {idx}: {arg}')
                    print(f'Error: {e}')
                    exit(1)
    
    @classmethod
    def assign_arg(cls, args:tuple[str,str]) -> bool:
        arg_name:str = args[0].lower().strip()
        arg_value:str = args[1].lower().strip()
        match arg_name:
            case 'sms':
                env['sms_send'] = arg_value
            case _:
                print(f'Unknown argument: {arg_name}')
                return False
        return True
    
    @classmethod
    def validate_env_vars(cls) -> None:
        try:
            env['sms_send']
        except KeyError:
            print('No sms_send argument provided, defaulting to "n"')
            env['sms_send'] = 'n'
