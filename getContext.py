#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 carry <carry@CarrHJRs-MBP.local>
#
# Distributed under terms of the MIT license.

"""

"""
from anki.hooks import addHook, wrap

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
import anki
from PyQt5 import QtWidgets
from anki.hooks import wrap
from anki.media import MediaManager
from aqt.utils import tooltip, showWarning
from aqt.editor import Editor, EditorWebView


import json
import uuid

addon_path = os.path.dirname(__file__)

from bs4 import BeautifulSoup
import requests

#  import .audioChange.clip_mp3 as clip_mp3
from .audioChange import clip_mp3


def get_renren(word):
    url = 'http://www.91dict.com/words?w=' + word
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, features="html.parser")
    tmp = soup.find_all(id="flexslider_2")[0].find_all("ul")[0].find_all("li")
    s = ""
    for i,x in enumerate(tmp) :
        imgMainbox = x.find(class_="imgMainbox")
        image_url = imgMainbox.find("img")["src"]
        audio_url = imgMainbox.find("audio")["src"]
        sentence = imgMainbox.find(class_="mBottom").text.strip()
        if image_url:
            template = """
            <div contenteditable="true"><table border="0" width="100%" cellpadding="0" cellspacing="0"><tbody><tr><td style="text-align: center;"> 
            <audio id="{3}" src="{0}"></audio>
            <div>
                <button onclick="document.getElementById('{3}').play()">Play</button>
                <button onclick="document.getElementById('{3}').pause()">Pause</button>
                <button onclick="aud = document.getElementById('{3}'); aud.playbackRate = 0.5; aud.currentTime=0; aud.play()">Speed 0.5x</button>
                <button onclick="aud = document.getElementById('{3}'); aud.playbackRate = 1; aud.currentTime=0; aud.play()">Speed 1.0x</button>
                <button onclick="document.getElementById('{3}').volume = 1">Vol max</button> 
                <button onclick="document.getElementById('{3}').volume += 0.2">Vol +</button> 
                <button onclick="document.getElementById('{3}').volume -= 0.2">Vol -</button>
            </div>
            </td></tr><tr><td style="text-align: center;">&nbsp;&nbsp;{1}</td></tr><tr><td style="text-align: center;">&nbsp;<img src="{2}" width="200"></td></tr></tbody></table></div>
            """.format(audio_url, sentence, image_url, uuid.uuid4().hex) + "<br/>"
            s = s+template
    return s


def transvert_mp3(editor, url):
    file_name = url[1:-1].split(':')[1]

    media_dir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(addon_path)), 'User 1'), 'collection.media')
    file_path = os.path.join(media_dir, file_name)

    clip_mp3(file_path)



    template = url+"""<br/>
    <audio id="{1}" src="{0}"></audio>
    <div>
        <button onclick="document.getElementById('{1}').play()">Play</button>
        <button onclick="document.getElementById('{1}').pause()">Pause</button>
        <button onclick="aud = document.getElementById('{1}'); aud.playbackRate = 0.5; aud.currentTime=0; aud.play()">Speed 0.5x</button>
        <button onclick="aud = document.getElementById('{1}'); aud.playbackRate = 1; aud.currentTime=0; aud.play()">Speed 1.0x</button>
        <button onclick="document.getElementById('{1}').volume = 1">Vol max</button> 
        <button onclick="document.getElementById('{1}').volume += 0.2">Vol +</button> 
        <button onclick="document.getElementById('{1}').volume -= 0.2">Vol -</button>
    </div><br>
    """.format(file_name, uuid.uuid4().hex)
    str = "document.execCommand('insertHTML', false, %s);" % json.dumps(template)
            #  self.web.eval("pasteHTML(%s, %s, %s);" % (
            #  json.dumps(html), json.dumps(internal), extended))

    editor.web.eval(str)
    pass


