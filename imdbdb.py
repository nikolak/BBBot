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

import sqlite3, os

defaultdb = 'imdb.sql'

try:
    from imdb import IMDb
except ImportError:
    print 'Warning: IMDbPY not installed!'

def dump_db(dump,db=''):
    if db == '':
        db = defaultdb
    conn = sqlite3.connect(str(db))
    with open(str(dump), 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    return 'database %s dumped to %s file' %(db, dump)

def restore_db(dump,db=''):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    f=open(dump,'r')
    script=''
    for line in f.readlines():
        script+=line
    c.executescript(script)
    print 'Database %s created from %s dump' %(db,dump)
    conn.close()

def create_db(filename=''):
    if filename == '':
        filename = defaultdb
    print 'creating new database'
    conn = sqlite3.connect(str(filename))
    c = conn.cursor()
    c.execute('''create table episodes
                (season text, episode text, name text,
                 summary text, imdburl text)''')
    i = IMDb(accessSystem='mobile')# accessSystem='mobile' should use less bandwidth
    m = i.get_movie('0903747')
    i.update(m, 'episodes')
    print m['episodes']
    for season in m['episodes']:
        for ep in m['episodes'][season]:
            print 'Downloading: ' + 'S:' + str(season) + 'E:' + str(ep) + ' info'
            e = m['episodes'][season][ep]
            i.update(e)
            ep_name = e['title']
            try:
                ep_plot = e['plot'].replace('::garykmcd"]', '').replace('[u"', '').replace('::Anonymous', '').split('u"')[0]
            except:
                ep_plot = 'N\A'
            imdb_url = m['episodes'][season][ep].movieID
            print 'Adding S' + str(season) + 'E' + str(ep) + ' ' + str(ep_name) + ' to the database'
            #add_to_db(str(season), str(ep), str(ep_name), str(ep_plot), str(imdb_url))
            t = (str(season), str(ep), str(ep_name), str(ep_plot), str(imdb_url))
            c.execute('insert into episodes values (?,?,?,?,?)', t)
            conn.commit()

def get_from_db(season, episode, lenght, filename=''):
    if filename == '':
        filename = defaultdb
    conn = sqlite3.connect(str(filename))
    c = conn.cursor()
    if season != '' and episode != '':
        season = str(season)
        episode = str(episode)
        try:
            c.execute('select * from episodes where season=:se and episode=:ep', {"se": season, "ep": episode})
        except:
            return 'IMDbDB module error'
        dbres = c.fetchone()
        #print dbres
        if dbres == None:
            return 'There is no info for season %s episode %s in the database' % (season, episode)
        if int(dbres[0]) < 10:
            season = '0' + dbres[0]
        else:
            season = dbres[0]
        if int(dbres[1]) < 10:
            episode = '0' + dbres[1]
        else:
            episode = dbres[1]
        title = str(dbres[2])
        plot = str(dbres[3])
        url = 'http://www.imdb.com/title/tt' + str(dbres[4])
        if title=='N/A' or url=='http://www.imdb.com/title/ttN/A':
            res='Not enough info about this episode to be displayed.'
        else:
            res = 'S' + season + 'E' + episode + ':' + title + ' | Plot: ' + plot
            res = res[:lenght - 49].strip() + '...Read more: ' + url
        return res

def add_to_db(season, episode, ep_name, ep_plot, imdb_url, filename=''):
    conn = sqlite3.connect(str(filename))
    c = conn.cursor()
    t = (str(season), str(episode), str(ep_name), str(ep_plot), str(imdb_url))
    c.execute('insert into episodes values (?,?,?,?,?)', t)
    conn.commit()

def update_db(seasonin,episodein,filename=''):
    if filename == '':
        filename = defaultdb
    conn = sqlite3.connect(str(filename))
    c = conn.cursor()
    i = IMDb(accessSystem='mobile')# accessSystem='mobile' should use less bandwidth
    m = i.get_movie('0903747')
    i.update(m, 'episodes')
    overwrite = False
    print 'Downloading: ' + 'S:' + str(seasonin) + 'E:' + str(episodein) + ' info'
    e = m['episodes'][seasonin][episodein]
    i.update(e)
    try:#maybe this should go one line up to try and catch exception on i.update(e) ?????
        ep_name = e['title']
    except:
        print 'There is no such episode/season, aborting...'
        return
    try:
        ep_plot = e['plot'].replace('::garykmcd"]', '').replace('[u"', '').replace('::Anonymous', '').split('u"')[0]
    except:
        ep_plot = 'N\A'
    imdb_url = m['episodes'][seasonin][episodein].movieID
    print 'Checking if there are any changes compared to current entry...'
    try:
        c.execute('select * from episodes where season=:se and episode=:ep', {"se": str(seasonin), "ep": str(episodein)})
    except:
        print 'Problem getting season/episode info from database, will update with new info'
        overwrite = True
    dbres = c.fetchone()
    if dbres == None:
        overwrite = True
    else:
        title = str(dbres[2])
        plot = str(dbres[3])
        url = str(dbres[4])
    if title != str(ep_name) or plot != str(ep_plot) or url != str(imdb_url):
        overwrite = True
        print 'There is difference between current and new info, will update.'
    else:
        overwrite = False
    if overwrite:
        print 'Adding S' + str(seasonin) + 'E' + str(episodein) + ' ' + str(ep_name) + ' to the database, overwriting previous entry'
        t = (str(seasonin), str(episodein), str(ep_name), str(ep_plot), str(imdb_url))
        c.execute('insert into episodes values (?,?,?,?,?)', t)
        if dbres != None:
            c.execute("delete from episodes").fetchone()   
            print 'Deleted old entry'       
    c.close()
    
if __name__ == '__main__':
#    restore_db('dump.sql','imdb.sql')
#    dump_db('dump.sql')
    print get_from_db(1, 1, 440)
#    create_db()
#    update_db()
    pass
