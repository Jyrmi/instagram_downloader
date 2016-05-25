from bs4 import BeautifulSoup as bs
from multiprocessing import Pool
from urllib2 import urlopen
from getopt import getopt
import requests
import sys
import os
import re

# --- Setup/declarations ---
os.nice(20)				# Make this process lowest priority

# Macros of sorts
workers = 30			# Size of the process pool used to download files
max_queue = 1000		# The maximum number of links to process at once.
max_dls = 999999		# Program terminates after downloading this many items

# url and path related stuff
output_directory = ''	# Will be initialized with the optional argument or a
						# default later.
profile_username = ''	# The Instagram username of the profile from which we
						# are downloading. Must be supplied.
websta_url = 'https://websta.me/' # Websta homepage



# --- Multiprocessing things ---
links = [] 	# Queue for the links to the images/videos, needed by
			# multiprocessing's map()

# Function that is used in multiprocessing's map(). Downloads the file at the
# url and writes it to disk.
def fetch_media(link):
	file_name_match = file_name.search(link).group(0)
	dl_path = output_directory + '/' + file_name_match

	response = urlopen(link)
	with open(dl_path, 'wb') as out:
		out.write(response.read())

		# DEBUG
		print dl_path



# --- Argument Parsing ---
opts, args = getopt(sys.argv[1:], '', ['dest=', 'max='])

# Expecting only one argument that isn't an option, which is the Instagram
# username or profile url. We only want the username for our purposes so strip
# off anything in a url that isn't a part of the username.
for argument in args:
	if 'www.instagram.com/' in argument:
		argument = argument.rstrip('\n/')
		profile_username = argument[argument.rfind('/')+1:]
	else:
		profile_username = argument.rstrip('\n/')

# Optional arguments
# --dest	an optional destination directory for the downloads. Defaults to
#			a directory of the same name as the target Instagram username in
#			the current directory.
# --max		an optional limit to the number of images/videos to download.
#			Defaults to 999,999.
for option, option_argument in opts:
	if option == '--dest':
		output_directory = option_argument
		if not os.path.exists(output_directory):
			os.makedirs(output_directory)
	if option == '--max':
		max_dls = int(option_argument)

# If the output directory doesn't exist, create it.
if not output_directory:
	output_directory = profile_username
	if not os.path.exists(profile_username):
		os.makedirs(profile_username)



# --- Pattern definitions ---
# - the links we need are often tucked away in the javascript of the html doc.

# - resize: websta displays a smaller version of all Instagram images, which
#	I'm guessing Instagram created created for other purposes. There's
#	consistently some extra stuff included in the middle of the original image
#	url to reference the smaller versions, like s640x640/sh0.08/ or the like.
#	We can just sub that stuff out and end up with the url to the og image.
resize = re.compile(r'[^/]+\d+x\d+/(sh\d+\.\d+/)?')

# - file_url: gets the url of the media item. Just looking for something that
#	starts with http and ends with jpg or mp4. Usually this link is embedded
#	within a bunch of surrounding javascript, so we want to cut that stuff
#	away.
file_url = re.compile(r'https?://[a-zA-Z0-9\./_-]+(jpg|mp4)')

# - file_name: usually a sequence of numbers, underscores, a few letters, and
#	an extension. This pattern should match with the file name from the file's
#	url.
file_name = re.compile(r'[a-zA-Z0-9_-]+\.(jpg|mp4)')



# --- Main Loop ---
process_pool = Pool(workers)

# Start with the Websta profile's first page.
profile_source = requests.get(websta_url + 'n/' + profile_username)
while profile_source:
	profile_soup = bs(profile_source.content, 'lxml')

	# Each individual image/video is contained within a div of this class.
	media_wrappers = profile_soup.find_all('div', {'class': 'mainimg_wrapper'})
	for wrapper in media_wrappers:

		# Video case
		# The video url is contained within an 'a' tag of an arcane class that
		# I don't think I should risk checking for exactly. All I know is that
		# class="mainimg" indicates an image, not a video, so check for
		# anything but.
		video_tag = wrapper.find(lambda tag: tag.name == 'a'
			and tag['class'] and 'mainimg' not in tag['class'])
		if video_tag and video_tag['href'].endswith('.mp4'): # Ensuring video

			# If the file already exists from a past scrape, then skip it.
			file_name_match = file_name.search(video_tag['href'])
			dl_path = output_directory + '/' + file_name_match.group(0)
			if os.path.exists(dl_path): continue

			# Otherwise, get the video source url and download it.
			file_url_match = file_url.search(video_tag['href']).group(0)

			# Append to the list and leave the rest to the workers.
			links.append(file_url_match)

			continue # There's also an image along with every video just
			# showing a still frame of the video. We don't need this, but the
			# next block of code would catch it, so continue past it.

		# If we've reached this point, no video link was found, so an image is
		# guaranteed.

		# Image case
		image_tag = wrapper.find('div', {'class': 'img-cover'})
		if image_tag and image_tag.has_attr('style'):

			# If the file already exists from a past scrape, then skip it.
			file_name_match = file_name.search(image_tag['style'])
			dl_path = output_directory + '/' + file_name_match.group(0)
			if os.path.exists(dl_path): continue

			# Otherwise, get the image source url and download it.
			file_url_match = file_url.search(image_tag['style'])

			# Here we are removing the extra stuff in the url that makes this
			# link reference a smaller, inferior version of the image. Sub it
			# out.
			file_url_match = resize.sub('', file_url_match.group(0))

			# Append to the list and leave the rest to the workers.
			links.append(file_url_match)

	# Set up the next page of items.
	# Keep clicking "Earlier" to browse further back in time until there's no
	# more content. The 'earlier' button is represented by the 'pager' list in
	# the html document.
	next_page_tag = profile_soup.find('ul', {'class': 'pager'})
	next_page_link = next_page_tag.find('a', href=True) # find the link within
	if next_page_link:
		profile_source = requests.get(websta_url + next_page_link['href'])
	else: profile_source = None # This will exit the while loop next iteration

	# Start the processes once the queue is full or there is no more content.
	if len(links) >= max_queue or not profile_source:
		process_pool.map(fetch_media, links)
		links = []


		# process_pool.map(lambda link:
		# 	open(output_directory + '/' +
		# 		file_name.search(link).group(0),
		# 		'wb').write(urlopen(link).read()), links)

		# Sad lambda function attempt for map ^