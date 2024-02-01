from bs4 import BeautifulSoup
import requests, sys, logging
import urllib.parse as urlparse

lgr = logging.getLogger( 'app_logger' )
lgr.setLevel(logging.DEBUG)
lgr_fh = logging.FileHandler( '../app.log', mode='w', encoding='utf-8' )
lgr_fh.setLevel( logging.DEBUG )
lgr_ch = logging.StreamHandler(sys.stdout)
lgr_ch.setLevel( logging.ERROR )
lgr_formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
lgr_fh.setFormatter( lgr_formatter )
lgr_ch.setFormatter( lgr_formatter )
lgr.addHandler( lgr_fh )
lgr.addHandler( lgr_ch )


lgr.debug( '======App begin logging======' )

subreddit = input( "Enter subreddit: " )
lgr.debug( f'User entered subreddit: {subreddit}' )
search_text = urlparse.quote( input( "Enter search term for subreddit: " ) )
lgr.debug( f'User entered search term: {search_text}' )

url = f"https://www.reddit.com/r/{subreddit}/search/?q={search_text}&restrict_sr=1&sort=new"
lgr.debug( f'URL: {url}' )

