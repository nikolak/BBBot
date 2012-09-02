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

import shelve

def main():
	db=shelve.open('database.db')
	db['password'] ='bot_nickname_password'
	db['banned']=['']
	db['admin']=['user1','user2']
	db['auth']=['user1','user2']
	db['initialch']=['channel1','channel2']
	db['streamlinks']=['']
	db['downloadlinks']=['']
	db['reddit']=''
	db['cc']=''
	db['api_key']=''
	db.sync()
	db.close()
	return 0

if __name__ == '__main__':
	main()


