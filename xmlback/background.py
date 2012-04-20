# Copyright (c) 2012 Russell Heilling
# See LICENSE.txt for license details
import xml.dom.minidom
import time

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
