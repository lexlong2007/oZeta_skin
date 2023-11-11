#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020, 11.2020, 06.2021
# file by sunriser 07.2021
# <widget source="session.Event_Now" render="zInfoEvents"/>
# <widget source="session.Event_Next" render="zInfoEvents"/>
# <widget source="Event" render="zInfoEvents"/>
# edit by lululla 07.2022
# recode from lululla 2023
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from Components.config import config
from enigma import eLabel
from enigma import eTimer
from enigma import eEPGCache
from time import gmtime
import json
import os
import re
import socket
import sys
import unicodedata
import NavigationInstance
PY3 = sys.version_info.major >= 3

global my_cur_skin, path_folder


try:
    PY3 = True
    unicode = str
    from urllib.parse import quote
    from urllib.request import urlopen
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
except:
    from urllib import quote
    from urllib2 import urlopen
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
epgcache = eEPGCache.getInstance()
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


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


try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if os.path.exists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
except:
    my_cur_skin = False


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
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = re.sub('\ \(\d+\)$', '', text) #remove episode-number " (xxx)" at the end
            text = re.sub('\ \(\d+\/\d+\)$', '', text) #remove episode-number " (xx/xx)" at the end
            text = text.replace('PrimaTv', '').replace(' mag', '')
            # text = text.replace(' 1', '').replace(' 2', '').replace(' 3', '').replace(' 4', '').replace(' 5', '')
            # text = text.replace(' 6', '').replace(' 7', '').replace(' 8', '').replace(' 9', '').replace(' 10', '')
            # text = text.replace(' 11', '').replace(' 12', '').replace(' 13', '').replace(' 14', '').replace(' 15', '')            
            # text = text.replace(' 16', '').replace(' 17', '').replace(' 18', '').replace(' 19', '').replace(' 20', '') 
            text = unicodify(text)
            text = text.lower()
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


def intCheck():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True


class zInfoEvents(Renderer, VariableText):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.text = ""

    GUI_WIDGET = eLabel

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            return self.text
        if what[0] != self.CHANGED_CLEAR:
            self.showInfos()

    def showInfos(self):
        self.event = self.source.event
        if self.event and self.event != 'None' or self.event != None:
            self.delay2()
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            if not PY3:
                self.evnt = self.evnt.encode('utf-8')
            self.evntNm = convtext(self.evnt)
            self.infos_file = "{}/{}".format(path_folder, self.evntNm)
            if not os.path.exists(self.infos_file):
                self.downloadInfos()
            if os.path.exists(self.infos_file):
                try:
                    with open(self.infos_file) as f:
                        data = json.load(f)
                        Title = ''
                        imdbRating = ''
                        Country = ''
                        Year = ''
                        Rated = ''
                        Genre = ''
                        Awards = ''
                        Director = ''
                        Writer = ''
                        Actors = ''
                        if 'Title' in data:
                            Title = data["Title"]
                        if 'imdbrating' in data:
                            imdbRating = data["imdbRating"]
                        if 'country' in data:
                            Country = data["Country"]
                        if 'year' in data:
                            Year = data["Year"]
                        if 'rated' in data:
                            Rated = data["Rated"]
                        if 'genre' in data:
                            Genre = data["Genre"]
                        if 'awards' in data:
                            Awards = data["Awards"]
                        if 'director' in data:
                            Director = data["Director"]
                        if 'writer' in data:
                            Writer = data["Writer"]
                        if 'actors' in data:
                            Actors = data["Actors"]

                        if Title and Title != "N/A":
                            with open("/tmp/rating", "w") as f:
                                f.write("%s\n%s" % (imdbRating, Rated))
                            self.text = "Title: %s" % str(Title)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nYear: %s" % str(Year)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nCountry: %s" % str(Country)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nGenre: %s" % str(Genre)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nDirector: %s" % str(Director)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nAwards: %s" % str(Awards)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nWriter: %s" % str(Writer)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nCast: %s" % str(Actors)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nRated: %s" % str(Rated)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nImdb: %s" % str(imdbRating)  # .encode('utf-8').decode('utf-8')
                            # print("text= ", self.text)
                            if not PY3:
                                self.text = self.text.encode('utf-8')
                            self.text = "Anno: %s\nNazione: %s\nGenere: %s\nRegista: %s\nAttori: %s" % (str(Year), str(Country), str(Genre), str(Director), str(Actors))

                        else:
                            if os.path.exists("/tmp/rating"):
                                os.remove("/tmp/rating")
                                print('/tmp/rating removed')
                        return self.text
                except Exception as e:
                    print(e)
            else:
                return ''

    def downloadInfos(self):
        self.year = self.filterSearch()
        try:
            try:
                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&include_adult=true&query={}".format(self.srch, tmdb_api, quote(self.evntNm))
                if self.year is not None:
                    url_tmdb += "&year={}".format(self.year)
                if PY3:
                    import six
                    url_tmdb = six.ensure_str(url_tmdb)
                try:
                    title = json.load(urlopen(url_tmdb))["results"][0]["title"]
                except:
                    title = json.load(urlopen(url_tmdb))["results"][0]["original_name"]
                print('Title1: ', title)
            except:
                pass
            try:
                url_omdb = "http://www.omdbapi.com/?tmdb_api={}&t={}".format(omdb_api, quote(title))
                data_omdb = json.load(urlopen(url_omdb))
                open(self.infos_file, "w").write(json.dumps(data_omdb))
                OnclearMem()
            except:
                pass
        except Exception as e:
            print('error ', str(e))

    def filterSearch(self):
        try:
            sd = "%s\n%s\n%s" % (self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
            w = [
                    "t/s",
                    "Т/s",
                    "SM",
                    "SM",
                    "d/s",
                    "D/s",
                    "stagione",
                    "Sig.",
                    "episodio",
                    "serie TV",
                    "serie"
                    ]
            for i in w:
                if i in sd:
                    self.srch = "tv"
                    break
                else:
                    self.srch = "multi"
            yr = [_y for _y in re.findall(r'\d{4}', sd) if '1930' <= _y <= '%s' % gmtime().tm_year]
            return '%s' % yr[-1] if yr else None
        except:
            pass

    def epgs(self):
        try:
            events = None
            ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            events = epgcache.lookupEvent(['IBDCT', (ref, 0, -1, -1)])
            for i in range(9):
                titleNxt = events[i][4]
                self.evntNm = convtext(titleNxt)
                self.infos_file = "{}/{}".format(path_folder, self.evntNm)
                if not os.path.exists(self.infos_file):
                    self.downloadInfos()
        except:
            pass

    def delay2(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.dwn)
        except:
            self.timer.callback.append(self.dwn)
        self.timer.start(50, True)

    def dwn(self):
        start_new_thread(self.epgs, ())
