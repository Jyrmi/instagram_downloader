Multiprocessed (wow!) Instagram Downloader - downloads all images/video from an
Instagram profile through Websta. Fast!!


Example usage:


python bin/run.py pythonpaige

or

python bin/run.py https://www.instagram.com/pythonpaige/




You may optionally specify the directory to download to:


python bin/run.py --dest pics pythonpaige

or

python bin/run.py --dest ~/Desktop/instagram_images pythonpaige


The tool is now scraping from websta.me instead of instagram.com due to
extracting media from instagram's main website not being straightforward.
The downloaded items will still be roughly in order, from newest to oldest,
but not perfectly in order due to how the posts are arranged on websta.