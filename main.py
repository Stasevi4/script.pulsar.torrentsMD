import xbmcaddon
import re
import xbmcgui
from pulsar import provider
from pulsar.util import notify
from pulsar.logger import log

__addon__ = xbmcaddon.Addon(id='script.pulsar.TorrentsMD')
__key__ = __addon__.getSetting("key")
__quality__ = __addon__.getSetting("quality")
__language__ = __addon__.getSetting("language")


def getkey():

  user = __addon__.getSetting("user")
  password = __addon__.getSetting("password")

  postData = {'username': user, 'password' : password, 'autologin' : '1'}
  response = provider.POST("http://torrentsmd.com/takelogin.php", postData)
  if response.data.find('user_box') > 0:

    response = provider.GET("http://torrentsmd.com/browse.php")
    data = response.data.decode("utf-8")
    for key in re.findall(r'rss\.php\?key=[^\'"\s<>\[\]]+', data):
        notify("Successfully logged in", "User: " + user.encode("utf8") , 10000,  __addon__.getAddonInfo('icon'))
	__addon__.setSetting(id='key', value=key.replace('rss.php?key=',''))
        return key.replace('rss.php?key=','')
  else:
        notify("", "Login failed " + user.encode("utf8") ,10000)
	__addon__.setSetting(id='key', value="")


def getsettings():
    quality = {"ALL" : "", "DVDRip" : "103","DVD" : "115","HDTV" : "111","HDTVRip" :"128"}[__quality__]
    language = {"ALL" : "", "Russian":"28","English":"180"}[__language__]

    return ','.join([quality,language])

def search(query):
    global __key__
    if len(__key__)< 1: 
      __addon__.openSettings()
      __key__ = getkey()
      
    params = {"key": __key__}

    if "imdb_id" in query:
         params["imdb"] = query['imdb_id'].replace("tt","")

    if "season" in query:
        params["search_str"] = "%(title)s [Season %(season)2d/Episode%(episode)2d]" % query

    if getsettings() != ",":
        params['categtags'] = getsettings()

    if "title" in query:
        title = query["title"]
    else:
        title = query
        params["search_str"] = query.encode("utf8")

    response = provider.GET("http://torrentsmd.com/rss.php", params)
    notify("Total files:" + str(len(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', response.data))), title.encode("utf8") ,10000, __addon__.getAddonInfo('icon'))
    return provider.extract_magnets(response.data)

def search_movie(movie):
    return search(movie)

def search_episode(episode):
    return search(episode)

provider.register(search, search_movie, search_episode)
