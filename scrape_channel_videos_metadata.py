# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 16:55:34 2021

@author: 49157
"""

import youtube_dl
import urllib3
import xmltodict
import re
import pandas as pd

             # UCfx7haP6UF8aFnv_y2tmsEg is the channel id 
             # you can get a channel ID through this website https://commentpicker.com/youtube-channel-id.php
             # replace C with U to include uploaded videos only
PLAYLIST_ID = 'UUfx7haP6UF8aFnv_y2tmsEg'  # MarvelousQuran

with youtube_dl.YoutubeDL({'ignoreerrors': True}) as ydl:
    playd = ydl.extract_info(PLAYLIST_ID, download=False)

relevant_info = []
videos_url = []
for video_dict in playd['entries']:
    title = video_dict['title']
    clean_title = re.sub('\W+','_', title)
    if clean_title[-1] == "_":
        clean_title = clean_title[:-1]
    
    url = video_dict['webpage_url']
    ID = url.split('=')[1]
    videos_url.append([title, url])
    cc = "manual"
    if 'subtitles' in video_dict.keys():
        if len(video_dict['subtitles'].keys()) > 0:
            subtitle = video_dict['subtitles']['en-US'][4]['url']
        else:
            subtitle = video_dict['automatic_captions']['ar'][3]['url']
            cc = 'automatic'
    else:
        subtitle = "not available"
        cc = 'not available'
    
    relevant_info.append([clean_title, url, ID, cc, subtitle])

df = pd.DataFrame (relevant_info, columns = ['Title', 'url', 'ID', 'CC', 'Subtitle'])
df.to_csv('Videos_info.csv')

transcripts = []
data_auto = []
for video in relevant_info:
    if video[2] != "not available":
        clean_title = video[0]
        url = video[2]
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        
        if video[3] == 'automatic':
            cc = 'ar_automatic_'
            data = response.data
            data = xmltodict.parse(data)
            data_auto.append(data)
            transcript = ['WEBVTT\nKind: captions\nLanguage: ar\n\n']
            print(data.keys())

            for slot_dict in data['tt']['body']['div']['p']:
                start = slot_dict['@begin'] 
                end = slot_dict['@end']
                if '#text' in slot_dict.keys():
                    text = slot_dict['#text']
                else:
                    text = ""     
                #transcript.append("".join([start,' --> ', dur, '\n', text, '\n\n']))
                #transcript.append("".join([start, '\n', text, '\n\n']))
                transcript.append("".join([start,' --> ', end, '\n', text, '\n\n']))
        
        else:
            break
            #cc = ""
            #transcript = response.data.decode('utf-8')
        
        
        if isinstance(transcript, list):
            transcript = "".join(transcript)
    
        fOut = open("".join([cc,clean_title,".txt"]), 'w', encoding='utf-8') 
        transcripts.append([clean_title,transcript])
        fOut.write(transcript)
        fOut.close()




