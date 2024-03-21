from lib._logger import Log_Init
import hashlib, re, requests
from os import environ as env
class Utility():
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
        # if not re.compile( r'(\(|\[)?' + env['filter_pattern'], re.IGNORECASE ).search( text ):
        if not needle.search( haystack ):
            # lgr.debug( f'Text does not contain {needle.pattern}: {haystack}' )
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