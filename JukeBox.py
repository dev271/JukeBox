from tkinter import *
import urllib.parse
import urllib.request
import urllib.error
import requests
import lxml
import pafy
import vlc
from functools import partial
from lxml import etree
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEVELOPER_KEY = 'AIzaSyDSD_5LByfWsJl5yUW0-YHRZXxRClqDSfs'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


class MusicHub:

    def __init__(self, master):

        self.upperFrame = Frame(master)
        self.upperFrame.grid(row=0, column = 1)

        self.lowerFrame = Frame(master, width=600, height=500, bg="white")
        self.lowerFrame.grid(row=1, column = 1)
        self.lowerFrame.grid_propagate(0)

        self.sideFrame = Frame(master, bg='white')
        self.sideFrame.grid(row = 0, column = 0)

        self.llFrame = Frame(master)
        self.llFrame.grid(row = 1, column = 0)

        self.bottomFrame = Frame(master)
        self.bottomFrame.grid(row = 2, column = 0)

        self.label1 = Label(self.upperFrame, text="Song name")
        self.label1.grid(row=0, column=0, sticky=E)

        self.entry1 = Entry(self.upperFrame)
        self.entry1.grid(row=0, column=1)

        self.query = StringVar()
        self.query.set("")
        self.entry1["textvariable"] = self.query

        self.button1 = Button(self.upperFrame, text="Search",
                              command=lambda: self.displayURL(master))
        self.button1.grid(row=0, column=2)

        self.button2 = Button(self.upperFrame, text = "Play all",
                              command = self.playAll)
        self.button2.grid(row = 0, column = 3)

        self.search_videos = []
        self.video_ids = ''
        self.videos = []
        self.playlists = []
        self.getPlaylists()
        self.textToSearch = ''
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()
        self.playlist_player = self.Instance.media_list_player_new()
        self.playlistManager(master)

    def getPlaylists(self):
        playlist_file = open('playlist_file.txt', 'r')
        for playlist in playlist_file.readlines():
            self.playlists.append(playlist[:len(playlist) - 1])

    def displayURL(self, master):
        if (self.query.get() != ""):
            self.textToSearch = self.query.get()
            self.youtube_search(self.textToSearch)
            self.displayOnScreen()

    def displayOnScreen(self):
        for widget in self.lowerFrame.winfo_children():
            widget.destroy()
        i = 0
        for video in self.videos:
            label2 = Label(self.lowerFrame, text=video)
            button2 = Button(self.lowerFrame, text="Play",
                             command=partial(self.playSong, self.search_videos[i]))
            button3 = Button(self.lowerFrame, text = 'Add to playlist',
                             command = partial(self.playlistSubWindow, video, self.search_videos[i]))
            label2.grid(row=i, column=0, sticky=W)
            button2.grid(row=i, column=1)
            button3.grid(row = i, column = 2)
            i = i + 1

    def playSong(self, id):
        video = pafy.new(id)
        bestaudio = video.getbestaudio()
        self.playlist_player.stop()
        self.player.stop()
        Media = self.Instance.media_new(bestaudio.url)
        Media.get_mrl()
        self.player.set_media(Media)
        self.player.play()

    def youtube_search(self, textToSearch):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
            q=textToSearch,
            type='video',
            part='id,snippet',
            maxResults=10
        ).execute()

        self.search_videos = []
        self.videos = []
        self.video_ids = ''

        # Merge video ids
        for search_result in search_response.get('items', []):
            self.search_videos.append(search_result['id']['videoId'])
        self.video_ids = ','.join(self.search_videos)

        # Call the videos.list method to retrieve location details for each video.
        video_response = youtube.videos().list(
            id=self.video_ids,
            part='snippet'
        ).execute()

        # Add each result to the list, and then display the list of matching videos.
        for video_result in video_response.get('items', []):
            self.videos.append('%s' % (video_result['snippet']['title']))

    def addToPlaylist(self, song_name, id, playlist_name):
        if(self.checkInPlaylist(id, playlist_name)):
            playlist_file = open(playlist_name + '.txt', 'a')
            playlist_file.write('%s %s\n' % (song_name, id))
            playlist_file.close()

    def checkInPlaylist(self, id, playlist_name):
        flag = 1
        playlist_file = open(playlist_name + '.txt', 'r')
        for song in playlist_file.readlines():
            song = song[:len(song) - 1]
            i = len(song) - 1
            while 1:
                if song[i] == ' ':
                    break
                i = i - 1
            song_id = song[i + 1:len(song)]
            song_name = song[:i]
            if song_id == id:
                flag = 0
        playlist_file.close()
        return flag

    def checkPlaylist(self, playlist_name):
        flag = 1
        for playlist in self.playlists:
            if playlist_name == playlist:
                flag = 0
        return flag

    def openPlaylist(self, event, playlist_name):
        playlist_file = open(playlist_name + '.txt', 'r')
        self.search_videos = []
        self.videos = []
        self.video_ids = ''
        for song in playlist_file.readlines():
            song = song[:len(song) - 1]
            i = len(song) - 1
            while 1:
                if song[i] == ' ':
                    break
                i = i - 1
            song_id = song[i + 1:len(song)]
            song_name = song[:i]
            self.search_videos.append(song_id)
            self.videos.append(song_name)
        self.displayOnScreen()

    def playAll(self):
        l = self.Instance.media_list_new()
        self.playlist_player.stop()
        self.player.stop()
        for id in self.search_videos:
            print (id)
            video = pafy.new(id)
            bestaudio = video.getbestaudio()
            #l.add_media(self.Instance.media_new(bestaudio.url))
            if(bestaudio != None):
                l.add_media(self.Instance.media_new(bestaudio.url))
        self.playlist_player.set_media_list(l)
        self.playlist_player.play()



    def playlistManager(self, master):
        label2 = Label(self.sideFrame, text = 'Playlists:')
        label2.grid(row = 0, column = 0)
        self.displayPlaylists()
        label3 = Label(self.bottomFrame, text = 'Add new playlist:')
        label3.grid(row = 0, column = 0)
        entry2 = Entry(self.bottomFrame)
        entry2.grid(row = 1, column = 0)
        newplaylist = StringVar()
        newplaylist.set('')
        entry2["textvariable"] = newplaylist
        button3 = Button(self.bottomFrame, text = 'Add', command = partial(self.addNewPlaylist, newplaylist))
        button3.grid(row = 1, column = 1)




    def addNewPlaylist(self, playlist_name):
        file = open('playlist_file.txt', 'a')
        if(playlist_name.get() != '' and self.checkPlaylist(playlist_name.get())):
            file.write('%s\n' % (playlist_name.get()))
            file2 = open(playlist_name.get() + '.txt', 'w+')
            file2.close()
        file.close()
        self.playlists = []
        self.getPlaylists()
        self.displayPlaylists()

    def displayPlaylists(self):
        for widget in self.llFrame.winfo_children():
            widget.destroy()
        i = 0
        for playlist in self.playlists:
            label3 = Label(self.llFrame, text = playlist)
            button3 = Button(self.llFrame, text = 'Remove Playlist',
                             command = partial(self.removePlaylist, playlist))
            label3.bind("<Button-1>", partial(self.openPlaylist, playlist_name = playlist))
            label3.grid(row = i, column = 0, sticky = W)
            button3.grid(row = i, column = 1, sticky = W)
            i = i + 1

    def removePlaylist(self, playlist_name):
        file = open('playlist_file.txt', 'r')
        old_playlists = file.readlines()
        file.close()
        file = open('playlist_file.txt', 'w')
        for playlist in old_playlists:
            if playlist != (playlist_name + '\n'):
                file.write(playlist)
        file.close()
        self.playlists = []
        self.getPlaylists()
        self.displayPlaylists()

    def playlistSubWindow(self, song_name, song_id):
        subwin = Toplevel()
        topFrame = Frame(subwin)
        topFrame.grid(row = 0, column = 0)
        label = Label(topFrame, text = 'Which playlist do you want to add this to?')
        downFrame = Frame(subwin, bg = 'white')
        downFrame.grid(row = 1, column = 0)
        i = 1
        for playlist in self.playlists:
            label3 = Label(downFrame, text = playlist)
            button3 = Button(downFrame, text = 'Add',
                             command = partial(self.addToPlaylist, song_name, song_id, playlist))
            label3.grid(row = i, column = 0, sticky = W)
            button3.grid(row = i, column = 1, sticky = W)
            i = i + 1





root1 = Tk()
m = MusicHub(master=root1)
root1.mainloop()

