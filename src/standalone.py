#!/usr/bin/python

import os
import subprocess
from Tkinter import Tk
from Tkinter import Label
from Tkinter import Entry
from Tkinter import Button
from Tkinter import StringVar
from Tkinter import N, S, E, W
import tkFileDialog

import sys
import re
import itertools
from time import sleep
from urllib2 import urlopen
from getopt import getopt
from selenium.webdriver import Chrome # pip install selenium


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
        exit(0)


def count_items(driver):
    """
    Counts the number of media items that appears on the profile.
    """
    items = driver.find_elements_by_class_name('_22yr2')

    return len(items)

def select_directory_callback():
    download_directory = tkFileDialog.askdirectory()
    if download_directory:
        E_path_text.set(download_directory)

def set_default_directory():
    E_path_text.set(os.getcwd()+'/'+E_username.get())
    def cancel(event):
        top.after_cancel(path_update_id)
    B_path_select.bind("<Button-1>", cancel)
    E_path.bind("<Button-1>", cancel)
    path_update_id = top.after(100, set_default_directory)

def start_callback():

    """
    Main loop of the scrape.
    """
    profile_username = E_username.get() # The Instagram username of the profile from which we
    # are downloading. Must be supplied.
    output_directory = E_path.get() # Will be initialized with the optional argument or a
    # default later.
    update_mode = True
    serialize = True
    latest_image = ''

    # If the output directory doesn't exist, create it.
    output_directory = profile_username
    if not os.path.exists(profile_username):
        os.makedirs(profile_username)

    # The latest downloaded images will be the first in the directory.
    files = os.listdir(output_directory)
    if files:
        latest_image = files[0]

    # Start the browser
    driver = Chrome(executable_path='../bin/chromedriver')
    driver.get(insta_url + profile_username)

    # Find the number of posts on this Instagram profile
    post_count_tag_xpath = ('//*[@id="react-root"]/section/main/'
                            + 'article/header/div[2]/ul/li[1]/span/span')
    post_count_tag = driver.find_element_by_xpath(post_count_tag_xpath)
    post_count = int(post_count_tag.text)

    # If the target profile is private, then redirect to the login page
    login_tag_xpath = '//*[@id="react-root"]/section/main/article/div/p/a'
    try:
        login_tag = driver.find_element_by_xpath(login_tag_xpath)
        login_page_url = login_tag.get_attribute('href')
        driver.get(login_page_url)

        # Wait for the user to login
        while driver.current_url == login_page_url:
            sleep(1)

        # Return to the target profile from the homepage
        driver.get(insta_url + profile_username)
    except:
        pass

    # Click the 'Load More' element
    driver.find_element_by_class_name('_oidfu').click()

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
            delete_row(driver)
            for url in urls:

                # Exit if we've reached the latest image that was in the
                # directory before downloading. This means the directory has
                # everything beyond this point.
                if update_mode:
                    fname = file_name.search(url).group(0)
                    if fname in latest_image:
                        exit(0)

                download_from_url(url, output_directory,
                                  serialize, post_count-processed)
                processed += 1

    driver.close()


top = Tk()
top.title('Instagram Downloader')
top.update_idletasks()


# Username or url label and entry box
L_username = Label(top, text="Username or url")
L_username.grid(row=0, column=0, sticky=N+S+E+W)

E_username_text = StringVar()
E_username = Entry(top, bd=2, textvariable=E_username_text)
E_username.grid(row=0, column=1, columnspan=2, sticky=N+S+E+W)


# Download path label, file browser button, and download path entry box
L_path = Label(top, text="Download path")
L_path.grid(row=1, column=0, sticky=N+S+E+W)

B_path_select = Button(top, text="...", command=select_directory_callback)
B_path_select.grid(row=1, column=1, sticky=N+S+E+W)

E_path_text = StringVar()
E_path_text.set(os.getcwd()+'/')
E_path = Entry(top, bd=2, textvariable=E_path_text)
E_path.grid(row=1, column=2)


# Start button
# L_downloads = Label(top, text='Downloaded:')
# L_downloads.grid(row=2, column=0)

# L_downloads = Label(top, text='0')
# L_downloads.grid(row=2, column=1)

B_start = Button(top, text="Go", command=start_callback)
# B_start.grid(row=2, column=2, sticky=N+S+E+W)
B_start.grid(row=2, column=0, columnspan=3, sticky=N+S+E+W)


# # Stdout from the run.py subprocess
# T_stdout = Text(top)
# T_stdout.grid(row=4, column=0, columnspan=3, sticky=N+S+E+W)


# Main loop
path_update_id = top.after(100, set_default_directory)
top.mainloop()