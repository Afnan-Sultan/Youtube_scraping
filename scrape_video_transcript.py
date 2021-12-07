# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 16:55:34 2021

@author: Afnan Sultan
"""

#make sure to download the following libraries in advance
import youtube_dl   # a library to download a youtube's video, audio, metadata and transcript
import urllib3      # a library that accesses links
import xmltodict    # a that parses xml files
import re           # regular expression library to clean text
import pandas as pd # helpful dataframe library

             # UCfx7haP6UF8aFnv_y2tmsEg is the channel id 
             # you can get a channel ID through this website https://commentpicker.com/youtube-channel-id.php
             # replace C with U to include uploaded videos only
PLAYLIST_ID = 'UUfx7haP6UF8aFnv_y2tmsEg'  # MarvelousQuran Youtube channel

# fetch the metadata for the channel\s video without downloading
# this takes ~30 seconds per video. So, this will take some time to be done according to how many videos you are trying to fetch
with youtube_dl.YoutubeDL({'ignoreerrors': True}) as ydl:
    playd = ydl.extract_info(PLAYLIST_ID, download=False)

#only part of the data extracted is relevant for pulling the transcripts. So, we are going to pick these relevant fields
relevant_info = [] #store all info
videos_url = [] #store videos' links only

#the data we need is under the key (enteries) which is itself a dictionary, so, we loop over it
for video_dict in playd['entries']:
    title = video_dict['title'] # the title of the video
    clean_title = re.sub('\W+','_', title) # a title can contain special chracters that can be problematic in further analysis. 
                                           # Here, we remove any special char (including spaces) and replace it with _. 
    if clean_title[-1] == "_":  #sometimes, the clean title will end with _, which I don't want to be there. So, I am removing it
        clean_title = clean_title[:-1]
    
    url = video_dict['webpage_url'] #the video link
    ID = url.split('=')[1]  #the video ID, which is very important if using youtube API services
    
    videos_url.append([title, url]) #adding the link to our list
    
    # CC referes to youtube's automatic generation of subtitles. If the subtitle is uploaded manually, it gets the value "manual"
    # if CC is generated automatically by youtube, it gets the value "automatic"
    # if CC is disabled, it gets the value "not available"
    cc = "manual"
    
    # the subtitles key exists when a transcript is available, either manually uploaded or automatically generated. 
    # when subtitles has valse > 0, it means that there is and uploaded subtitle
    # when the size ia 0, then an automated CC exisi. and in this case, you can find it generated in several languages
    if 'subtitles' in video_dict.keys():
        if len(video_dict['subtitles'].keys()) > 0:
            # the dictionary will contain different links for different text and xml representatio of the transcript.
            # this path leads to the most readable and preprocessed link
            #sine this channel is in english, the uploaded subtitles has a key set to en-US. this setting maybe change accordingly
            subtitle = video_dict['subtitles']['en-US'][4]['url'] 
        else:
            # For automatic CCs, this path leads to the best xml link to be easily parsed afterwards. 
            # For extracting transcripts for other languages, replace 'en'-which stands for english- with the appropriate abbreviation of that other language.
            # You can navigate through the variable dictionary to check which languages are supported and what is the appropriate abbreviation 
            subtitle = video_dict['automatic_captions']['en'][3]['url'] 
            cc = 'automatic'
    else:
        subtitle = "not available"
        cc = 'not available'
    
    relevant_info.append([clean_title, url, ID, cc, subtitle]) #append all the info we gathered to our list

# now, we convert the list we genreated to pandas dataframe. it will make writing it out to a file easier and prettier
df = pd.DataFrame (relevant_info, columns = ['Title', 'url', 'ID', 'CC', 'Subtitle'])

# save the data to an excel sheet, you can pick different formats by uncommenting any of the following lines
writer = pd.ExcelWriter('Videos_info.xlsx', engine='xlsxwriter') #excel format
df.to_excel(writer, index=False)
writer.save() 
#df.to_csv('Videos_info.csv', index=False) #comma separated format
#df.to_csv('Videos_info.tsv', sep = '\t', index=False) #tab separated format

#now, we extract the actual text of the transcript
transcripts = [] #This will be a variable that you can explore inside the IDE beside the outputted transcripts

# we pick only videos with the values "manual" or "automatic" in the CC column. This meand there's a transcript available
for video in relevant_info:
    if video[2] != "not available":
        clean_title = video[0] # extract title
        
        print('getting transcript for:', clean_title) #an updating statement
        
        url = video[2]  # extract the transcript's link
        http = urllib3.PoolManager() # prepare an http request
        response = http.request('GET', url) # get the content of the transcript's link
        
        # parsing the automatic CCs will be different than parsing manual CCs as the former is in xml format
        if video[3] == 'automatic':
            cc = 'en_automatic_' #will be used for naming the output file. Its specifying the language and pointing that the output file is automatically CCed
            data = response.data #extracting the transcript's xml part from the response object
            data = xmltodict.parse(data) #parsing the xml, which will give a table with the staer, end and text of each timestamp 
            
            # for the file to be appropriately uploaded to a youtube video as a subtitle file, the following needs to be present in the top of the file
            # change en to the language abbreviation you are using
            transcript = ['WEBVTT\nKind: captions\nLanguage: en\n\n']
            
            # for each timestamp, these are the paths that lead to the start, end and text fields. 
            # we extract them and join them together in the appropriate way for a youtube subtitle
            for slot_dict in data['tt']['body']['div']['p']:
                start = slot_dict['@begin'] 
                end = slot_dict['@end']
                if '#text' in slot_dict.keys():
                    text = slot_dict['#text']
                else:
                    text = ""     
                transcript.append("".join([start,' --> ', end, '\n', text, '\n\n']))
        
        else:
            break
        
        # a check up step to make sure we are passing only strings to be written out
        if isinstance(transcript, list):
            transcript = "".join(transcript)
        
        transcripts.append([clean_title,transcript]) #adding the title and transcript to our list variable
        
        # after looping over all the time stamps, we will write the full transcript to a file 
        # the file's name is the same as the the vide name, alongside a prefix that tells if it's a manuall subtitle or automatic, and language of the subtitle
        fOut = open("".join([cc,clean_title,".txt"]), 'w', encoding='utf-8') 
        fOut.write(transcript)
        fOut.close()
