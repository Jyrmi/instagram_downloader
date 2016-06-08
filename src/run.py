#!/usr/bin/env python
"""
Browser-run version of instagram_downloader.
"""

import os
import sys
import re
import itertools
from urllib2 import urlopen
from getopt import getopt
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox # pip install selenium
# from selenium.webdriver.common.keys import Keys

# url and path related stuff
insta_url = 'https://www.instagram.com/'

# --- Pattern definitions ---
# - file_name: usually a sequence of numbers, underscores, a few letters, and
#   an extension. This pattern should match with the file name from the file's
#   url.
file_name = re.compile(r'[a-zA-Z0-9_-]+\.(jpg|mp4)')

# - resize: websta displays a smaller version of all Instagram images, which
#   I'm guessing Instagram created created for other purposes. There's
#   consistently some extra stuff included in the middle of the original image
#   url to reference the smaller versions, like s640x640/sh0.08/ or the like.
#   We can just sub that stuff out and end up with the url to the og image.
resize = re.compile(r'[^/]+\d+x\d+/(sh\d+\.\d+/)?')

def delete_item(driver, n_times):
    """
    Deletes the first media item that appears on the profile.
    """
    # print 'deleting %d item(s)' % n_times

    for _ in itertools.repeat(None, n_times):
        script_find_item = "var aa=document.getElementsByClassName('_8mlbc _vbtk2 _t5r8b')[0];"
        script_delete_item = "aa.parentNode.removeChild(aa)"
        driver.execute_script(script_find_item + script_delete_item)

# def delete_row(driver, n_times):
#     """
#     Deletes the top row (three items) on the profile.
#     """
#     print 'deleting %d row(s)' % n_times
#     delete_item(driver, n_times * 3)

def delete_row(driver, n_times):
    """
    Deletes the top row (three items) on the profile.
    """
    print 'deleting %d row(s)' % n_times

    for _ in itertools.repeat(None, n_times):
        script_find_row = "var aa=document.getElementsByClassName('_myci9')[0];"
        script_delete_row = "aa.parentNode.removeChild(aa)"
        driver.execute_script(script_find_row + script_delete_row)

def download_and_delete_row(driver, n_times, output_directory):
    """
    Deletes the top row (three items) on the profile.
    """
    # print 'dl\'ing & deleting %d row(s)' % n_times

    images = driver.find_elements_by_tag_name('img')
    for i in xrange(n_times * 3):
        link = resize.sub('', images[i].get_attribute('src'))
        fname = file_name.search(link).group(0)
        dl_path = output_directory + '/' + fname

        response = urlopen(link)
        with open(dl_path, 'wb') as out:
            out.write(response.read())

            # DEBUG
            print dl_path


    for _ in itertools.repeat(None, n_times):
        script_find_row = "var aa=document.getElementsByClassName('_myci9')[0];"
        script_delete_row = "aa.parentNode.removeChild(aa)"
        driver.execute_script(script_find_row + script_delete_row)

def count_items(driver):
    """
    Counts the number of media items that appears on the profile.
    """
    items = driver.find_elements_by_class_name('_22yr2')
    count = len(items)

    # print '%d photos/images on page currently' % count

    return count

def print_tags(driver):
    """
	Prints all the media item tags on the current page.
	"""
    media_links = []

    media_tags = driver.find_elements_by_class_name('_icyx7')
    for media_item in media_tags:
        link = media_item.get_attribute('src')
        media_links.append(link)
    print media_links
    print len(media_tags), 'items'

def main():
    """
    Main loop of the scrape.
    """

    profile_username = '' # The Instagram username of the profile from which we
    # are downloading. Must be supplied.
    output_directory = '' # Will be initialized with the optional argument or a
    # default later.
    
    # --- Argument Parsing ---
    opts, args = getopt(sys.argv[1:], '', ['dest='])

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
    # --dest    an optional destination directory for the downloads. Defaults to
    #           a directory of the same name as the target Instagram username in
    #           the current directory.
    for option, option_argument in opts:
        if option == '--dest':
            output_directory = option_argument
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

    # If the output directory doesn't exist, create it.
    if not output_directory:
        output_directory = profile_username
        if not os.path.exists(profile_username):
            os.makedirs(profile_username)

    print profile_username, output_directory

    # max_queue = 30 # maximum number of items in queue before emptying
    loaded = 0
    processed = 0

    driver = Firefox()
    driver.get(insta_url + profile_username)

    # Find the number of posts on this Instagram profile
    profile_soup = BeautifulSoup(driver.page_source, 'lxml')
    post_count_tag = profile_soup.find('span', {'class': '_e8fkl'})
    post_count = int(post_count_tag.text.replace(',', ''))

    # Zoom right out
    # html = driver.find_element_by_tag_name("html")
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)
    # html.send_keys(Keys.CONTROL, Keys.SUBTRACT)

    # Click the 'Load More' element
    driver.find_elements_by_class_name('_oidfu')[0].click()
    driver.execute_script("window.scrollTo(0, -1000000);")
    # loaded = 24

    # Load all the posts into the browser
    while loaded < post_count:

        # print 'processed %d' % processed

        # driver.execute_script("window.scrollTo(0, 1000000);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(.1)
        driver.execute_script("window.scrollTo(0, 0);")
        sleep(1)

        while count_items(driver) > 24 or post_count - processed < 24:
        # while count_items(driver) >= 24:
            download_and_delete_row(driver, 4, output_directory)
            # try:
            #     # delete_row(driver, 4)
            #     download_and_delete_row(driver, 4)
            # except:
            #     break

            processed += 12

        # print 'loaded', loaded, '\tprocessed', processed

        # if loaded - processed >= max_queue or loaded >= post_count:

        #     # print_tags(driver)
        #     print 'EMPTYING QUEUE'

        #     # Repeats <loaded> times
        #     for _ in itertools.repeat(None, (loaded-processed)/3):
        #         delete_row(driver)
        #         processed += 3


        # Load more content by scrolling to the bottom of the page
        # last_position = driver.execute_script('return window.scrollY;')

        # driver.execute_script("window.scrollTo(0, 1000000);")
        # sleep(1.5)

        # new_position = driver.execute_script('return window.scrollY;')
        # print last_position, '>', new_position

        # If the browser successfully loaded more content, count it
        # if last_position != new_position:
        #     loaded += 12

    driver.close()

if __name__ == "__main__":
    main()
