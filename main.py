import requests
import youtube_dl

from youtube_feed import YoutubeFeed

youtube_feeds_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCuYtwhBPiVI5UiZgT3GEdAw'
feeds_xml = requests.get(youtube_feeds_url).text
for entry in YoutubeFeed(feeds_xml).entries[:1]:
    with youtube_dl.YoutubeDL({
        'outtmpl': entry.title
    }) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={entry.video_id}'])
