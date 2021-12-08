# -*- coding: utf-8 -*-
"""
@author: Afnan Sultan
"""

#make sure to download the following libraries in advance
import pandas as pd                 # helpful dataframe library
import googleapiclient.discovery    # Google API service, usefull for all Google services
import re                           # regular expression library to clean text

#read a list of videos info. The code for extracting this list is in the 'scrape_video_transcript.py' file
#we only care about the 'title' and 'ID' columns, So, if you have you own list that contains these two info, then pass it directly
df = pd.read_csv('Videos_info.csv')

#extract the two columns that are relevant to this task (the tilte, for naming the output file, and the video ID, for scraping the comments)
videos_url = df[['Title', 'ID']].values.tolist()

def request_comments(video_id):
    '''
    This function takes a tuple (video name and video ID) as input. It passes the ID to google API and retrieves all the top-level comments on a videe,
    excluding the replies on the comments. It returns another tuple (video name, list of comments). 
    '''
    
    #Identify the Google service and the version used. Here, it's youtube.v3
    #You need to replace '$your key' with the API key that you creat through your google account. Here is a link to learn more 
    #https://developers.google.com/youtube/v3/getting-started
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = "$your key")
    
    #this will be as an analogy to scrolling down to load the next set of comments
    nextPageToken = None
    
    #this is where we will store our data for visualisation when needed
    info = []
    
    #The loop will continue as long as 'nextPageToken' is not empty (i.e. untill all comments are retrieved)
    while(1):
        #calling the commentThread function with parameters snippets (i.e comments), load up to 100 comment per page token, video ID and the current page token. 
        request = youtube.commentThreads().list(
        part="snippet,replies",
        maxResults=100,  #prettyPrint = False,
        videoId = video_id[1],
        pageToken = nextPageToken
        )
        
        #calling excute function to convert the request object to a response object that we can iterate over
        res = request.execute()
        
        #get the next page token for the current page,  if available
        nextPageToken = res.get('nextPageToken', None)

        #Identifying the number of comments to iterate over and extract the relevant info
        ncoms =len(res['items'])
        for i in range(0,ncoms):
            
            #this is the path for the fields Comment, date of comment, auther of the comment and number of liked per comment
            com = (res['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'])
            
            #we remove any white spaces (i.e. tabs, new lines) from the comment to avoid problems during outputing to different formats
            clean_com = re.sub('\s+',' ',com)
            
            pubat = (res['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt'])
            auth = (res['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            like = (res['items'][i]['snippet']['topLevelComment']['snippet']['likeCount'])
            
            #store the comment to our list
            info.append([auth, pubat, like, clean_com, "", "", ""])
        
        #when the nextPageToken is empty, the loop will break and the function will return the comments
        if (nextPageToken =="" or nextPageToken == None):
                break

    return(info)

#the next piece is for retrieving comments for multiple videos and writing them to a file. 
#If you are intrested in getting comments for one video only, then, simply call the function on your video tuple diredtly
#e.g. comments = request_comments(['video_name', 'Video_ID']), then convert it to dataframe and write it to a file the same way as mentioned below

#this variable will store all the comments for all the videos we pass to the function (to navigate through in the IDE if you want)
all_comments = []
for vid_id in videos_url:
    #we call our 'request_comments' function and convert the returned list to a pandas dataframe. Which will be easier to visualize and write to a file.
    comments = pd.DataFrame(request_comments(vid_id), columns = ['Name', 'Time', 'Likes', 'Comment'])
    all_comments.append(comments
    
    #this will output the comments for each video to an excel file named by the vidoes title
    writer = pd.ExcelWriter("".join([vid_id[0],'_comments.xlsx']), engine='xlsxwriter')
    comments.to_excel(writer, index=False)
    writer.save() 
                        
    #uncomment the following line to save the files as tab seperated files
    #comments.to_csv("".join([vid_id[0],'_comments.tsv']), sep='\t', index=False)
