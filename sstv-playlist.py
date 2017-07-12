#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''generate an m3u8 playlist with your SmoothStreamsTV credentials'''

from getpass import getpass
from json import loads, dumps
from os import path
from urllib.request import urlopen
from urllib.parse import urlencode
import time

__appname__ = 'SSTV-playlist'
__author__ = 'Stevie Howard (stvhwrd)'
__copyright__ = 'Copyright 2016, Stevie Howard'
__license__ = 'MIT'
__version__ = 'v0.2-beta'


greeting = '''
WELCOME to the SmoothStreamsTV playlist generator!

This program will generate an .m3u8 playlist file with all available channels
for the SmoothStreamsTV IPTV provider, playable in media players and browsers.
Please note: channel names/numbers are sourced from SmoothStreamsTV,
and current as of March 15, 2017.
'''


def main():

    colourPrint('bold', greeting)
    # ENTER YOUR CREDENTIALS BELOW
    # example: username = 'sampleuser@email.com'
    # example: password = 'psswrd1234!'
    username = ''
    password = ''

    # CHOOSE YOUR SERVER HERE (see list below)
    # example for US West:  server = 'dnaw'
    server = ''

    servers = {
        'Asia Random':                      'dap',
        'Europe NL1 (Amsterdam)':           'deu-nl1',
        'Europe NL2 (Amsterdam)':           'deu-nl2',
        'Europe NL3 (Amsterdam)':           'deu-nl3',
        'Europe NL Random':                 'deu-nl',
        'Europe UK1 (io)':                  'deu-uk1',
        'Europe UK2 (100TB)':               'deu-uk2',
        'Europe UK Random':                 'deu-uk',
        'Europe Random':                    'deu',
        'USA/Canada East 1 (New Jersey)':   'dnae1',
        'USA/Canada East 2 (Virginia)':     'dnae2',
        'USA/Canada East 3 (Montreal)':     'dnae3',
        'USA/Canada East 4 (Toronto)':      'dnae4',
        'USA/Canada East Random':           'dnae',
        'USA/Canada West 1 (Phoenix, AZ)':  'dnaw1',
        'USA/Canada West 2 (San Jose, CA)': 'dnaw2',
        'USA/Canada West Random':           'dnaw',
        'USA/Canada Random':                'dna'
    }

    # CHOOSE YOUR HOST HERE (see list below)
    # example for StreamTVNow:  host = 'viewstvn'
    host = ''

    hosts = {
        'Live247':     'view247',
        'MyStreams':   'viewms',
        'StarStreams': 'viewss',
        'StreamTVNow': 'viewstvn'
    }

    # If you have not hardcoded your credentials and server/host preferences
    # above, you will be prompted for them on each run of the script.
    if not host:
        host = getHost(hosts)

    if not server:
        server = getServer(servers)

    if not username or not password:
        username, password = getCredentials()

    colourPrint('yellow',
                '\nPlease wait, generating playlist.')

    authSign = getAuthSign(username, password, host)

    playlistText = generatePlaylist(server, host, authSign)
    playlistFile = buildPlaylistFile(playlistText)
# end main()


def getAuthSign(un, pw, host):
    '''request JSON from server and return hash'''

    baseUrl = 'http://auth.smoothstreams.tv/hash_api.php?'

    params = {
        "username": un,
        "password": pw,
        "site": host
    }

    url = baseUrl + urlencode(params)

    try:
        response = urlopen(url).read().decode('utf-8')
        data = loads(response)
        if data['hash']:
            colourPrint('green',
                        'Thank you, authentication complete.\n')
            return data['hash']

    except ValueError:
        colourPrint('red',
                    'Unable to retrieve data from the server.\n' +
                    'Please check your internet connection and try again.')
        exit(1)
    except KeyError:
        colourPrint('red',
                    'There was an error with your credentials.\n' +
                    'Please double-check your username and password,' +
                    ' and try again.')
        exit(1)
# end getAuthSign()


