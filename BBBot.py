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

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, ip_numstr_to_quad, is_channel
from time import sleep, time
import bblib as brba
import imdbdb
import sys

class BBBot(SingleServerIRCBot):
    stop = False

    def __init__(self, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        try:
            self.initial_channels = brba.initialch
            self.banned_users = brba.banned
            self.admin = brba.admin
            self.authorized = brba.auth
            self.ircpass = brba.password
            self.cc = '#' + brba.cc
        except AttributeError:
            print 'Problems with the database, one or more items missing.'
            self.stop = True
            self.die()
        self.maxlen = 440
        self.cmdlimits = {'!stream':0, '!download':0, '!i':0, 'notify':20, 'timelimit':10, 'notifytime':10}
        self.allcmds = ['bot', '.time', '.ban', '.unban', '.ath', '.rmath', '.join', '.quit', '.say', '.add', '.remove', '.update', '!i', '!download', '!stream', '!imdb', '!suggest', '.help']
        self.disabledcmds = ['!imdb', '!download']
    def on_nicknameinuse(self, c, e):
#        if we want to ghost originally intented nickname, not really tested, should work in theory
#        c.privmsg('NickServ', 'GHOST %s %s' % (self.nickname, self.ircpass))
#        sleep(2)#enough?
#        c.nick(self.nickname)
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.privmsg('NickServ', 'IDENTIFY ' + self.ircpass.strip())#strip needed?
        sleep(2) 
        for ch in self.initial_channels:
            if ch.startswith('#'):
                c.join(ch)
            else:
                c.join('#' + ch)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        nick = nm_to_n(e.source())
        t = e.target()
        command = e.arguments()[0]
        if command == '!streams':
            command = '!stream'
        if command.split()[0] in self.disabledcmds:
            return
        if 'bot' in self.disabledcmds and not command.startswith('.turn'):
            return
        if not is_channel(t):
            t = nick
        if not nick.lower() in self.authorized:
            if command in ['!stream', '!i', '!download']:
                if time() - self.cmdlimits[command] < self.cmdlimits['timelimit']:
                    if time() - self.cmdlimits['notify'] > self.cmdlimits['notifytime']:
                        try:#info and notification split to 2 lines to make it easier to read
                            info = str(self.cmdlimits['timelimit']), str(self.cmdlimits['timelimit'] - (time() - self.cmdlimits[command])).split('.')[0]
                            notification = ': Only one command of that kind is alllowed every %s seconds, try again in %s seconds' % info
                        except:
                            notification = 'Error:'
                        c.privmsg(t, nick + notification)
                        self.cmdlimits['notify'] = time()
                    return
                self.cmdlimits[command] = time()
        self.do_command(e, e.arguments()[0])
        return#?

    def on_dccmsg(self, c, e):
        c.privmsg("You said: " + e.arguments()[0])
            
    def on_dccchat(self, c, e):
        if len(e.arguments()) != 2:
            return
        args = e.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)
        

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection
        t = e.target()
        #cmd=cmd.strip()
        if not is_channel(t):
            t = nick

        if cmd.split()[0].strip().lower() in self.disabledcmds:
            return
        if nick.lower() in self.banned_users:
            return

        elif 'bot' in self.disabledcmds and not cmd.startswith('.turn'):
            return

        elif cmd == 'botinfo':
            if nick.lower() in self.admin:
                c.privmsg(nick, 'Disabled commands:')
                c.privmsg(nick, self.disabledcmds)
                c.privmsg(nick, 'Initial channels:')
                c.privmsg(nick, self.initial_channels)
                sleep(2)
                c.privmsg(nick, 'Banned users:')
                c.privmsg(nick, self.banned_users)
                sleep(2)
                c.privmsg(nick, 'Bot admins:')
                c.privmsg(nick, self.admin)
                sleep(2)
                c.privmsg(t, 'Bot authorized users')
                c.privmsg(t, self.authorized)
                
                
                
        elif cmd.startswith('.time'):
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
        
        elif cmd.startswith('.turn'):
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
                        c.privmsg(t, '%s is already disabled')
                        return
                    self.disabledcmds.append(what.lower())
                    c.privmsg(t, '%s is now disabled.' % what)
                if value.lower() == 'on':
                    if not what.lower() in self.disabledcmds:
                        c.privmsg(t, '%s isn\'t disabled')
                        return
                    self.disabledcmds.remove(what.lower())
                    c.privmsg(t, '%s is now enabled.' % what)

        elif cmd.startswith('.ban') or cmd.startswith('.unban'):
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

        elif cmd.startswith('.ath'):
            user = cmd.replace('.ath', '').strip()
            if nick.lower() in self.admin:
                self.authorized.append(user)
                c.privmsg(t, user + ' is added to list of authoritized users.')
        

        elif cmd.startswith('.rmath'):
            user = cmd.replace('.rmath', '').strip()
            if nick.lower() in self.admin:
                if user in self.admin:
                    c.privmsg(t, 'It\'s impossible to remove' + user)
                    return
                if user in self.authorized:
                    self.authorized.remove(user)
                    c.privmsg(t, user + ' is removed from list of authoritized users.')
                else:
                    c.privmsg(t, user + ' is not on the list')

        elif cmd.startswith('.join'):
            ch = cmd.replace('.join', '').strip()
            if nick.lower() in self.admin:
                if ch.startswith('#'):
                    c.join(ch)
                else:
                    c.join('#' + ch)
                
        elif cmd.startswith('.quit'):
            ch = cmd.replace('.quit', '').strip()
            if nick.lower() in self.admin:
                if ch.startswith('#'):
                    c.part(ch + ' BBBot out!')
                else:
                    c.part('#' + ch + ' BBBot out!')
                
        elif cmd.startswith('.say'):
            if nick.lower() in self.authorized:
                channel = cmd.replace('.say', '').strip().split()[0]
                text = cmd.replace('.say', '').replace(channel, '').strip()
                if len(cmd.split()) < 3:
                    c.privmsg(t, 'Missing something? Proper usage .say channel text, you seem to only have 2 parameters.')
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
                    c.privmsg(t, 'Bot doesn\'t seem to be in %s channel, so he can\'t say anything there.' % channel)
                    return
                else:
                    c.privmsg(t, 'Some error')
                
    
        elif cmd.startswith('.add'):
            if nick.lower() in self.authorized:
                try:
                    what = cmd.split()[1].strip()
                    value = cmd.replace('.add', '').replace(what, '').strip()
                except IndexError:
                    c.privmsg(t, 'Error. Proper usage .add <stream/download> <link>')
                c.privmsg(t, brba.addremove('add', what, value))
            else:
                c.privmsg(t, nick + ': You\'re not allowed to add links.')

        elif cmd.startswith('.remove'):
            if nick.lower() in self.authorized:
                try:
                    what = cmd.split()[1].strip()
                    value = cmd.replace('.remove', '').replace(what, '').strip()
                except IndexError:
                    c.privmsg(t, 'Error. Proper usage .remove <stream/download> <link>')
                if what == 'stream' and value == 'clear_all':
                    c.privmsg(t, 'Removing all links, use following text to restore it if necessary!')
                    c.privmsg(t, brba.stream())
                c.privmsg(t, brba.addremove('remove', what, value))
            else:
                c.privmsg(t, nick + ': You\'re not allowed to remove links.')

        elif cmd.startswith('.update'):
            if nick.lower() in self.authorized:
                try:
                    url = cmd.replace('.update', '')
                except IndexError:
                    c.privmsg(t, 'index error')
                c.privmsg(t, brba.updatethread(url))
                
        elif cmd == '!i':
            if not is_channel(t): 
                return
            c.privmsg(t, brba.info())

        elif cmd == '!download':
            if not is_channel(t): 
                return
            c.privmsg(t, brba.download())
            
        elif cmd == '!stream' or cmd == '!streams':
            if not is_channel(t): 
                return
            c.privmsg(t, brba.stream())
            
        elif cmd.startswith('!imdb'):
            if not is_channel(t): 
                return
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
            
        elif cmd.startswith('!suggest'):
            if not is_channel(t): 
                return
            suggestion = cmd.replace('!suggest', '')
            if suggestion.strip() != '':
                c.privmsg(self.cc, '[suggestion] : ' + nick + ' : ' + suggestion)


            
        elif cmd == '.help':
                if nick.lower() in self.admin:
                    helpStrings = [
                                   '.turn <on/off> | turns bot on or off (ignores all commands)',
                                   '.ath <username> | adds <username> to authorized list allowing them to use .<add/remove> and .<update>',
                                   '.rmath <username> | removes <username> from authorized list',
                                   '.join <channel> | bot will join #<channel> be sure to write the channel name without # otherwise the bot will join ##<channel>',
                                   '.quit <channel> | bot will part from <channel> be sure to use <chanell> without #',
                                   '.add <stream or download> <link> | adds link to stream or download list. <link> can contain multiple words and spaces',
                                   '.remove <stream/download> <link> | Opposite of command above. Note: if you added link with multiple words this command can\'t remove only certain words. You have to enter same text as when it was added',
                                   '.update <text> | this adds text after "Latest reddit discussion thread" in !i command.',
                                   '.add sstream <link> | this will shorten <link> using goog.gl and add it to stream list'
                                   ]
                elif nick.lower() in self.authorized:
                    helpStrings = [
                                   '.add <stream or download> <link> | adds link to stream or download list. <link> can contain multiple words and spaces',
                                   '.remove <stream/download> <link> | Opposite of command above. Note: if you added link with multiple words this command can\'t remove only certain words. You have to enter same text as when it was added',
                                   '.update <text> | this adds text after "Latest reddit discussion thread" in !i command.',
                                   '.add sstream <link> | this will shorten <link> using goog.gl and add it to stream list'
                                   ]
                else: 
                    helpStrings = [
                                    '!stream | shows current list of streams',
                                    '!download | shows current list of download links',
                                    '!i | shows info about show, time untill next episode, next episode name, latest reddit discussion',
                                    '!suggest <link> | suggest link to be added to !stream list of streams'
                                    ]
                for string in helpStrings:
                    c.privmsg(nick, string)


def main():
    server = '127.0.0.1'
    port = 6667
    nickname = 'BBBot'
    
    bot = BBBot(nickname, server, port)
    while not bot.stop:
        try:
            bot.start()
        except:
            print sys.exc_info()[0]
            raise
    
if __name__ == "__main__":
    main()
 
