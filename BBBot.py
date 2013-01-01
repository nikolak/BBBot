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

from irclib import nm_to_n, is_channel
from ircbot import SingleServerIRCBot
from datetime import datetime
from time import sleep, time
import bblib as brba
import traceback
import imdbdb
import sys


class BBBot(SingleServerIRCBot):
    stop = False

    def __init__(self, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.version = '0.4.6'
        self.github = 'https://github.com/Nikola-K/BBBot/'
        self.nickname = nickname
        self.initial_channels = brba.initialch
        self.banned_users = brba.banned
        self.admin = brba.admin
        self.authorized = brba.auth
        self.ircpass = brba.password
        self.cc = '#' + brba.cc
        self.debug = False
        self.logdebug = False
        self.maxlen = 440
        self.cmdlimits = {'!stream': 0, '!download': 0, '!i': 0, 'notify': 20,
                          'timelimit': 10, 'notifytime': 10}
        self.allcmds = ['bot', '.time', '.ban', '.unban', '.ath', '.rmath',
                        '.join', '.quit', '.say', '.add', '.remove', '.update',
                        '!i', '!download', '!stream', '!imdb', '!suggest',
                        '.help'
                        ]
        self.disabledcmds = ['!imdb', '!download']
        self.loggedinusers = []
        self.restrictedcmds = ['.time', '.ban', '.unban', '.ath', '.rmath',
                               '.join', '.quit', '.say', '.add', '.remove',
                               '.update'
                               ]
        self.cmdqueue = []

    _uninteresting_events = {
                             'all_raw_messages': None,
                             'yourhost': None,
                             'created': None,
                             'myinfo': None,
                             'featurelist': None,
                             'luserclient': None,
                             'luserop': None,
                             'luserchannels': None,
                             'luserme': None,
                             'n_local': None,
                             'n_global': None,
                             'luserconns': None,
                             'motdstart': None,
                             'motd': None,
                             'endofmotd': None,
                             'topic': None,
                             'topicinfo': None,
                             'ping': None,
                             }

    def _dispatcher(self, c, e):
        if self.debug:
            eventtype = e.eventtype()
            if eventtype not in self._uninteresting_events:
                source = e.source()
                if source is not None:
                    source = nm_to_n(source)
                else:
                    source = ''
                debug = "Event: %s (%s->%s) %s" % (eventtype, source,
                                                   e.target(),
                                                   e.arguments())
                print debug
                print datetime.now()
                if self.logdebug:
                    f = open('log.log', 'a')
                    f.write(debug + '\n')
        SingleServerIRCBot._dispatcher(self, c, e)

    def on_mode(self, c, e):
        eventtype = e.eventtype()
        if eventtype == 'mode':
            fromnickname = e.source()
            if fromnickname is not None:
                fromnickname = nm_to_n(fromnickname)
            if fromnickname == None:
                return
            channel = e.target()
            try:
                modearg = e.arguments()[0]
                targetname = e.arguments()[1]
            except:
                return
            if targetname == c.get_nickname():
                if modearg.startswith('+'):
                    c.privmsg(channel, 'Thanks for the %s, %s!'\
                                      % (modearg, fromnickname))
                if modearg.startswith('-'):
                    c.privmsg(channel, ':( I really liked having %s, %s...'
                              % (modearg.replace('-', '+'), fromnickname))

    def on_307(self, c, e):
    #Event: event type: 307 (irc.TestIRC.localhost->BBBot)
    # ['nickname', 'is a registered nick']
        try:
            nickname = e.arguments()[0]
            print 'checking'
            if e.arguments()[1] == 'is a registered nick':
                if nickname.lower() in self.loggedinusers:
                    self.do_command(self.cmdqueue[0],
                                    self.cmdqueue[1],
                                    self.cmdqueue[2])
                    self.cmdqueue = []
                else:
                    self.loggedinusers.append(nickname.lower())
                    if len(self.cmdqueue) < 3:
                        self.cmdqueue = []
                        pass
                    else:
                        self.do_command(self.cmdqueue[0],
                                        self.cmdqueue[1],
                                        self.cmdqueue[2])
                        self.cmdqueue = []
        except:
            self.cmdqueue = []
            pass

    def on_privnotice(self, c, e):
        source = e.source()
        if (source and str(nm_to_n(e.source())).lower() in self.admin) or\
        (source and str(nm_to_n(e.source())).lower() == 'nickserv'):
            if e.arguments()[0].find('IDENTIFY') >= 0:
                # Received request to identify
                if self.ircpass and self.nickname == c.get_nickname():
                    c.privmsg('nickserv', 'identify %s' % self.ircpass)
            if e.arguments()[0].find('NICKNAME') >= 0:
                c.nick(self.nickname)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
        c.privmsg('NickServ', 'GHOST %s %s' % (self.nickname, self.ircpass))
        sleep(1)
        c.nick(str(self.nickname))
        if c.get_nickname() != self.nickname:
        #if for some reason we were unable to ghost originally intended nickname
        #should be fixed when nickname leaves/times out
            c.nick(c.get_nickname() + "__")

    def on_welcome(self, c, e):
        for ch in self.initial_channels:
            if ch.startswith('#'):
                c.join(ch)
            else:
                c.join('#' + ch)

    def on_quit(self, c, e):
        qnick = nm_to_n(e.source())
        if qnick.lower() == self.nickname.lower():
            # Our desired nick just quit - take the nick back
            #if this doesn't work /notice BBBot NICKNAME should
            #change bots name to our intentionally desired nickname
            c.nick(self.nickname)
        print 'User %s quit' % qnick
        if qnick.lower() in self.loggedinusers:
            self.loggedinusers.remove(qnick.lower())

    def on_privmsg(self, c, e):
        nickname = nm_to_n(e.source())
        if nickname in self.authorized:
            if nickname in self.loggedinusers:
                self.do_command(nm_to_n(e.source()),
                                e.target(),
                                e.arguments()[0])
            else:
                c.whois(nickname)
                #sleep(1)
                self.cmdqueue.append(nm_to_n(e.source()))
                #chan/nick
                self.cmdqueue.append(e.target())
                #destination
                self.cmdqueue.append(e.arguments()[0])
                #command

    def on_pubmsg(self, c, e):
        nick = nm_to_n(e.source())
        t = e.target()
        command = e.arguments()[0]
        if command == '!streams':
            command = '!stream'
        try:
            if (command.split()[0] in self.disabledcmds) or\
               (('bot' in self.disabledcmds) and not\
               command.startswith('.turn')):
                return
        except:
            return
        if not is_channel(t):
            t = nick
        if (nick.lower() in self.authorized) and\
           (command.split()[0].strip() in self.restrictedcmds) and\
           (nick.lower() not in self.loggedinusers):
            c.whois(nick)
            self.cmdqueue.append(nm_to_n(e.source()))
            #chan/nick
            self.cmdqueue.append(e.target())
            #destination
            self.cmdqueue.append(e.arguments()[0])
            #command
            return
        if not nick.lower() in self.authorized:
            if command in ['!stream', '!i', '!download']:
                if time() - self.cmdlimits[command] < self.cmdlimits['timelimit']:
                    if time() - self.cmdlimits['notify'] > self.cmdlimits['notifytime']:
                        try:
                        #info and notification split to 2 lines to make it easier to read
                            info = str(self.cmdlimits['timelimit']),
                            str(self.cmdlimits['timelimit'] - 
                            (time() - self.cmdlimits[command])).split('.')[0]
                            notification = ': Only one command of that kind is'\
                            'alllowed every %s seconds, try again in %s seconds' % info
                        except:
                            notification = 'Error:'
                        c.privmsg(t, nick + notification)
                        self.cmdlimits['notify'] = time()
                    return
                self.cmdlimits[command] = time()
        self.do_command(nm_to_n(e.source()), e.target(), e.arguments()[0])
        return

    def do_command(self, nick, t, cmd):
        c = self.connection
        if not is_channel(t):
            t = nick

        if (cmd.split()[0].strip().lower() in self.disabledcmds) or\
           (nick.lower() in self.banned_users) or\
           (('bot' in self.disabledcmds) and (cmd.split()[0] != ('.turn'))):
            return
        if (nick.lower() in self.authorized) and\
           (cmd.split()[0].strip() in self.restrictedcmds) and\
           (nick.lower() not in self.loggedinusers):
            c.privmsg(t, 'You need to be logged in to do that')

        elif cmd == 'botinfo':
            if nick.lower() in self.admin:
                inchannels = []
                for chname in self.channels:
                    inchannels.append(chname)
                c.privmsg(nick, 'Disabled commands:' + str(self.disabledcmds))
                c.privmsg(nick, 'Initial channels:' + str(self.initial_channels))
                c.privmsg(nick, 'Currently on: ' + str(inchannels))
                c.privmsg(nick, 'Banned users:' + str(self.banned_users))
                c.privmsg(nick, 'Bot admins:' + str(self.admin))
                c.privmsg(nick, 'Bot authorized users' + str(self.authorized))
                sleep(3)

        elif cmd.split()[0] == ('.time'):
            subcmd = cmd.replace('.time', '').strip()
            if nick.lower() in self.authorized:
                if subcmd.split()[0].strip() == 'limit':
                    newlimit = subcmd.replace('limit', '').strip()

                    try:
                        self.cmdlimits['timelimit'] = float(newlimit)
                    except ValueError:
                        c.privmsg(t, 'Value must be number')
                        return
                    c.privmsg(t, nick + ': Limit for every user command set to %s seconds!' % newlimit)
                    return
                if subcmd.split()[0].strip() == 'notify':
                    newlimit = subcmd.replace('notify', '').strip()
                    try:
                        self.cmdlimits['notifytime'] = float(newlimit)
                    except ValueError:
                        c.privmsg(t, 'Value must be number')
                        return
                    c.privmsg(t, nick + ': Minimum time between notifications set to %s seconds!' % newlimit)
                    return
                else:
                    c.privmsg(t, nick + ': Invalid parameters, .time <limit/notify> <number>')

        elif cmd.split()[0] == ('.turn'):
            if nick.lower() in self.admin:
                what = cmd.split()[1].strip()
                value = cmd.split()[2].strip()
                if what not in self.allcmds:
                    c.privmsg(t, 'Unknown command %s' % what)
                    return
                if not value.lower() in ['on', 'off']:
                    c.privmsg(t, 'Unknown value %s | only "on" and "off are supported' % value)
                    return
                if value.lower() == 'off':
                    if what.lower() in self.disabledcmds:
                        c.privmsg(t, '%s is already disabled' % what)
                        return
                    self.disabledcmds.append(what.lower())
                    c.privmsg(t, '%s is now disabled.' % what)
                if value.lower() == 'on':
                    if not what.lower() in self.disabledcmds:
                        c.privmsg(t, '%s isn\'t disabled' % what)
                        return
                    self.disabledcmds.remove(what.lower())
                    c.privmsg(t, '%s is now enabled.' % what)

        elif cmd.split()[0] == ('.ban') or cmd.startswith('.unban'):
            if nick.lower() in self.authorized:
                if cmd.split()[0].strip() == '.ban':
                    user = cmd.replace('.ban', '').strip()
                    if user.lower() in self.banned_users:
                        c.privmsg(t, user + ' is already banned')
                    else:
                        self.banned_users.append(user.lower())
                        c.privmsg(t, user + ' is banned from using BBBot.')
                if cmd.split()[0].strip() == '.unban':
                    user = cmd.replace('.unban', '').strip()
                    if user.lower() in self.banned_users:
                        self.banned_users.remove(user.lower())
                        c.privmsg(t, user + ' is now allowed to use BBBot.')
                    else:
                        c.privmsg(t, user + ' is not banned.')

        elif cmd.split()[0] == ('.ath'):
            user = cmd.replace('.ath', '').strip()
            if nick.lower() in self.admin:
                self.authorized.append(user)
                c.privmsg(t, user + ' is added to list of authoritized users.')

        elif cmd.split()[0] == ('.rmath'):
            user = cmd.replace('.rmath', '').strip()
            if nick.lower() in self.admin:
                if user in self.admin:
                    c.privmsg(t, 'It\'s impossible to remove ' + user)
                    return
                if user in self.authorized:
                    self.authorized.remove(user)
                    c.privmsg(t, user + ' is removed from list of authoritized users.')
                else:
                    c.privmsg(t, user + ' is not on the list')

        elif cmd.split()[0] == ('.join'):
            channels = cmd.replace('.join', '').strip()
            if nick.lower() in self.admin:
                for ch in channels.split():
                    if ch.startswith('#'):
                        c.join(ch)
                    else:
                        c.join('#' + ch)

        elif cmd.split()[0] == ('.quit'):
            channels = cmd.replace('.quit', '').strip()
            if nick.lower() in self.admin:
                for ch in channels.split():
                    if ch.startswith('#'):
                        c.part(ch + ' BBBot out!')
                    else:
                        c.part('#' + ch + ' BBBot out!')

        elif cmd.split()[0] == ('.say'):
            if nick.lower() in self.authorized:
                channel = cmd.replace('.say', '').strip().split()[0]
                text = cmd.replace('.say', '').replace(channel, '').strip()
                if len(cmd.split()) < 3:
                    c.privmsg(t, 'Missing something? Proper usage .say channel text,'\
                              ' you seem to only have 2 parameters.')
                    return
                if not channel.startswith('#'):
                    channel = '#' + channel
                inchannels = []
                for chname in self.channels:
                    inchannels.append(chname)
                if channel in inchannels:
                    c.privmsg(channel, text)
                    return
                if not channel in inchannels:
                    c.privmsg(t, 'Bot doesn\'t seem to be in %s channel,'\
                              ' so he can\'t say anything there.' % channel)
                    return
                else:
                    c.privmsg(t, 'Some error')

        elif cmd.split()[0] == ('.add'):
            if nick.lower() in self.authorized:
                try:
                    what = cmd.split()[1].strip()
                    value = cmd.replace('.add', '').replace(what, '').strip()
                except IndexError:
                    c.privmsg(t, 'Error. Proper usage .add <stream/download> <link>')
                c.privmsg(t, brba.addremove('add', what, value))
            else:
                c.privmsg(t, nick + ': You\'re not allowed to add links.')

        elif cmd.split()[0] == ('.remove'):
            if nick.lower() in self.authorized:
                try:
                    what = cmd.split()[1].strip()
                    value = cmd.replace('.remove', '').replace(what, '').strip()
                except IndexError:
                    c.privmsg(t, 'Error. Proper usage .remove <stream/download> <link>')
                if what == 'stream' and value == 'clear_all':
                    c.privmsg(t, 'Removing all links, use following text to restore it if necessary!')
                    c.privmsg(t, brba.stream()[13:].strip())
                c.privmsg(t, brba.addremove('remove', what, value))
            else:
                c.privmsg(t, nick + ': You\'re not allowed to remove links.')

        elif cmd.split()[0] == '.inf':
            if nick.lower() in self.authorized:
                try:
                    info = cmd.replace('.inf', '')
                except IndexError:
                    c.privmsg(t, 'index error')
                c.privmsg(t, brba.updateainfo(info))

        elif cmd == '!i':
            c.privmsg(t, brba.info())

        elif cmd == '!download':
            c.privmsg(t, brba.download())

        elif cmd == '!stream' or cmd == '!streams':
            c.privmsg(t, brba.stream())

        elif cmd.split()[0] == '!suggest':
            suggestion = cmd.replace('!suggest', '')
            if suggestion.strip() != '':
                c.privmsg(self.cc, '[suggestion] : ' + nick + ' : ' + suggestion)
                c.privmsg(nick, 'Thank you for your suggestion it will be reviewed as soon as possible!')

        elif cmd.split()[0] == '!imdb':
            values = cmd.replace('!imdb', '')
            values = values.split('.')
            try:
                season = int(values[0])
                episode = int(values[1])
            except ValueError:
                c.privmsg(t, 'Error, use it like this <!imdb 1.2> for example')
                return
            result = imdbdb.get_from_db(season, episode, self.maxlen)
            c.privmsg(t, result)

        elif cmd == '.help' or cmd == '.help -v':
            if len(cmd.split()) == 2:
                print cmd.split()
                if cmd.split()[1].strip() == '-v':
                    c.privmsg(t, 'BBBot Version %s by wub_wub' % self.version)
                    return
            c.privmsg(t, 'Check out GitHub for help! %s' % self.github)


def main():
    server = '127.0.0.1'
    port = 6667
    nickname = 'BBBot'

    bot = BBBot(nickname, server, port)
    while not bot.stop:
        try:
            bot.start()
        except:
            try:
                f = open('log.log', 'a')
                f.write('******Error: ' + str(datetime.now()))
                f.write(str(sys.exc_info()) + '\n')
                f.write('Sys.exc_info: ' + str(sys.exc_info()) + '\n')
                t, v, tb = sys.exc_info()
                for line in traceback.format_exception(t, v, tb):
                    err = line + '\n'
                    f.write(err)
                f.write('*' * 20)
                f.close()
            except:
                pass
            raise
            sys.exc_clear()
            sys.exc_traceback = sys.last_traceback = None

if __name__ == "__main__":
    main()
