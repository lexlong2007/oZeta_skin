#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020
# file for skin oZeta
# <widget render="zParental" source="session.Event_Now" position="315,874" size="50,50" zPosition="3" transparent="1" alphatest="blend"/>
# recode from lululla 2023

from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.config import config
from enigma import ePixmap, eTimer, loadPNG
import json
import re
import os
import sys
curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
pratePath = '/usr/share/enigma2/%s/parental' % curskin
print('patch fsk', pratePath)

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
else:
    pass


def isMountReadonly(mnt):
    mount_point = ''
    with open('/proc/mounts') as f:
        for line in f:
            line = line.split(',')[0]
            line = line.split()
            print('line ', line)
            try:
                device, mount_point, filesystem, flags = line
            except Exception as err:
                print("Error: %s" % err)
            if mount_point == mnt:
                return 'ro' in flags
    return "mount: '%s' doesn't exist" % mnt


path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        path_folder = "/media/mmc/poster"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


REGEX = re.compile(
        r'([\(\[]).*?([\)\]])|'
        r'(: odc.\d+)|'
        r'(\d+: odc.\d+)|'
        r'(\d+ odc.\d+)|(:)|'
        r'( -(.*?).*)|(,)|'
        r'!|'
        r'/.*|'
        r'\|\s[0-9]+\+|'
        r'[0-9]+\+|'
        r'\s\*\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'Премьера\.\s|'
        r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
        r'(х|Х|м|М|т|Т|д|Д)/с\s|'
        r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
        r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
        r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            # # add
            text = text.replace("\xe2\x80\x93", "")  # replace special '-'
            # # add end
            text = re.sub(r"[-,?!/\.\":]", ' ', text)  # replace (- or , or ! or / or . or " or :) by space
            # text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = re.sub('\ \(\d+\)$', '', text)  # remove episode-number " (xxx)" at the end
            text = re.sub('\ \(\d+\/\d+\)$', '', text)  # remove episode-number " (xx/xx)" at the end
            # # add
            # text = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)
            # # text = text.replace(' ^`^s', '').replace(' ^`^y','')
            # text = re.sub('\Teil\d+$', '', text)
            # text = re.sub('\Folge\d+$', '', text)
            # # add end
            text = text.replace('PrimaTv', '').replace(' mag', '')
            text = text.replace(' prima pagina', '')
            # # text = text.replace(' 6', '').replace(' 7', '').replace(' 8', '').replace(' 9', '').replace(' 10', '')
            # # text = text.replace(' 11', '').replace(' 12', '').replace(' 13', '').replace(' 14', '').replace(' 15', '')
            # # text = text.replace(' 16', '').replace(' 17', '').replace(' 18', '').replace(' 19', '').replace(' 20', '')
            text = unicodify(text)
            text = text.capitalize()
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


class zParental(Renderer):

    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        try:
            if not self.instance:
                return
            if what[0] == self.CHANGED_CLEAR:
                if self.instance:
                    self.instance.hide()
            if what[0] != self.CHANGED_CLEAR:
                self.delay()
        except:
            pass

    def showParental(self):
        self.event = self.source.event
        if not self.event:
            return
        fd = "{}\n{}\n{}".format(self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
        try:
            cert = ''
            pattern = ["\d{1,2}\+"]
            for i in pattern:
                age = re.search(i, fd)
                if age:
                    cert = re.sub("\+", "", age.group()).strip()
                else:
                    try:
                        self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')  # .encode('utf-8')
                        if not PY3:
                            self.evnt = self.evnt.encode('utf-8')
                        if self.evnt and self.evnt != 'None' or self.evnt is not None:
                            self.evntNm = convtext(self.evnt)
                            infos_file = "{}/{}".format(path_folder, self.evntNm)
                            if infos_file:
                                with open(infos_file) as f:
                                    age = json.load(f)['Rated']
                                    cert = {
                                            "TV-G": "0",
                                            "G": "0",
                                            "TV-Y7": "6",
                                            "TV-Y": "6",
                                            "TV-10": "10",
                                            "TV-12": "12",
                                            "TV-14": "14",
                                            "TV-PG": "16",
                                            "PG-13": "16",
                                            "PG": "16",
                                            "TV-MA": "18",
                                            "R": "18",
                                            "N/A": "UN",
                                            "Not Rated": "UN",
                                            "Unrated": "UN",
                                            "": "UN",
                                            "Passed": "UN", }.get(age)
                    except:
                        pass
                if cert != '':
                    self.instance.setPixmap(loadPNG(os.path.join(pratePath, "FSK_{}.png".format(cert))))
                    self.instance.show()
                else:
                    if self.instance:
                        self.instance.hide()
        except:
            if self.instance:
                self.instance.hide()

    def delay(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.showParental)
        except:
            self.timer.callback.append(self.showParental)
        self.timer.start(50, True)
