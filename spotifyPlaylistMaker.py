#################################################################
# SPOTIFY PLAYLIST MAKER
# Created on: July 3, 2019
# Created by: Amitesh Yeleswarapu
#################################################################
# The purpose of the app is to sort liked songs on Spotify into
# appropriate playlists based on Genre, Mood, and various audio
# features.
#################################################################
# To run go to terminal and this folder
# enter the following commands:
#   export SPOTIPY_CLIENT_ID='f61e3e870e5d432c96a8f9d18c2dd8b1'
#   export SPOTIPY_CLIENT_SECRET='a54568d361c1460cbae5760dc9543991'
#   export SPOTIPY_REDIRECT_URI='http://google.com/'
#   python3 <fileName> <userID>
#   python3 spotifyxx.py 22pogq775dvuszqbcfxgch5zi
#################################################################


import os
import sys
import json
import spotipy
import webbrowser
import datetime
import spotipy.util as util
from json.decoder import JSONDecodeError

#get the username from terminal
username = sys.argv[1]
scope = 'user-library-read' #for seeing all saved songs and reading information about them
scopeModify = 'playlist-modify-private' #for creating the private playlists
scopeReadPrivate = 'playlist-read-private'
#userID: 22pogq775dvuszqbcfxgch5zi

#erase cache and prompt for user persmission
def getSpotifyObject(username, scope = ""):
    try:
        token = util.prompt_for_user_token(username,scope)
    except:
        #if os.path.exists(f".cache-{username}"):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username,scope)
    return spotipy.Spotify(auth=token)

def removeBlankLines(myFile):
    with open(myFile,'rw') as file:
        for line in file:
            if not line.isspace():
                file.write(line)
def getBPM(songIDs,spotifyObject):
    idBPMdict = {}
    for songID in songIDs:
        idBPMdict[songID]=spotifyObject.audio_features(songID)[0]["tempo"]
    return idBPMdict
def main():
    #DIFFERENT SCOPED SPOTIFY OBJECTS INSTANTIATION
    spotifyObject = getSpotifyObject(username, scope)
    spotifyObjectModify = getSpotifyObject(username, scopeModify)
    spotifyObjectReadPrivate = getSpotifyObject(username, scopeReadPrivate)
    #CURRENT DATE
    now = datetime.datetime.now()
    n = str(now.month)+"/"+str(now.day)+"/"+str(now.year)
    #INSTANTIATE USER INFORMATION VARIABLES
    user = spotifyObject.current_user()
    userID = user['id']
    
    #DATA STRUCTURES FOR PLAYLIST INFORMATION AND CREATINO
    songLists = [dict() for x in range(6)]
    playlistsCreated = [False]*6
    playlistDict = {"Throwback":0,"Rap":1, "Dance":2,"Sad":3,"Happy":4,"High Energy":5}
    #0=tb, 1=rap, 2 = dance, 3=sad, 4=happy, 5=highEnergy
    
    #READ FROM FILE TO SEE WHICH PLAYLISTS HAVE ALREADY BEEN MADE AND JUST NEED TO BE UPDATED
    #OPEN FILE TO READ WRITE AND MODIFY
    #******************************************************************************************************************
    print("should have created file")
    pause = input("press any key to continue")
    plIDFileWrite = open("myPlaylistsID.txt","w")
    plIDFileRead = open("myPlaylistsID.txt","r")
    plIDS = list(plIDFileRead)
    plIDNameDict = {}
    
    #THIS IS TO CHECK WHICH PLAYLISTS ALREADY EXIST AND ARE IN THE FILE. THIS MAKES SURE THAT ERRORS ARE NOT MADE IF
    #PLAYLIST PREVIOUSLY CREATED WAS DELETED
    #******************************************************************************************************************
    print("about to go through file")
    for line in plIDS:
        try:
            #this will see if there exists a playlist with the id from the file
            #then it will create a list of dictionaries of songs in each playlist [[id:name]]
            line=line.strip()
            thisPlaylist = spotifyObjectReadPrivate.user_playlist(userID, line)
            thisPlaylistTracks = thisPlaylist["tracks"]
            pos = playlistDict[thisPlaylist["Name"]]
            playlistsCreated[pos]=True
            plIDNameDict[line]=thisPlaylist["Name"]
            for track in thisPlaylistTracks:
                songLists[pos][track["track"]["id"]]=track["track"]["name"]
        except:
                #NEED TO DELETE THE ID FROM THE FILE
                #MAKE SURE THAT THE FILE IS STILL BEING READ FROM CORRECTLY
            plIDFileWrite.write("\n")#replace incorrect lines with blank lines and then at the end call removeBlankLines function to fix the file.
    #******************************************************************************************************************
    print("went through file")
    #THIS IS WHERE YOU CREATE ANY NEW PLAYLISTS THAT HAVE NOT PREVIOUSLY BEEN CREATED BY THIS PROGRAM
    for playlistName in playlistDict:
        pos = playlistDict[playlistName]
        if not playlistsCreated[pos]:
            spotifyObjectModify.user_playlist_create(userID, name=playlistName+n,public=False, description = "Made by SpotifyPlaylistMaker")
            playlistsCreated[pos]=True
    #******************************************************************************************************************
    print("created new playlists")
    #THIS IS WHERE YOU UPDATE THE PLAYLISTID FILE WITH NEW IDS FROM PLAYLISTS YOU JUST CREATED
    playlists = spotifyObjectReadPrivate.current_user_playlists(limit=50, offset=0)
    plIDFileAppend = open("myPlaylistsID.txt","a+")
    for playlist in playlists['items']:
        if playlist['name'][:-len(n)] in playlistDict and playlist['name'].endswith(n):
            plIDNameDict[playlist["id"]]=playlist["name"][:-len(n)]
            spotifyObjectModify.user_playlist_change_details(userID, playlist["id"], name=playlist["name"][:-len(n)])
            plIDFileAppend.write(playlist["id"]+"\n")
    #******************************************************************************************************************
    print("changed names of new playlists and plIDNameDict has been created and plIDFile should be updated")
    print(plIDNameDict)

    #CLOSE PLAYLISTID FILE AND REMOVE POTENTIAL BLANK LINES INSERTED INTO PLAYLISTID FILE
    plIDFileRead.close()
    plIDFileAppend.close()
    plIDFileWrite.close()
