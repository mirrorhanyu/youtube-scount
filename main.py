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

entry = next((entry for entry in YoutubeFeed(feeds_xml).entries if entry.video_id not in saved_youtube_ids), None)

if entry is not None:
    with youtube_dl.YoutubeDL({
        'outtmpl': 'youtube-download-file'
    }) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={entry.video_id}'])
        demoji.download_codes()
        translator = Translator()
        translated_title = translator.translate(demoji.replace(entry.title), dest='zh-CN').text
        title = f'#{demoji.replace(entry.author)}# {translated_title}'[:80]
        description = translator.translate(demoji.replace(entry.media_description), dest='zh-CN').text[:250]
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
                    desc=description
                )
            ],
            title=title,
            tid=entertainment_video_type,
            tag=tags,
            desc=description,
            source=source,
            cover=entry.media_thumbnail,
            dynamic=''
        )
        db.save('saved_youtubes', {
            'id': entry.video_id,
            'title': entry.title,
            'translated_title': title
        })