def getCredentials():
    '''prompt user for username and password'''

    colourPrint('bold',
                ('You may wish to store your credentials and server ' +
                 'preferences in this file by opening it in a text editor ' +
                 'and filling in the username, password, and server ' +
                 'fields.\nIf you choose not to do this, you will be ' +
                 'prompted for this information on each run of this script.'))

    colourPrint('yellow',
                '\nPlease enter your username for SmoothStreamsTV:')
    username = input('')
    colourPrint('green',
                '\nThank you, ' + username + '.\n')

    colourPrint('yellow',
                '\nPlease enter your password for SmoothStreamsTV:')
    password = getpass('')

    return username, password
# end getCredentials()


def getServer(servers):
    '''prompt user to choose closest server'''

    validServer = False

    colourPrint('yellow',
                '\nServer options:')
    colourPrint('yellow',
                dumps(servers, sort_keys=True, indent=4))
    print('Example, for USA/Canada West 1 (Phoenix, AZ): enter "dnaw1" (without the quotes)\n')
    colourPrint('yellow',
                '\nPlease choose your server:')
    server = input('')
    for key, value in list(servers.items()):
        # cheap and dirty alternative to regex
        if server in value and len(value) == len(server):
            validServer = True
            colourPrint('green',
                        '\nYou have chosen the ' + key + ' server.\n')
            break

    if not validServer:
        colourPrint('red',
                    ('\n"' + server + '" is not a recognized server.' +
                     ' The playlist will be built with "' + server + '",' +
                     ' but may not work as expected.\n'))

    return (server)
# end getServer()


def getHost(hosts):
    '''prompt user to choose closest server'''

    validHost = False

    colourPrint('yellow',
                '\nHost options:')
    colourPrint('yellow',
                dumps(hosts, sort_keys=True, indent=4))
    print('Example, for StreamTVNow: enter "viewstvn" (without the quotes)\n')
    colourPrint('yellow',
                '\nPlease choose your host:')
    host = input('')
    for key, value in list(hosts.items()):
        # cheap and dirty alternative to regex
        if host in value and len(value) == len(host):
            validHost = True
            colourPrint('green',
                        '\nYou have chosen the ' + key + ' host.\n')
            break

    if not validHost:
        colourPrint('red',
                    ('\n"' + value + '" is not a recognized host.' +
                     ' Authentication will be attempted on "' + value +
                     '", but might not succeed.\n'))

    return (host)
# end getServer()


def buildPlaylistFile(body):
    '''write playlist to a new local m3u8 file'''

    title = 'SmoothStreamsTV.m3u8'

    # open file to write, or create file if DNE, write <body> to file and save
    with open(title, 'w+') as f:
        f.write(body)
        f.close()

    # check for existence/closure of file
    if f.closed:
        colourPrint('yellow',
                    '\nPlaylist built successfully, located at: ')
        colourPrint('underline',
                    path.abspath(title))
        exit(0)
    else:
        raise FileNotFoundError
# end buildPlaylistFile()


def generatePlaylist(server, host, authSign):
    '''build string of channels in m3u8 format based on
    global channelDictionary'''

    m3u8 = '#EXTM3U\n'
    # iterate through channels in channel-number order
    for channel in sorted(channelDictionary, key=lambda channel: int(channel)):
        m3u8 += ('#EXTINF:-1, ' + channel +
                 ' ' + channelDictionary[channel] +
                 '\n' + 'http://' + server +
                 '.smoothstreams.tv:9100/' + host + '/ch' + channel +
                 'q1.stream/playlist.m3u8?wmsAuthSign=' + authSign + '\n')

    return m3u8
# end generatePlaylist()


class colour:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def colourPrint(spec, text):
    '''print text with specified formatting effect'''

    text = str(text)
    if spec.upper() == 'BOLD':
        print((colour.BOLD + text + colour.END))
    elif spec.upper() == 'GREEN':
        print((colour.GREEN + text + colour.END))
    elif spec.upper() == 'YELLOW':
        print((colour.YELLOW + text + colour.END))
    elif spec.upper() == 'RED':
        print((colour.RED + text + colour.END))
    elif spec.upper() == 'PURPLE':
        print((colour.PURPLE + text + colour.END))
    elif spec.upper() == 'CYAN':
        print((colour.CYAN + text + colour.END))
    elif spec.upper() == 'DARKCYAN':
        print((colour.DARKCYAN + text + colour.END))
    elif spec.upper() == 'BLUE':
        print((colour.BLUE + text + colour.END))
    elif spec.upper() == 'UNDERLINE':
        print((colour.UNDERLINE + text + colour.END))
