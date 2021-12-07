import pandas as pd
import googleapiclient.discovery
import re


df = pd.read_csv('Videos_info.csv')
videos_url = df[['Title', 'ID']].values.tolist()

def request_comments(video_id):
    #print(title)
    #fOut = open("".join([video_id[0], "_comments.tsv"]), 'w', encoding='utf-8')
    #fOut.write("Name\tTime\tComment\rReply by\tReply time\tReply\n")
    #fOut.write("Name\tTime\tComment\n")
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = "AIzaSyBQIuTIfVJQBrnB8ZPC5yyjVYknQ0Bb548")
    nextPageToken = None
    info = []
    while(1):
        request = youtube.commentThreads().list(
        part="snippet,replies",
        maxResults=100,  #prettyPrint = False,
        videoId = video_id[1],
        pageToken = nextPageToken
        )
        res = request.execute()
        nextPageToken = res.get('nextPageToken', None)

        #for key in res.keys():
        ncoms =len(res['items'])
        for i in range(0,ncoms):
            com = (res['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'])#.replace('\n', ' ').replace('\t', ' ')
            clean_com = re.sub('\s+',' ',com)
            pubat = (res['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt'])
            auth = (res['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            like = (res['items'][i]['snippet']['topLevelComment']['snippet']['likeCount'])
            #output = "\t".join([auth, pubat, clean_com, '\n'])
            #info.append([auth, pubat, like, clean_com])
            info.append([auth, pubat, like, clean_com, "", "", ""])
            #fOut.write(output)

            if(res['items'][i]['snippet']['totalReplyCount']) > 0:
                parent = res['items'][i]['snippet']['topLevelComment']['id']
                nextPageTokenRep = None
                while(1):
                   request2 = youtube.comments().list(
                       part = 'snippet', 
                       id = video_id[1], 
                       #maxResults = 100, 
                       pageToken = nextPageTokenRep,
                       parentId = parent)
                   data2 = request2.execute()
                   nextPageTokenRep = data2.get('nextPageTokenRep');
                   nreplies = len(data2['items'])
                   for j in range(nreplies, -1, -1):
                       rpauth = data2['items'][j]['snippet']['authorDisplayName']
                       rpcom = data2['items'][j]['snippet']['textDisplay']
                       rppubat = data2['items'][j]['snippet']['publishedAt']
                       #data2.items[i].snippet.updatedAt]);
                       #fOut.write("\t".join(['\t\t',rpauth, rpcom, rppubat, '\n' ]))
                       info.append(["", "", "", "", rpauth, rppubat, rpcom])
                   if (nextPageTokenRep =="" or nextPageTokenRep == None):
                       break
                 
        if (nextPageToken =="" or nextPageToken == None):
                break

    return(info)

all_comments = []
for vid_id in videos_url[0]:
    comments = pd.DataFrame(request_comments(vid_id), columns = ['Name', 'Time', 'Likes', 'Comment'])
    all_comments.append(comments)
    #comments.to_csv("".join([vid_id[0],'.tsv']), sep='\t', index=False)
    
    writer = pd.ExcelWriter("".join([vid_id[0],'.xlsx']), engine='xlsxwriter')
    #comments.to_excel(writer, index=False)
    #writer.save() 
