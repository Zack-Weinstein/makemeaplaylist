from os import urandom
import requests
import json
from datetime import datetime

overlapThresh = 0.4
now = datetime.now()
names = []

### Setup for spotify API
clientID = '00000'              # Replaced for git
clientSecret = '00000'          # Replaced for git
userID = 'raspberrypi3'

auth_url = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1/'

authData = {
    'grant_type': 'client_credentials',
    'client_id': clientID,
    'client_secret': clientSecret,
}

auth_response = requests.post(auth_url, data=authData)
access_token = auth_response.json().get('access_token')
access_token = 'BQBbfwRjb5A7gCZHsX-UkRif_sgOo-LXGtXAZRNoxYUcgnFP7JFBocIbp9xFhE4wjt01C9acsK7A9u5G_F3ZNjtzucC9med0JRuFOutiGgpqXIGcf3c8Th1QVayTWA8MpxYhU4EA6k2MHduR9zM0UtCc9x3H4PKkKJx_50Y1ZHHQtRkSKMRee5GfsQ6f10XADcom_TCE4qGAISlozyLTip-Ry8YgCetow7hpb2JaCmOvTDfW'

headers = {
    'Authorization': 'Bearer {}'.format(access_token)
}
###
def generatePlaylist(songs:list):
    seedGenres = genreList(songs)
    playlistEndpoint = (f'users/{userID}/playlists')
    playlistURL = ''.join([base_url, playlistEndpoint])
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    request_body = json.dumps({
          "name": f"Autolist -- {now}",
          "description": f"makin playlists {names}",
          "public": False
        })
    response = requests.post(url = playlistURL, data = request_body, headers=headers)
    playlistID = response.json()['id']
    playlistURL = response.json()['external_urls']['spotify']

    playlistList = []

    for genre in seedGenres:
        anotherOne = 0
        if len(playlistList) > 50:
            print("broken")
            break
        gsEndpoint = ('search?type=track&limit=40&q=genre%3A' + genre + '/')
        gsURL = ''.join([base_url,gsEndpoint])
        gsResponse = requests.get(gsURL,headers=headers)
        file = json.loads(gsResponse.text)
        for track in file['tracks']['items']:
            if anotherOne >= 50/(len(seedGenres)-1):
                break
            sURI = track['uri'].split(':')[2]
            sURL = track['external_urls']['spotify']
            score = genreMatch(sURI, seedGenres)
            if score >= overlapThresh:
                playlistList.append(f'spotify:track:{sURI}')
                anotherOne += 1
                print(f'{len(playlistList)*2}%')
            if score == 0:
                pass
            if len(playlistList) >= 50:
                break
    playAddEnd = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    playlistCon = json.dumps({
        "uris" : playlistList
    })
    response = requests.post(url = playAddEnd, data = playlistCon, headers=headers)
    return(playlistURL)

def idFromURL(song:str):
    sId = (song.split('track/')[1]).split('?')[0]
    return(sId)

def genreList(songz:list):
    songs = []
    for song in songz:
        songs.append(idFromURL(song))
    genres = []
    for song in songs:
         sEndpoint = ('tracks/' + song)
         sURL = ''.join([base_url,sEndpoint])
         sResponse = requests.get(sURL,headers=headers)
         sArtist = sResponse.json()['artists'][0]['id']
         aEndpoint = ('artists/' + sArtist)
         aURL = ''.join([base_url,aEndpoint])
         aResponse = requests.get(aURL,headers=headers)
         aGenres = aResponse.json()['genres']
         names.append(sResponse.json()['name'])
         for genre in aGenres[:3]:
            if genre not in genres:
                genres.append(genre)
    return genres

def genreMatch(songID:str, genres:list):
    score = 0
    sGenres = genreL('https://open.spotify.com/track/' + songID)
    for genre in sGenres:
        if genre in genres:
            score += 1
    if len(sGenres) > 0:
        score = score / len(sGenres)
    return(score)

def genreL(sonz:str):
    song = idFromURL(sonz)
    genres = []

    sEndpoint = ('tracks/' + song)
    sURL = ''.join([base_url,sEndpoint])
    sResponse = requests.get(sURL,headers=headers)
    sArtist = sResponse.json()['artists'][0]['id']
    aEndpoint = ('artists/' + sArtist)
    aURL = ''.join([base_url,aEndpoint])
    aResponse = requests.get(aURL,headers=headers)
    aGenres = aResponse.json()['genres']

    return aGenres

def mmafpl(songs:list):     # Testing
    playlistEndpoint = (f'users/{userID}/playlists')
    playlistURL = ''.join([base_url, playlistEndpoint])
    request_body = json.dumps({
          "name": "Just another playlist",
          "description": "makin playlists",
          "public": False
        })
    response = requests.post(url = playlistURL, data = request_body, headers=headers)
    playlistID = response.json()['id']
    playlistURL = response.json()['external_urls']['spotify']
    print(playlistURL)

    playAddEnd = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    playlistCon = json.dumps({
        "uris" : songs
    })
    response = requests.post(url = playAddEnd, data = playlistCon, headers=headers)
    print(response)
    print('***')

#generatePlaylist(['11dFghVXANMlKmJXsNCbNl', '23KrgrkSQN9rY3DWbklgMc'])
#generatePlaylist(['https://open.spotify.com/track/1WMBlpjhd3AUQiNfJOzfIl'])
#mmafpl(['spotify:track:4YIoQqE50AdyG4BQafCi3u','spotify:track:7yuecadXy2rAgc6Id2D6Qw'])
#genreL('https://open.spotify.com/track/55vsJO4tLZQ37qzD5QUOmh?si=000ed16311414402')
#generatePlaylist(['https://open.spotify.com/track/4YIoQqE50AdyG4BQafCi3u?si=4576e5fa3425460f', 'https://open.spotify.com/track/7yuecadXy2rAgc6Id2D6Qw?si=ba8af69da23d4293'])
#generatePlaylist(['https://open.spotify.com/track/21AJQhGZpujjZQXByZAXpr?si=739fe611e88b49c2', 'https://open.spotify.com/track/2MbdDtCv5LUVjYy9RuGTgC?si=07f4c4b3f2884441'])



def main():
    i = True
    while i:
        son = input("What songs would you like your playlist based on? Enter as many *spotify links* as you like separated by commas: ")
        songs = []
        for song in son.split(','):
            songs.append(song.strip(' '))
        #print(songs)
        try:
            print('\nBegining collation...')
            results = generatePlaylist(songs)
            print('Process completed successfully!\n')
            print(f'Here is the link to your custom playlist, enjoy! {results}')
            y = ((input("\nDo you want another playlist? Enter Y or N: ")).lower())
            if y == 'n':
                i = False
        except:
            print("\nUnfortunately that didn't work :( \nPlease make sure all your links are correct.\n")

main()