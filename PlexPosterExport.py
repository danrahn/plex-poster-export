# Set variables here, otherwise you will be asked them during script run
baseurl = '' # e.g. 'http://127.0.0.1:32400'
token = ''   # e.g. 'abcdef0123456789'

# If you're running this script on a machine other than the one hosting your server, add
# any necessary to:from paths. E.g. if your server is on a Linux machine and your Plex
# media lives under /mnt/data, and that path is mounted on a Windows machine as Z:\, you
# would have:
#
#    path_maps = { 
#        '/mnt/data/' : 'Z:\\' 
#    }
#
# If you have multiple roots mapped to different locations, you can add multiple entries:
#
#    path_maps = {
#        '/mnt/data1/Plex' : 'Y:\\Plex',
#        '/mnt/data2/Movies/' : 'Z:\\'
#    }
path_maps = {
    
}

######################################################################################################
#                                                                                                    #
# - Movie Libraries -> Download poster and place next to video as poster.png                         # 
# - TV Libraries -> Download show poster, place in root folder for show as poster.png                #
#                -> Download season poster and save to season folder as poster.png                   #
#                -> Download episode title card, place next to episode named the same as episode     #
#                                                                                                    #
######################################################################################################

from plexapi.server import PlexServer
from plexapi.utils import download
from plexapi import video
if baseurl == '' and token == '' :
    baseurl = input('What is your Plex URL:  ')
    token = input('What is your Plex Token:  ')
repeat = True
plex = PlexServer(baseurl, token)

def map_path(video_path: str) -> str:
    for src, dst in path_maps.items():
        if video_path.startswith(src):
            video_path = dst + video_path[len(src):]
            src_fwd = src.find('/') != -1
            dst_fwd = dst.find('/') != -1
            if src_fwd != dst_fwd:
                video_path = video_path.replace('/' if src_fwd else '\\', '/' if dst_fwd else '\\')
            break
    return video_path

def get_sep(file_path: str) -> str:
    # Assumes given file includes a path separator
    return '/' if file_path.find('/') != -1 else '\\'

def runScript():
    # list libraries for user to select which to export from
    sectionList = [x.title for x in plex.library.sections()]
    print(" ")
    print ("  Your Libraries: ")
    for i in sectionList:
        print ("      " + str(sectionList.index(i)) + " - " + i)

    selectedLibrary = int(input("Enter the number of the library to export posters from:  "))
    selectedLibraryType = plex.library.section(sectionList[selectedLibrary]).type
    selectedLibraryItems = plex.library.section(sectionList[selectedLibrary]).search()

    if selectedLibraryType == "movie" :
        # loop through movies and export poster
        for video in selectedLibraryItems:
            videoTitle = video.title
            videoPath = video.media[0].parts[0].file
            path_sep = get_sep(videoPath)
            videoFolder = map_path(videoPath.rpartition(path_sep)[0] + path_sep)
            videoPoster = video.thumb
            print("Downloading poster for " + videoTitle + f' (to {videoFolder})')
            posterPath = download(baseurl + videoPoster, token, "poster.png", videoFolder)

    if selectedLibraryType == "show" :
        # loop through tv shows and export main show poster
        for video in selectedLibraryItems:
            showTitle = video.title
            showPath = video.locations
            path_sep = get_sep(showPath[0])
            showFolder = map_path(showPath[0] + path_sep)
            showPoster = video.thumb
            print("Downloading images for " + showTitle)
            posterPath = download(baseurl + showPoster, token, "poster.png", showFolder)
            
            # loop through seasons and export season poster
            for season in video.seasons():
                seasonTitle = season.title
                seasonThumb = season.thumb
                seasonPoster = download(baseurl + seasonThumb, token, seasonTitle + ".png", showFolder)
                
            # now loop through episodes and grab title cards
            for episode in video.episodes() :
                episodeTitle = episode.title
                episodePath = map_path(episode.locations[0].rpartition(path_sep)[0] + path_sep)
                episodeFile = map_path(episode.locations[0][episode.locations[0].rindex(path_sep)+1:][:-4])
                episodeThumb = episode.thumb
                episodeThumbPath = download(baseurl + episodeThumb, token, episodeFile + ".png", episodePath)
    print(" ")
        
while (repeat):
    runScript()
    runagain = input("Would you like to run on another library (y/n)?   ")
    if(runagain != "y"):
        repeat = False
else:
    exit()
