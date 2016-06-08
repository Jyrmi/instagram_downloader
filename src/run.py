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
from selenium.webdriver import Firefox # pip install selenium


insta_url = 'https://www.instagram.com/'

# --- Pattern definitions ---
# - file_name: usually a sequence of numbers, underscores, a few letters, and
#   an extension. This pattern should match with the file name from the file's
#   url.
file_name = re.compile(r'[a-zA-Z0-9_-]+\.(jpg|mp4)')

# - resize: Instagram sometimes displays a smaller version of images, which
#   I'm guessing Instagram created created for thumbnails. There's
#   consistently some extra stuff included in the middle of the original image
#   url to reference the smaller versions, like s640x640/sh0.08/ or the like.
#   We can just sub that stuff out and end up with the url to the og image.
resize = re.compile(r'[^/]+\d+x\d+/(sh\d+\.\d+/)?')

# - crop: same thing as with resize here; something like c86.0.550.550/ is
#   added to the url to crop the image for thumbnails. Sub it out.
crop = re.compile(r'c[\d\.]+/')


def download_from_url(url, directory='./', serialize=False, number=0):
    fname = file_name.search(url).group(0)

    if serialize:
        fname = '(' + str(number) + ') ' + fname

    dl_path = directory + '/' + fname

    response = urlopen(url)
    with open(dl_path, 'wb') as out:
        out.write(response.read())

    # DEBUG
    print dl_path


def fetch_row_links(driver):
    """
    Gets the url of each image from the top row (three items) on the profile.
    """
    urls = []
    for image in driver.find_elements_by_class_name('_icyx7')[:3]:

        resized = resize.sub('', image.get_attribute('src'))
        link = crop.sub('', resized)

        urls.append(link)

    return urls


def delete_row(driver):
    """
    Removes the top row of images from view (by deleting them from the DOM).
    """
    find_row = "var aa=document.getElementsByClassName('_myci9')[0];"
    remove_row = "aa.parentNode.removeChild(aa)"
    try:
        driver.execute_script(find_row + remove_row)
    except:
        print 'exception: no more images'
        exit(0)


def count_items(driver):
    """
    Counts the number of media items that appears on the profile.
    """
    items = driver.find_elements_by_class_name('_22yr2')

    return len(items)


def main():
    """
    Main loop of the scrape.
    """

    profile_username = '' # The Instagram username of the profile from which we
    # are downloading. Must be supplied.
    output_directory = '' # Will be initialized with the optional argument or a
    # default later.
    update_mode = False
    serialize = False

    # --- Argument Parsing ---
    opts, args = getopt(sys.argv[1:], '', ['dest=', 'update', 'serialize'])

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
        elif option == '--update':
            update_mode = True
        elif option == '--serialize':
            serialize = True

    # If the output directory doesn't exist, create it.
    if not output_directory:
        output_directory = profile_username
        if not os.path.exists(profile_username):
            os.makedirs(profile_username)

    # Start the browser
    driver = Firefox()
    driver.get(insta_url + profile_username)

    # Find the number of posts on this Instagram profile
    post_count_tag = driver.find_element_by_class_name('_e8fkl')
    post_count = int(post_count_tag.text)

    # Click the 'Load More' element
    driver.find_elements_by_class_name('_oidfu')[0].click()

    # Load all the posts into the browser
    processed = 0
    while processed < post_count:
        # Load more content by scrolling to the bottom of the page
        driver.execute_script("window.scrollTo(0, 0);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Download 4 rows of items (4 rows are loaded upon each scroll) and
        # remove them from view
        for _ in itertools.repeat(None, 4):
            urls = fetch_row_links(driver)
            for url in urls:
                download_from_url(url, output_directory,
                                  True, post_count-processed)
                processed += 1
            delete_row(driver)

    driver.close()

if __name__ == "__main__":
    main()
