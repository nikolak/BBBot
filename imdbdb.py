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
#       

import sqlite3
try:
    from imdb import IMDb
except ImportError:
    print 'Warning: IMDbPY not installed!'
conn = sqlite3.connect('imdb.sql')
c = conn.cursor()

def create_db():
    c = conn.cursor()
    c.execute('''create table episodes
                (season text, episode text, name text,
                 summary text, imdburl text)''')
    return 'Database created'

def get_from_db(season,episode):
    episode=str(episode)
    season=str(season)
    if season!='' and episode!='':#get by season,episode
        try:
            c.execute('select * from episodes where season=?', season)
        except:
            return 'IMDbDB module error, no such season and or episode?'
        for row in c:
            if row[1]==episode:
                res=row
                season=''
                episode=''
                title=''
                plot=''
                url=''
                if int(row[0])<10:
                    season='0'+row[0]
                else:
                    season=row[0]
                if int(row[1])<10:
                    episode='0'+row[1]
                else:
                    episode=row[1]
                title=str(row[2])
                plot=str(row[3]).replace('::garykmcd"]','').replace('[u"','').split('u"')[0]
                url='http://www.imdb.com/title/tt'+str(row[4])
                return 'S'+season+'E'+episode+':'+title+' : '+url+' | Plot: '+ plot

def add_to_db(season,episode,ep_name,ep_plot,imdb_url):
    t=(str(season),str(episode),str(ep_name),str(ep_plot),str(imdb_url))
    c.execute('insert into episodes values (?,?,?,?,?)',t)
    conn.commit()#needs to be here?

def update_db():
    i = IMDb(accessSystem='mobile')
    m = i.get_movie('0903747')
    i.update(m, 'episodes')

    print m['episodes']
    for season in m['episodes']:
        for ep in m['episodes'][season]:
            print 'Downloading: '+'S:'+str(season)+'E:'+str(ep)
            e=m['episodes'][season][ep]
            i.update(e)
            ep_name=e['title']
            ep_plot=e['plot']
            imdb_url=m['episodes'][season][ep].movieID
            add_to_db(str(season),str(ep),str(ep_name),str(ep_plot),str(imdb_url))
            print 'S'+str(season)+'E'+str(ep)+' Added to database'
    c.close()
if __name__ == '__main__':
#    create_db()
#    update_db()
    pass