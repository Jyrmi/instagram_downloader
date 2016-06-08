# Instagram downloader (need FireFox installed)

### Uses Selenium WebDriver to load content on an Instagram profile

Example usage:

**python bin/run.py pythonpaige**

or

**python bin/run.py https://www.instagram.com/pythonpaige/**

Optional arguments:

⋅⋅* --dest

⋅⋅* --update

⋅⋅* --serialize

You may optionally specify the directory to download to:

**python bin/run.py --dest pics pythonpaige**

or

**python bin/run.py --dest ~/Desktop/instagram_images pythonpaige**

You may also optionally indicate whether to run the downloader in update mode so that it terminates once reaching an already existing file:

**python bin/run.py --update pythonpaige**

You may also optionally indicate whether to serialize the downloaded files. Without the option, file names will be their original web ID's, e.g.

11142783_1577741432494889_787295718_n.jpg

11189805_917626121591623_583183794_n.jpg

11184547_1414354925550367_274565051_n.jpg

etc., but running

**python bin/ run.py --serialize pythonpaige**

will result in file names being followed by their number, i.e.

(1) 11142783_1577741432494889_787295718_n.jpg

(2) 11189805_917626121591623_583183794_n.jpg

(3) 11184547_1414354925550367_274565051_n.jpg

where the earliest posted image is number (1).

##### A simple Tkinter GUI has been added with the intention of packaging the downloader for Windows. If using the GUI, it should be run in the same directory as *run.py* with **python gui.py**.