#removeBlankLines("myPlaylistsID.txt")
    #******************************************************************************************************************
    print("closed all files")
                                                

    numSavedTracks = spotifyObject.current_user_saved_tracks(limit=1, offset=0)['total']
    #GET SONGS 20 AT A TIME AND PLACE IN APPROPRIATE PLAYLISTS
    for i in range(0,numSavedTracks//20+1):
        savedTracks = spotifyObject.current_user_saved_tracks(limit=20, offset = i*20)
        savedTracksList = savedTracks['items']
        print(str(i))
        for track in savedTracksList:
            #GATHERING OBJECTS NEEDED TO PLACE TRACKS INTO PLAYLISTS
            audioFeatures = spotifyObject.audio_features(track["track"]["id"])[0]
            #PLACE TRACK IN THROWBACK PLAYLIST
            if now.year - int(track['track']['album']['release_date'][0:4]) >10:
                #print(track['track']['name'], track['track']['album']['release_date'])
                #only add songs that are not already in the dictionary
                if track['track']['id'] not in songLists[playlistDict["Throwback"]]:
                    songLists[playlistDict["Throwback"]][track['track']['id']]=track['track']['name']
            #PLACE TRACK IN RAP PLAYLIST
            if audioFeatures["speechiness"]>0.33 and audioFeatures["speechiness"]<0.67:
                if track['track']['id'] not in songLists[playlistDict["Rap"]]:
                    songLists[playlistDict["Rap"]][track['track']['id']]=track['track']['name']
            #PLACE TRACK IN DANCE PLAYLIST
            if audioFeatures["danceability"]>0.67:
                if track['track']['id'] not in songLists[playlistDict["Dance"]]:
                    songLists[playlistDict["Dance"]][track['track']['id']]=track['track']['name']
            #PLACE TRACK IN SAD PLAYLIST
            if audioFeatures["valence"] <0.33:
                if track['track']['id'] not in songLists[playlistDict["Sad"]]:
                    songLists[playlistDict["Sad"]][track['track']['id']]=track['track']['name']
            #PLACE TRACK IN HAPPY PLAYLIST
            if audioFeatures["valence"] >0.67:
                if track['track']['id'] not in songLists[playlistDict["Happy"]]:
                    songLists[playlistDict["Happy"]][track['track']['id']]=track['track']['name']
            #PLACE TRACK IN HIGH ENERGY PLAYLIST
            if audioFeatures["energy"]>0.67:
                if track['track']['id'] not in songLists[playlistDict["High Energy"]]:
                    songLists[playlistDict["High Energy"]][track['track']['id']]=track['track']['name']

#******************************************************************************************************************
    print("finished putting songs in different playlist lists (still haven't been sent to spotify)")
        #for playlist in songLists:
        #print("START OF PLAYLIST")
        #print(playlist)
    #******************************************************************************************************************
    print("going to put songs into playlists")
    
    for id in plIDNameDict:
        #.sort(key=lambda getBPM(spotifyObject)
        #list(songLists[playlistDict[plIDNameDict[id]]].keys()).sort(key=getBPM(spotifyObject), reverse=True)
        #spotifyObjectModify.user_playlist_add_tracks(userID, id,list(songLists[playlistDict[plIDNameDict[id]]].keys()))
        idbpmDict = getBPM(songLists[playlistDict[plIDNameDict[id]]].keys(),spotifyObject)
        sorted(idbpmDict.items(), key=lambda item: item[1],reverse=True)
        addToPlaylist = list(idbpmDict.keys())
        i=0
        while i<=(len(addToPlaylist)//100):
            spotifyObjectModify.user_playlist_add_tracks(userID, id,addToPlaylist[i*100:(i+1)*100])
            i+=1
        i=(len(addToPlaylist)//100) # if len is 50 i = 0, if len is 101 i =1
        while i>=0:
            spotifyObject


if __name__ == '__main__':
    main()