# end colourPrint()


channelDictionary = {
    '01': 'ESPNNews',
    '02': 'ESPN',
    '03': 'ESPN 2',
    '04': 'ESPN U',
    '05': 'Fox Sports 1',
    '06': 'Fox Sports 2',
    '07': 'NFL Network',
    '08': 'NBA TV',
    '09': 'MLB Network',
    '10': 'NHL Network',
    '11': 'NBC Sports Network',
    '12': 'Golf Channel',
    '13': 'Tennis Channel',
    '14': 'CBS Sports Network',
    '15': 'Fight Network',
    '16': 'WWE Network',
    '17': 'Sportsnet World',
    '18': 'Sportsnet 360',
    '19': 'Sportsnet Ontario',
    '20': 'Sportsnet One',
    '21': 'TSN 1',
    '22': 'Univision Deportes',
    '23': 'ESPN Deportes',
    '24': 'Comedy Central',
    '25': 'Spike',
    '26': 'USA Network',
    '27': 'A&E',
    '28': 'TBS',
    '29': 'TNT',
    '30': 'SyFy',
    '31': 'Cartoon Network East',
    '32': 'HGTV',
    '33': 'CNN',
    '34': 'NBC East',
    '35': 'CBS East',
    '36': 'ABC East',
    '37': 'Fox East',
    '38': 'Viceland',
    '39': 'CNBC',
    '40': 'Fox News 360',
    '41': 'History Channel',
    '42': 'Discovery Channel',
    '43': 'National Geographic',
    '44': 'FX',
    '45': 'FXX',
    '46': 'BeIN USA',
    '47': 'AMC',
    '48': 'HBO East',
    '49': 'HBO Comedy',
    '50': 'HBO Signature',
    '51': 'HBO Zone',
    '52': 'Showtime East',
    '53': 'ActionMax HD East',
    '54': 'Cinemax Moremax',
    '55': 'Starz Cinema',
    '56': 'Starz East',
    '57': 'Starz Cinema',
    '58': 'Investigation America',
    '59': 'Cinemax East',
    '60': 'Cinemax 5 Star',
    '61': '',
    '62': '',
    '63': 'Food Network',
    '64': 'E!',
    '65': '',
    '66': '',
    '67': '',
    '68': '',
    '69': '',
    '70': 'US West',
    '71': 'US West',
    '72': 'US West',
    '73': 'Spectrum Sportsnet',
    '74': 'MMA TV 01',
    '75': 'AXS TV HD',
    '76': 'Sportsnet Ontario 720p',
    '77': 'Sportsnet One 720p',
    '78': 'TSN 1 720p',
    '79': 'AMC 720p',
    '80': 'HBO 720p',
    '81': 'HBO Comedy 720p',
    '82': 'HBO Signature 720p',
    '83': 'HBO Zone 720p',
    '84': 'ActionMax 720p',
    '85': '',
    '86': '',
    '87': '',
    '88': '',
    '89': '',
    '90': '',
    '91': '',
    '92': '',
    '93': '',
    '94': '',
    '95': '',
    '96': '',
    '97': '',
    '98': '',
    '99': '',
    '100': '',
    '101': '',
    '102': '',
    '103': '',
    '104': '',
    '105': '',
    '106': '',
    '107': 'Premier HD',
    '108': 'BT Sport 1 HD',
    '109': 'BT Sport 2 HD',
    '110': 'BT Sport 3 HD',
    '111': 'BT Sport ESPN HD',
    '112': 'Sky Sports News',
    '113': 'Sky Sports 1 UK',
    '114': 'Sky Sports 2 UK',
    '115': 'Sky Sports 3 UK',
    '116': 'Sky Sports 4 UK',
    '117': 'Sky Sports 5 UK',
    '118': 'Sky Sports F1 UK',
    '119': 'European Slot',
    '120': 'European Slot'
}


if __name__ == '__main__':
    main()
