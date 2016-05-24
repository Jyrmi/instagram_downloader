from bs4 import BeautifulSoup as bs
from urllib2 import urlopen
from getopt import getopt
import requests
import json
import sys
import os

os.nice(20)

output_directory = ''
profile_username = ''
profile_url = 'https://www.instagram.com/'
page_prefix = 'https://www.instagram.com/p/'

opts, args = getopt(sys.argv[1:], '', ['dest='])
for argument in args:
	if 'www.instagram.com/' in argument:
		profile_url = argument
	else:
		profile_username = argument
		profile_url += argument

for option, option_argument in opts:
	if option == '--dest':
		output_directory = option_argument
		if not os.path.exists(output_directory):
			os.makedirs(output_directory)

if not output_directory:
	if not profile_username:
		profile_username = profile_url[profile_url.rfind('/'):]
	if not os.path.exists(profile_username):
		os.makedirs(profile_username)
		output_directory = profile_username

profile_source = requests.get(profile_url)
profile_soup = bs(profile_source.content, 'lxml')
body_tag = profile_soup.find('body', {'class': ''})
script_tags = body_tag.find_all('script', {'type': 'text/javascript'})

items = ''
tag = script_tags[0]
embedded_json = tag.text[tag.text.find('{'):tag.text.rfind('}')+1]
items = json.loads(embedded_json.encode("iso-8859-1", "ignore"))

for page in items['entry_data']['ProfilePage']:
	for node in page['user']['media']['nodes']:
		print node['id']
		if node['is_video']: # Open the link to the video
			dl_path = output_directory + '/' + node['id'] + '.mp4'
			if os.path.exists(dl_path): continue
			video_source = requests.get(page_prefix + node['code'])
			video_soup = bs(video_source.content, 'lxml')
			meta_tag = video_soup.find('meta',
				{'property': 'og:video:secure_url'})
			video_link = meta_tag['content']
			response = urlopen(video_link)
			with open(dl_path, 'wb') as out:
				out.write(response.read())
		else: # Is an image
			dl_path = output_directory + '/' + node['id'] + '.jpg'
			if os.path.exists(dl_path): continue
			response = urlopen(node['display_src'])
			with open(dl_path, 'wb') as out:
				out.write(response.read())