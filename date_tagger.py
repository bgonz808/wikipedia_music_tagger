#!/usr/bin/env python
# Robert J Gonzales
# 2015 April 30

# Currently supports .mp3 (ID3 tags)
#  - Add support for .m4a .mp4
#  - Add support for .flac
# Implement Log File
#  - Bad Queries
#  - Number of songs updated/failed
# Support filenames containing Unicode (see error below)
"""
/usr/lib/python2.7/urllib.py:1268: UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
  return ''.join(map(quoter, s))
Traceback (most recent call last):
  File "./media_year_fix.py", line 129, in <module>
    print USAGE
  File "./media_year_fix.py", line 117, in main
    for fname in list_fh:
  File "./media_year_fix.py", line 98, in updateYear
    audio["TDRC"] = TDRC(3, [ts])
  File "./media_year_fix.py", line 26, in getDateFromWikipedia
    opener = urllib2.build_opener()
  File "/usr/lib/python2.7/urllib.py", line 1268, in quote
    return ''.join(map(quoter, s))
KeyError: u'\xeb'

"""

from datetime import datetime
import os
import re
import sys
import urllib2
from mutagen.id3 import ID3, TDRC, TALB, TPE1, ID3TimeStamp
from mutagen.flac import FLAC
import mutagen.mp4

USAGE = "USAGE: Pass in a list of media files"
MONTH_NUMS = {"jan":"01", "feb":"02", "mar":"03", "apr":"04", "may":"05", "jun":"06", "jul":"07", "aug":"08", "sep":"09", "oct":"10", "nov":"11", "dec":"12"}
DATE_FMT = ["%B %d %Y","%d %B %Y","%b %d %Y","%d %b %Y","%B %Y","%b %Y","%Y"]
BASE_URL = "http://en.wikipedia.org/wiki/"
PREV_RESULT = {"TALB":None, "TPE1":None, "TDRC":None}

def getDateFromWikipedia(artist, album):
    artist = artist[0]
    album  = album[0]
    # Generate URLs based on artist and title
    opener = urllib2.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    # Guess many possible URLs for Wikipedia Album page
    url_list = [urllib2.quote(album + " (" + artist + " album)"),
                urllib2.quote(album),
                urllib2.quote(album.lower() + " (" + artist.lower() + " album)"),
                urllib2.quote(album.lower()),
                urllib2.quote(album.lower() + " (" + artist + " album)"),
                urllib2.quote(album + " (" + artist.lower() + " album)"),
                urllib2.quote((album) + " (album)"),
                urllib2.quote((album.lower()) + " (album)")]
    infile = None
    for url in url_list:
        full_url = BASE_URL + url
        try:
            infile = opener.open(full_url)
            print "\t-I- Found at \"..."+url+"\""
            # Try to find the correct page
            artistFoundInPage = None
            for this_line in infile:
                if artistFoundInPage is None:
                    match_artist = re.search(artist, this_line, re.IGNORECASE)
                    if match_artist is not None:
                        artistFoundInPage = "yes"
                match_date = re.search('class=\"published\"[^>]*>(.+)<\/td>', this_line)
                if (match_date is not None) and (artistFoundInPage is not None):
                    date = match_date.group(1).lower()
                    date = date.replace(',', "").replace("th","").replace("rd","").replace("nd","").replace("st","").replace("</a>","").rstrip(' ')
                    date = re.sub("<a href.+>", "", date)
                    for fmt in DATE_FMT:
                        DTObj = None
                        try:
                            DTObj = datetime.strptime(date, fmt)
                        except ValueError:
                            print "\t\t-W- DATE=\""+date+"\" couldn't be read as FMT=\""+fmt+"\""
                            continue
                        if DTObj is None:
                            print "\t\t-E- No suitable date found"
                            continue
                        date_tag = DTObj.strftime("%Y-%m-%d 00:00:00")
                        print "\t\t-I- Using timestamp \""+date_tag+"\""
                        return date_tag
                    print "\t\t-E- Date can't be interpreted \""+match_date.group(0)+"\""
                    print "\t\t    OR page had date but was irrelevant."
            print "\t-W- No \"published date\" found on page \"..."+url+"\""
        except urllib2.HTTPError:
            print "\t-W- Not found at \"..."+url+"\""
    if infile is None:
        print "\t-E- Skipping file, no wiki page found"
        # TODO: add files w.o. matches to a log
        return None
    else:
        print "\t-E- No \"published date\" found on any page"
        return None

def updateYear(fname):
    _, ext = os.path.splitext(fname)
    ext = ext.lower()
    if ext == ".flac": # not supported yet
        return
    if ext == ".mp4": # not supported yet
        return
    if ext == ".m4a": # not supported yet
        return
    if ext == ".mp3":
        audio = ID3(fname)
        album = audio["TALB"]
        artist = audio["TPE1"]
        print album, artist
        # Prevent duplicate searches for same artist+albumtitle combo. Store last result.
        # TODO: store queries in a hash, but for now last result is good enough with
        # searches grouped by album as would be expected in a folder hierarchy.
        if (PREV_RESULT["TALB"] == album) and (PREV_RESULT["TPE1"] == artist):
            if PREV_RESULT["TDRC"] is None:
                return 1
            ts = ID3TimeStamp(PREV_RESULT["TDRC"])
            audio["TDRC"] = TDRC(3, [ts])
            audio.save()
            return 0
        date_tag = getDateFromWikipedia(artist, album)
        if date_tag == None:
            PREV_RESULT["TDRC"] = None
            return 1
        PREV_RESULT["TALB"] = album
        PREV_RESULT["TPE1"] = artist
        PREV_RESULT["TDRC"] = date_tag
        ts = ID3TimeStamp(date_tag)
        audio["TDRC"] = TDRC(3, [ts])
        audio.save()
        return 0

def main():
    try:
        list_fh = file(sys.argv[1])
        num = 1
        for fname in list_fh:
            fname = fname.rstrip('\n')
            print "File ",num, "\t", fname
            updateYear(fname)
            num += 1
        list_fh.close()
    except IOError:
        print "-E- specify a list of mp3s"

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print USAGE
            sys.exit(1)
        else:
            main()
            sys.exit(0)
    except (KeyboardInterrupt, SystemExit):
        print "Charlie!! He bit mee."
        sys.exit(2)
