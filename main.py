import glob
import os

import requests
import youtube_dl
from bilibiliupload import Bilibili, VideoPart

from youtube_feed import YoutubeFeed

youtube_feeds_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCuYtwhBPiVI5UiZgT3GEdAw'
feeds_xml = requests.get(youtube_feeds_url).text
for entry in YoutubeFeed(feeds_xml).entries[:1]:
    description = entry.media_description[:250]
    with youtube_dl.YoutubeDL({
        'outtmpl': 'youtube-download-file'
    }) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={entry.video_id}'])
        title = f'[Bora] {entry.title}'
        entertainment_video_type = 71
        tags = ['颜值', 'YOUTUBE搬运', '美女', '韩国', '时尚穿搭', '旅行']
        source = 'http://www.youtube.com'
        filepath = glob.glob('youtube-download-file')[0]
        bilibili = Bilibili(os.getenv('BILIBILI_COOKIE', ''))
        bilibili.upload(
            parts=[
                VideoPart(
                    path=filepath,
                    title=entry.title,
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
