#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#       
#       Copyright (c) 2012 Nikola Kovacevic <nikolak@outlook.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from time import gmtime, strftime
from datetime import datetime
import shelve
import googl

db = shelve.open('database.db')
api_key = db['api_key']
if api_key != '':
    client=googl.Googl(api_key)
admin=db['admin']
password=db['password']
banned=db['banned']
admin=db['admin']
auth=db['auth']
initialch=db['initialch']
cc=db['cc']
airtimes=['06.08:02:00:00','13.08:02:00:00','20.08:02:00:00','27.08:02:00:00','03.09:02:00:00']#GMT dd.mm

def getairtime():
    t1 = strftime('%d.%m:%H:%M:%S', gmtime())#current date/time GMT
    ctime=datetime.strptime(t1,'%d.%m:%H:%M:%S')
    for t in airtimes:
        try:
            airtime=datetime.strptime(t,'%d.%m:%H:%M:%S')
            if ctime<=airtime:
                return t
        except ValueError:
            return 'error'
    else:
        return 'error'

def getepisode():
    airtime=getairtime()
    if airtime=='error':
        return 'N/A'
    episodes={'06.08:02:00:00':'Breaking Bad: Season 5, Episode 4 "Fifty-One" (5 Aug. 2012)',
              '13.08:02:00:00':'Breaking Bad: Season 5, Episode 5 "Dead Freight" (12 Aug. 2012)',
              '20.08:02:00:00':'Breaking Bad: Season 5, Episode 6 "Buyout" (19 Aug. 2012)',
              '27.08:02:00:00':'Breaking Bad: Season 5, Episode 7 "Say My Name" (26 Aug. 2012)',
              '03.09:02:00:00':'Breaking Bad: Season 5, Episode 8 "Gliding Over All" (2 Sep. 2012)'
              }
    try:
        return episodes[airtime]
    except KeyError:
        return 'N/A'

def timediff():
    airtime=getairtime()
    if airtime=='error':
        return 'N/A'
    ctime = strftime('%d.%m:%H:%M:%S', gmtime())
    t1=datetime.strptime(ctime,'%d.%m:%H:%M:%S')
    t2=datetime.strptime(airtime,'%d.%m:%H:%M:%S')
    sec = t2-t1
    d = datetime(1,1,1) +sec

    return ("%d days %d hours %d minutes %d seconds" % (d.day-1, d.hour, d.minute, d.second))


def shorten(value):
    try:
        result = client.shorten(str(value.strip()))
        return result['id']
    except googl.GooglError as e:
        return str(e)


def addremove(kind,what,value):
    error='Error adding %s | Usage .<add/remove> <sstream/stream/download> <link>'
    if what=='stream':
        if value=='':
            return error%('URL')
        try:
            tmp=db['streamlinks']
            if kind=='add':
                tmp.append(value)
                message='Link: '+value+' successfully added to stream list!'
            if kind=='remove':
                if value=='clear_all':
                    tmp=['']
                    message='Everything removed!'
                else:
                    tmp.remove(value)
                    message='Link: '+value+' successfully removed from stream list!'
            if kind not in ['add','remove']:
                return error%('stream')
            db['streamlinks']=tmp
            db.sync()
            return message
        except ValueError:
            return error%('or removing stream, database error.')
        
    if what=='sstream':
        if api_key=='':
            return 'goo.gl api key not entered'
        if value=='':
            return error%('URL')
        try:
            tmp=db['streamlinks']
            if kind=='add':
                if len(value.split())>1:
                    print value.split()
                    return 'when using sstream only url is allowed, no addditional text'
                svalue=shorten(value)
                if not svalue.startswith('http://'):
                    return 'Errror: '+svalue
                tmp.append(svalue)
                message='Link: '+value+' successfully shortened to '+svalue+' and added to stream list!'
            if kind=='remove':
                message='Use .remove stream <shortened link> to remove it from the list.'
            if kind not in ['add','remove']:
                return error%('stream')
            db['streamlinks']=tmp
            db.sync()
            return message
        except ValueError:
            return error%('or removing stream, database error.')

    if what=='download':
        if value=='':
            return error%('download URL')
        try:
            tmp=db['downloadlinks']
            if kind=='add':
                tmp.append(value)
                message='Link: '+value+' successfully added to download list!'
            if kind=='remove':
                tmp.remove(value)
                message='Link: '+value+' successfully removed from download list!'
            if kind not in ['add','remove']:
                return error%('download link')
            db['downloadlinks']=tmp
            db.sync()
            return message
        except ValueError:
            return error%('or removing stream, database error.')
    if what not in ['stream','download']:
        return error%('or removing links.')
        

def info():
    try:
        reddit=db['reddit']
    except ValueError:
        reddit='N/A'
    return 'Next episode: '+getepisode()+' | Airs in '+timediff()+' | Latest reddit discussion thread '+reddit

def updatethread(url):
    db['reddit']=url
    db.sync()
    return 'New reddit lnk/thread: '+url
    
def download():
    try:
        links=db['downloadlinks']
    except KeyError:
        return 'error'
    string='%s' % ' '.join(map(str, links))
    if string.strip()=='':
        return 'There are no download links to display currently!'
    return 'Download links: '+string

def stream():
    try:
        links=db['streamlinks']
    except KeyError:
        return 'error'
    string='%s' % ' '.join(map(str, links))
    if string.strip()=='':
        return 'There are no stream links to display currently! '
    return 'Stream links: '+string

#if __name__ == '__main__':
#    pass
