#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright ¬© 2020 carry <carry@CarrHJRs-MBP.local>
#
# Distributed under terms of the MIT license.

"""

"""
from anki.hooks import addHook, wrap

from aqt import mw, editor
from aqt.utils import showInfo
from aqt.qt import *
import anki
from PyQt5 import QtWidgets
from anki.hooks import wrap
from anki.media import MediaManager
from aqt.utils import tooltip, showWarning
from aqt.editor import Editor, EditorWebView



addon_path = os.path.dirname(__file__)



import logging
logger = logging.getLogger(__name__)
logFile = os.path.join(addon_path, 'local.log')
open(logFile, 'w').close()
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(logFile)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
#  consoleHandler = logging.StreamHandler()
#  consoleHandler.setFormatter(logFormatter)
#  logger.addHandler(consoleHandler)


#  from aqt.qt import *


def _processMime_around(self, mime, _old):
    """I found that anki dealt with html, urls, text first before dealing with image,
    I didn't find any advantages of it. If the user wants to copy an image from the web broweser,
    it will make anki fetch the image again, which is a waste of time. the function will try to deal with image data first if mime contains it.contains

    This function is always called when pasting!"""

    # "Paste when resizing"
    #  if Setup.config['auto'] is False:
    #      logger.debug("Setup.config['auto'] is False, run the original _processMime directly")
    #      return _old(self, mime)
    #  logger.debug('grabbing MIME data: found formats {}'.format(mime.formats()))

    logger.debug('grabbing MIME data: found formats {}'.format(mime.formats()))
    logger.debug('hasImage: {}'.format(mime.hasImage()))
    logger.debug('hasUrls: {}'.format(mime.hasUrls()))

    if mime.hasImage():

        # Resize the image, then pass to Anki
        #  print('found image in mime data: getting the resized QImage...')
        im = mime.imageData()
        im = im.scaledToWidth(200, Qt.FastTransformation)
        path = os.path.join(addon_path, 'tmp.png')
        im.save(path, None, 80)

        import requests
        r = requests.post("https://sm.ms/api/v2/upload", files={'smfile': open(path, 'rb')})
        import json

        if json.loads(json.dumps(r.json()))['code'] == 'image_repeated':
            url = json.loads(json.dumps(r.json()))['images']
        else:
            url = json.loads(json.dumps(r.json()))['data']['url']

        html = """
        <img src="{0}" width="200" style="display: block; margin-left: auto; margin-right: auto; width: 200px"><br/>
        """.format(url)

        #  mime = QMimeData()
        #  im = resize(mime.imageData())
        mime = QMimeData()
        import json
        str = "document.execCommand('insertHTML', false, %s);" % json.dumps(html)
        self.editor.web.eval(str)


#          html = """<div contenteditable="true"><table border="0" width="100%" cellpadding="0" cellspacing="0"><tbody><tr><th><audio controls="">
#    <source src="https://mp3.91dict.com/mp32/9854930345aaf869383c471028d004e5/92.mp3?auth_key=1587168000-0-0-039c315f4e0e88e3c46119ea0bc2ca5e" type="audio/mpeg">
#  </audio><p>&nbsp;<em>Test</em>&nbsp;results? I don't have&nbsp;<em>test</em>&nbsp;results. I'm a virgin.<br> <img src="https://img.91dict.com/img2/9854930345aaf869383c471028d004e5/92.jpg?x-oss-process=image/resize,m_fill,h_494,w_800&amp;auth_key=1587168000-0-0-2ab8a91e849993c7f1e4b623c1a3d00c" width="400"><br></p>&nbsp;</th></tr></tbody></table><p><br></p></div>
#  """
        #  mime.setHtml(html)
        #  mime.setImageData(im)

        #  mime.clear()
        logger.debug('clear successfully')
        #  mime = self.editor.imageResizer(paste = False, mime = mime)
        #
        logger.debug('let anki handle the resized image')
        return _old(self, mime)
    # return self._processImage(mime)
    logger.debug("image data isn't detected, run the old _processMime function")
    return _old(self, mime)

EditorWebView._processMime = wrap(EditorWebView._processMime, _processMime_around, 'around')



