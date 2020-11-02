import demoji
import glob
import os

import requests
import youtube_dl
from bilibiliupload import Bilibili, VideoPart
from googletrans import Translator

from database import Database
from youtube_feed import YoutubeFeed

db = Database(
    os.getenv('UESRNAME'),
    os.getenv('PASSWORD'),
    os.getenv('REPO')
)

saved_youtube_ids = [saved_youtube.get('id') for saved_youtube in db.find_all('saved_youtubes')]

youtube_feeds_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCuYtwhBPiVI5UiZgT3GEdAw'
feeds_xml = requests.get(youtube_feeds_url).text

entry = next((entry for entry in YoutubeFeed(feeds_xml).entries if entry.video_id not in saved_youtube_ids), default=None)

if entry is not None:
    description = entry.media_description[:250]
    with youtube_dl.YoutubeDL({
        'outtmpl': 'youtube-download-file'
    }) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={entry.video_id}'])
        demoji.download_codes()
        translator = Translator()
        title = translator.translate(demoji.replace(entry.title), dest='zh-CN').text[:80]
        entertainment_video_type = 71
        tags = ['颜值', 'YOUTUBE搬运', '美女', '韩国', '时尚', '穿搭']
        source = 'http://www.youtube.com'
        filepath = glob.glob('youtube-download-file*')[0]
        bilibili = Bilibili(os.getenv('BILIBILI_COOKIE', ''))
        bilibili.upload(
            parts=[
                VideoPart(
                    path=filepath,
                    title=title,
                    desc=description[:250]
                )
            ],
            title=title,
            tid=entertainment_video_type,
            tag=tags,
            desc=description,
            source=source,
            cover='',
            dynamic=''
        )
        db.save('saved_youtubes', {
            'id': entry.video_id,
            'title': entry.title,
            'translated_title': title
        })
