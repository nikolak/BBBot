BBBot
========

BBBot is a simple IRC bot written in python using [irclib](http://python-irclib.sourceforge.net/ "irclib -- Internet Relay Chat (IRC) protocol client library").
It's a simple bot that enables selected users to add links/text to be displayed when users use commands. Primarily wiritten to share stream/download links and/or episode info for TV Shows.
It also displays information when the next episode airs and its name.
The data is saved using shelve. Should work on every 2.6+ python. Tested and developed on python 2.7.3.

Commands
========

Commands are divided into 3 calink tegories, admins, authortized users and normal users.

All commands except the ones for normal users can be used via private chat i.e. they don't have to be said to bot publicly on a channel.

Admins:
--------

`.turn <on/off>`    - turns bot on or off, bot will still be online but it will ignore all commands.

`.ath <username>`   - adds <username> to authorized list allowing them to use commands listed below under "Admins/authoritized nicknames" section. Note: list of authoritized usernames isn't saved i.e. is lost on restart.

`.rmath <username>` - removes <username> from authorized list

`.join <channel>`   - bot will join <channel>

`.quit <channel>`   - bot will part from <channel>


Admins/authoritized nicknames:
--------

`.add <stream or download> <link>` - adds link to stream or download list. <link> can contain multiple words and spaces.

`.remove <stream/download> <link>` - Opposite of command above. Note: if you added link with multiple words this command can't remove only certain words. You have to enter same text as when it was added

`.add sstream <link>` - shortens link using goo.gl service and adds it to stream list, to remove it use `.remove stream <shortened url>`. When using `sstream` no additional text can be added with this command, it will return error if you try to use `.add sstream <url> some descriptive text`

`.ban <username>` and `.unban <username>` - disallow or allow <username> to use any of BBBot's commands

`.say <channel> <text>` - if bot is present on <channel> it will say <text> on that channel, channel can be entered as `#<channel>` or `<channel>`

To clear all stream links use `.remove stream clear_all` this will display current stream list in case you want to undo clear_all command.


Users:
--------

`!i`        - Shows next episode name, air time and link to reddit discussion thread. Example of displayed info:Next episode: [...] Latest reddit discussion thread S05E04 "Fifty-One" http://reddit.com

`!stream`   - Shows links/text that has been added via .add stream <link> command

`!download` - Shows links/text that has been added via .add download <link> command

`!suggest <url> and/or <text>` - suggest link to be added to stream/download list or sends message to BBBot's main channel.

Installation
========

To run BBBot on your own PC the following changes are necessarry:


create_db.py:
--------

In create_db.py change the following:

`password` - password to be used when bot joins, if nickname isn't registered leave it empty

`banned` - list of banned users, the users aren't allowed to use any command, even if user is in admin list. Banning using IRC commands will be implemented later on.

`admin` - people who will be on the admin list, the list can't be modified from IRC. Nicknames should be added as `['nickname','nickname2']` etc.

`auth` - list of people who are on authoritized list, users who are added in admin list should be manually added here too otherwise they won't be able to use commands assigned to users on authoritized list untill they're added to it.

`initialch` - list of channels that bot will attempt to join after it connects to server. 

`streamlinks` - list of stream links, you could leave this empty and add them from IRC.

`downloadlinks` - same as streamlinks only for download links.

`reddit` - text that will be showed after !i command, "Latest reddit discussion" + text in reddit field. This can be edited from IRC using .update command

`api_key` - Your goo.gl API key.

After you modified create_db.py file run it `python create_db.py` and it should create `database.db` file, make sure this file is in same location as bblib.py and BBBot.py files.

bblib.py
--------

On line 34 edit airtimes, enter times according to GMT timezone if you want the numbers to be correct.

On line 53 add episode names and air times, make sure that the air times are same as on line 34 otherwise the episode names won't be reutrned.

BBBot.py
--------

Modify server name on line 204, port on 205(default is 6667) and nickname on 206.

---

Make sure all files are in same folder and run BBBot.py.
