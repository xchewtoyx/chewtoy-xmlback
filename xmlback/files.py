# Copyright (c) 2012 Russell Heilling
# See LICENSE.txt for license details
import os
import re
import random

SUPPORTED = r'.*\.(jpg|png)$'

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
