import glob
import os
import re
from itertools import chain

import demoji
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

# youtube_feeds_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCuYtwhBPiVI5UiZgT3GEdAw'
# feeds_xml = requests.get(youtube_feeds_url).text

# Velvet Tube 벨벳튜브
# https://www.youtube.com/watch?v=UIFmqSpj8gE

youtube_feeds = [
    # Eunji Pyoapple
    'https://youtube.com/feeds/videos.xml?channel_id=UC9K0rLE1SMh86nVxzkCBpNA',

    # self add
    'https://youtube.com/feeds/videos.xml?playlist_id=PLaNoH0JqaHZMTi0r_8QoMFIFz0qoxaDSA',

    # Eunji Pyoapple playlists
    'https://youtube.com/feeds/videos.xml?playlist_id=PLP6nl9XHMGoqkmELxBmbdnwE8VEM7ODBg',
    'https://youtube.com/feeds/videos.xml?playlist_id=PLP6nl9XHMGooO-NrfLCD_0O6sChBprsTa',
    # Bora
    'https://youtube.com/feeds/videos.xml?playlist_id=PLwHNaMWjN2CVn77Ya3eCTSNy6FSXDdW5R',
    'https://youtube.com/feeds/videos.xml?playlist_id=PLwHNaMWjN2CW2LwSyV0ceqRLA5mfC1RUr',
    'https://youtube.com/feeds/videos.xml?playlist_id=PLwHNaMWjN2CVv38HJPVmVr5lSnEssjc1J',
    'https://youtube.com/feeds/videos.xml?playlist_id=PLwHNaMWjN2CVNy4Km6Gkb0NfwcDtkkeHV',
]
youtube_feed_entries = [YoutubeFeed(requests.get(feed).text).entries for feed in youtube_feeds]
# entries = [entry for youtube_feed_entry in youtube_feed_entries for entry in youtube_feed_entry]
entries = list(chain.from_iterable(youtube_feed_entries))

entry = next((entry for entry in entries if entry.video_id not in saved_youtube_ids), None)

if entry is not None:
    with youtube_dl.YoutubeDL({
        'outtmpl': 'youtube-download-file'
    }) as ydl:
        demoji.download_codes()
        translator = Translator()
        translated_title = re.sub('[\uac00-\ud7ff]+', '', translator.translate(demoji.replace(entry.title), dest='zh-CN').text)
        author = entry.author.encode("ascii", "ignore").decode()
        title = f'#{demoji.replace(author)}# {translated_title}'.replace("ㅣ", "").replace("ㅋㅋ", "")[:80]
        description = translator.translate(demoji.replace(entry.media_description), dest='zh-CN').text[:250]
        entertainment_video_type = 71
        tags = ['种草', '颜值', '美女', '写真', '小姐姐', '模特', 'vlog', '韩国', '时尚', '穿搭']
        source = entry.video_url
        ydl.download([f'https://www.youtube.com/watch?v={entry.video_id}'])
        video_path = glob.glob('youtube-download-file*')[0]
        bilibili = Bilibili(os.getenv('BILIBILI_COOKIE', ''))
        with open('youtube-image-file.jpg', 'wb') as file:
            file.write(requests.get(entry.media_thumbnail).content)
        cover = bilibili.cover_up('youtube-image-file.jpg')
        print('start to upload', entry.video_id, title)
        bilibili.upload(
            parts=[
                VideoPart(
                    path=video_path,
                    title=title,
                    desc=description
                )
            ],
            title=title,
            tid=entertainment_video_type,
            tag=tags,
            desc=description,
            source=source,
            cover=cover,
            dynamic=''
        )
        db.save('saved_youtubes', {
            'id': entry.video_id,
            'author': entry.author,
            'title': entry.title,
            'translated_title': title
        })
