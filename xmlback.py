#!/usr/bin/python
# Copyright (c) 2012 Russell Heilling
# See LICENSE.txt for license details
import os
import sys
import re
import xml.dom.minidom
import time
import random

SUPPORTED = r'.*\.(jpg|png)$'

TIME_PART = {
    'year': 'tm_year',
    'month': 'tm_mon',
    'day': 'tm_mday',
    'hour': 'tm_hour',
    'minute': 'tm_min',
    'second': 'tm_sec',
}

class Background(object):
    """
    Uses xml.dom.minidom to build an XML transitions file for GNOME
    """
    def __init__(self):
        self.doc = xml.dom.minidom.Document()
        self.root = self.doc.createElement("background")
        self.root.appendChild(self.start_time())

    def text_elem(self, name, text):
        """
        helper function to simplify the creation of text nodes.
        """
        elem = self.doc.createElement(name)
        text = self.doc.createTextNode(str(text))
        elem.appendChild(text)
        return elem

    def add_image(self, filename, duration=895):
        """
        Add a new static image to the list of backgrounds.
        Default transition period of 895 seconds (i.e. 15 minutes if you
        include transition time)
        """
        static = self.doc.createElement("static")
        static.appendChild(self.text_elem("duration", str(duration)))
        static.appendChild(self.text_elem("file", filename))
        self.root.appendChild(static)
                          
    def add_transition(self, fromfile, tofile, duration=5):
        """
        Add a transition between pairs of background images
        """
        assert fromfile != tofile
        transition = self.doc.createElement("transition")
        transition.appendChild(self.text_elem("duration", str(duration)))
        transition.appendChild(self.text_elem("from", fromfile))
        transition.appendChild(self.text_elem("to", tofile))
        self.root.appendChild(transition)

    def start_time(self):
        """
        Create the starttime element using the current UTC time
        """
        start = time.gmtime()
        start_elem = self.doc.createElement("starttime")
        for name, part in TIME_PART.items():
            time_elem = self.text_elem(name, getattr(start, part))
            start_elem.appendChild(time_elem)
        return start_elem

    def toxml(self):
        """
        Convert the minidom object to textual XML representation
        """
        return self.root.toprettyxml(indent='  ')

def image_files(path, shuffle=False):
    """
    Return a list of supported image files in the chosen directory

    Paths are normalised and made absolute enabling the images and xml
    file to be stored in different locations without problems.
    """
    assert os.path.isdir(path)
    supported = re.compile(SUPPORTED)
    images = []
    for filename in os.listdir(path):
        if supported.match(filename):
            images.append(os.path.realpath(os.path.join(path, filename)))
    if shuffle:
        random.shuffle(images)
    return images

def transitions(path, shuffle=False):
    """
    List the files in the target path and iterate over the pairs,
    returning a link back to the start on completion. 
    """
    images = image_files(path, shuffle)
    fromfile = None
    for tofile in images:
        if fromfile:
            yield (fromfile, tofile)
        fromfile = tofile
    if images:
        if len(images)==1:
            yield(images[0], None)
        else:
            yield(fromfile, images[0])
        
def main(path='.', dest='-', duration=900, transition=2):
    """
    take a path and list all of the supported image types out to XML
    format suitable for use as a gnome background.

    path defaults to current directory, destination file defaults to
    stdout. 

    You cannot enable this background file from the Gnome 3 GUI at the
    current time (2012-04-19, so the following shell command will be
    required: 

    gsettings set org.gnome.desktop.background picture-uri \
              'file:///path/to/background.xml'
    """
    if dest == '-':
        outfile = sys.stdout
    else:
        outfile = open(dest, "w")

    background = Background()
    for (fromfile, tofile) in transitions(path, shuffle=True):
        background.add_image(fromfile, int(duration)-int(transition))
        if tofile:
            background.add_transition(fromfile, tofile, transition)
    outfile.write(background.toxml())

if __name__ == "__main__":
    if len(sys.argv) > 5:
        sys.stderr.write("Usage: xmlback.py [imgdir [outfile.xml]]")
        sys.exit(0)
    main(*sys.argv[1:])
