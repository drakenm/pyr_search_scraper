from bs4 import BeautifulSoup as soup
import requests, sys, logging, re, os, yaml
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
app_path = os.path.dirname( os.path.realpath( __file__ ) )
root_path = os.path.dirname( app_path )
lgr.debug( f'App path: {app_path}' )
lgr.debug( f'Root path: {root_path}' )

conf_path = f'{root_path}/conf.yaml'
if ( os.path.exists( conf_path ) ):
    lgr.debug( 'Found conf.yaml' )
    with open( conf_path, 'r' ) as file:
        conf_data = yaml.safe_load( file )
        lgr.debug( conf_data )
        subreddit = conf_data['subreddit']
        search_text = conf_data['search_text']
else:
    subreddit = input( "Enter subreddit: " )
    lgr.debug( f'User entered subreddit: {subreddit}' )
    search_text = urlparse.quote( input( "Enter search term for subreddit: " ) )
    lgr.debug( f'User entered search term: {search_text}' )



url = f"https://www.reddit.com/r/{subreddit}/search/?q={search_text}&restrict_sr=1&sort=new"
lgr.debug( f'URL: {url}' )

r = requests.get( url, headers={'User-agent': 'Mozilla/5.0'} )

if r.status_code == 200:
    lgr.debug( 'Request successful' )
    page = soup( r.content, 'html.parser' )
    search_result = page.find_all( attrs={"data-testid":"post-title-text"} )
    lgr.debug( f'Found {len(search_result)} search results' )
    for post in search_result:
        href = post['href']
        # title = post.find( 'h3' )
        if post:
            lgr.debug( f'Title: {post.text}' )
            lgr.debug( f'HREF: {href}' )
        else:
            lgr.debug( 'No title found' )