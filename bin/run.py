from bs4 import BeautifulSoup as bs
from urllib2 import urlopen
from getopt import getopt
import requests
import json
import sys
import os
import re

os.nice(20)

output_directory = ''
profile_username = ''
# profile_url = 'https://www.instagram.com/'
websta_url = 'https://websta.me/'
max_dls = 9999

opts, args = getopt(sys.argv[1:], '', ['dest=', 'max='])
for argument in args:
	if 'www.instagram.com/' in argument:
		argument = argument.rstrip('\n/')
		profile_username = argument[argument.rfind('/')+1:]
	else:
		profile_username = argument.rstrip('\n/')

for option, option_argument in opts:
	if option == '--dest':
		output_directory = option_argument
		if not os.path.exists(output_directory):
			os.makedirs(output_directory)
	if option == '--max':
		max_dls = int(option_argument)

if not output_directory:
	output_directory = profile_username
	if not os.path.exists(profile_username):
		os.makedirs(profile_username)

# Get that s640x640/sh0.08/ stuff out of the image's url. I'm guessing it's
# Websta's way of resizing the og Instagram image for its own website format.
resize = re.compile(r's\d+x\d+/(sh\d+\.\d+/)?')

# Compile a pattern that matches with the file url
file_url = re.compile(r'https?://[a-zA-Z0-9\./_-]+(jpg|mp4)')

# Compile a pattern that matches with the file name from the file's url
file_name = re.compile(r'[a-zA-Z0-9_-]+\.(jpg|mp4)')

# Start with the profile's front page on Websta
profile_source = requests.get(websta_url + 'n/' + profile_username)

# Keep clicking "Earlier" to browse further back in time
# until there's no more content
count = 1
while profile_source:
	profile_soup = bs(profile_source.content, 'lxml')

	media_wrappers = profile_soup.find_all('div', {'class': 'mainimg_wrapper'})
	for wrapper in media_wrappers:

		video_tag = wrapper.find(lambda tag: tag.name == 'a'
			and tag['class'] and 'mainimg' not in tag['class'])
		if video_tag and video_tag['href'].endswith('.mp4'):
			# Download the video
			file_name_match = file_name.search(video_tag['href'])
			dl_path = output_directory + '/' + file_name_match.group(0)
			if os.path.exists(dl_path): continue

			file_url_match = file_url.search(video_tag['href']).group(0)
			response = urlopen(file_url_match)
			with open(dl_path, 'wb') as out:
				out.write(response.read())
				count += 1
				print dl_path
			continue

		image_tag = wrapper.find('div', {'class': 'img-cover'})
		if image_tag and image_tag.has_attr('style'):
			# Download the image
			file_name_match = file_name.search(image_tag['style'])
			dl_path = output_directory + '/' + file_name_match.group(0)
			if os.path.exists(dl_path): continue

			file_url_match = file_url.search(image_tag['style'])
			file_url_match = resize.sub('', file_url_match.group(0))
			response = urlopen(file_url_match)
			with open(dl_path, 'wb') as out:
				out.write(response.read())
				count += 1
				print dl_path

		if count >= max_dls: break
	if count >= max_dls: break

	# Set up the next page
	next_page_tag = profile_soup.find('ul', {'class': 'pager'})
	next_page_link = next_page_tag.find('a', href=True)
	if next_page_link:
		profile_source = requests.get(websta_url + next_page_link['href'])
	else: profile_source = None # And exit the while loop