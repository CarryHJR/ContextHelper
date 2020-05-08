#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 carry <carry@CarrHJRs-MBP.local>
#
# Distributed under terms of the MIT license.

"""

"""

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright ¬¨¬© 2020 carry <carry@CarrHJRs-MBP.local>
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
import os


addon_path = os.path.dirname(__file__)


def clip_mp3(file_path):
    try:
        import pydub 
        import numpy as np

        def read(f, normalized=False):
            """MP3 to numpy array"""
            a = pydub.AudioSegment.from_mp3(f)
            y = np.array(a.get_array_of_samples())
            if a.channels == 2:
                y = y.reshape((-1, 2))
            if normalized:
                return a.frame_rate, np.float32(y) / 2**15
            else:
                return a.frame_rate, y
        def write(f, sr, x, normalized=False):
            """numpy array to MP3"""
            channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
            if normalized:  # normalized array - each item should be a float in [-1, 1)
                y = np.int16(x * 2 ** 15)
            else:
                y = np.int16(x)
            song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
            song.export(f, format="mp3", bitrate="320k")
        samplerate, data = read(file_path)
        start = max(np.where(data > 2000)[0][0] - 20000, 0)
        data_new = data[start:]
        write(file_path, samplerate, data_new)
    except Exception as e:
        pass

def transvert_mp3(editor, file_name):
    media_dir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(addon_path)), 'User 1'), 'collection.media')
    file_path = os.path.join(media_dir, file_name)
    clip_mp3(file_path)

    import uuid, json


    template = """<br/>
    <audio id="{1}" src="{0}"></audio>
    <div>
        <button onclick="document.getElementById('{1}').play()">Play</button>
        <button onclick="document.getElementById('{1}').pause()">Pause</button>
        <button onclick="aud = document.getElementById('{1}'); aud.playbackRate = 0.5; aud.currentTime=0; aud.play()">Speed 0.5x</button>
        <button onclick="aud = document.getElementById('{1}'); aud.playbackRate = 1; aud.currentTime=0; aud.play()">Speed 1.0x</button>
        <button onclick="document.getElementById('{1}').volume = 1">Vol max</button> 
        <button onclick="document.getElementById('{1}').volume += 0.1">Vol +</button> 
        <button onclick="document.getElementById('{1}').volume -= 0.1">Vol -</button>
    </div><br/>
    """.format(file_name, uuid.uuid4().hex)
    str = "document.execCommand('insertHTML', false, %s);" % json.dumps(template)
            #  self.web.eval("pasteHTML(%s, %s, %s);" % (
            #  json.dumps(html), json.dumps(internal), extended))

    editor.web.eval(str)
    pass


import logging


#  from aqt.qt import *



def myAddMedia(self, path, canDelete=False):
    transvert_mp3(self, path)
Editor.addMedia = wrap(Editor.addMedia, myAddMedia)