def get_oxford(word):
    url = "https://www.lexico.com/definition/" + word
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, features="html.parser")
    sembs = soup.findAll("section", class_="gramb")
    oxford = ""
    for semb in sembs:
        items = semb.ul.findAll("li", recursive=False)
        title = semb.h3.text
        li= ""
        for i in range(len(items)):
            try: 
                definition = items[i].div.p.find(class_="ind").text
            except Exception as e:
                definition = ""
            try: 
                exg = items[i].div.find(class_="exg").em.text
            except Exception as e:
                exg = ""
            if items[i].find(class_="subSenses"):
                items_sub = items[i].find(class_="subSenses").findAll("li", recursive=False)
            else:
                items_sub = []
            html_sub = ""
            for j in range(len(items_sub)):
                definition_sub = items_sub[j].find(class_="ind").text
                if items_sub[j].find(class_="exg", recursive=False): 
                    exg_sub = items_sub[j].find(class_="exg", recursive=False).text 
                else: 
                    exg_sub =  ""
                html_sub = html_sub + """<li><div>{0}</div><div>{1}</div></li>""".format(definition_sub, exg_sub)
            if len(html_sub) > 0:
                html = """<li><div>{0}</div><div>{1}</div></li><ol>{2}</ol>""".format(definition, exg, html_sub)
            else:
                html = """<li><div>{0}</div><div>{1}</div></li>""".format(definition, exg)
            li = li+html
            
        oxford_sub = """<details>
  <summary><em>{0}</em></summary>
  <div style="font-size: 8px"><ul>{1}</ul></div></details>""".format(title, li)
        oxford = oxford + oxford_sub
    return oxford


def get_dict_html(editor, word):
    html_oxford = get_oxford(word)
    html_renren = get_renren(word)
    str = "document.execCommand('insertHTML', false, %s);" % json.dumps(word + "<br/><br/>" + html_oxford + html_renren + "<br>")
    editor.web.eval(str)

def toggle_dict(editor):
    selection = editor.web.selectedText()
    if selection.startswith('[') and selection.endswith(']'):
        transvert_mp3(editor, selection)
    else:
        get_dict_html(editor, selection)


def toggle_dict_test(editor):
    selection = editor.web.selectedText()
    print(selection)
    html = """
    <div contenteditable="true" style="width:100%; height:100%;" class="w-e-text" id="text-elem40419199085002266"><table border="0" width="100%" cellpadding="0" cellspacing="0"><tbody><tr><th><audio controls="">
  <source src="https://mp3.91dict.com/mp32/9854930345aaf869383c471028d004e5/92.mp3?auth_key=1587168000-0-0-039c315f4e0e88e3c46119ea0bc2ca5e" type="audio/mpeg">
</audio><p>&nbsp;<em>Test</em>&nbsp;results? I don't have&nbsp;<em>test</em>&nbsp;results. I'm a virgin.<br> <img src="https://img.91dict.com/img2/9854930345aaf869383c471028d004e5/92.jpg?x-oss-process=image/resize,m_fill,h_494,w_800&amp;auth_key=1587168000-0-0-2ab8a91e849993c7f1e4b623c1a3d00c" height="250" width="400"><br></p>&nbsp;</th></tr></tbody></table><p><br></p></div>
    """
    str = "document.execCommand('insertHTML', false, %s);" % json.dumps(html)
    editor.web.eval(str)

def setupEditorButtonsFilter(buttons, editor):
    #  key = QKeySequence(gc('Key_insert_table'))
    #  keyStr = key.toString(QKeySequence.NativeText)
    #  if gc('Key_insert_table'):
    b = editor.addButton(
            os.path.join(addon_path, "icons", "renren.png"),
            "tablebutton",
            toggle_dict
            #  toggle_table,
            #  tip="Insert table ({})".format(keyStr),
            #  keys=gc('Key_insert_table')
            )
    buttons.append(b)
    return buttons
addHook("setupEditorButtons", setupEditorButtonsFilter)

