from datetime import datetime, timezone, timedelta
import glob
import os
import re
from itertools import chain

import demoji
import requests
import youtube_dl
from bilibiliupload import Bilibili, VideoPart
from gitdatabase.client import Client
from googletrans import Translator as GoogleTranslator
from retrying import retry
from translate import Translator

from youtube_feed import YoutubeFeed


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=12)
def translate_via_googletrans(text):
    print('start to translate via googletrans', text)
    translator = GoogleTranslator()
    translation = translator.translate(text, dest='zh-CN').text
    print('translate via googletrans: ', translation)
    return translation


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=12)
def translate_via_translate(text):
    print('start to translate via translate', text)
    translator = Translator(from_lang='ko', to_lang="zh")
    translation = translator.translate(text)
    print('translate via translate: ', translation)
    return translation


def translate_to_chinese(text):
    try:
        return translate_via_googletrans(text)
    except:
        return translate_via_translate(text)


def beijing_time():
    utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc.astimezone(timezone(timedelta(hours=8)))


client = Client(os.getenv('REPO'), os.getenv('UESRNAME'), os.getenv('PASSWORD'))


saved_youtube_ids = [saved_youtube.get('id') for saved_youtube in client.saved_youtubes.find({})]

# youtube_feeds_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCuYtwhBPiVI5UiZgT3GEdAw'
# feeds_xml = requests.get(youtube_feeds_url).text

# Velvet Tube 벨벳튜브
# https://www.youtube.com/watch?v=UIFmqSpj8gE


# 'https://www.youtube.com/channel/UC20oe-ECFnuQH8jr-4McArw/videos',

# PDF
# https://gumroad.com/pyoapple

youtube_feeds = [
    # Eunji Pyoapple
    'https://youtube.com/feeds/videos.xml?channel_id=UC9K0rLE1SMh86nVxzkCBpNA',
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
        translated_title = re.sub('[\uac00-\ud7ff]+', '', translate_to_chinese(demoji.replace(entry.title)))
        author = entry.author.encode("ascii", "ignore").decode()
        title = f'#{demoji.replace(author)}# {translated_title}'.replace("ㅣ", "").replace("ㅋㅋ", "")[:80]
        description = translate_to_chinese(demoji.replace(entry.media_description))[:250]
        daily_video_type = 21
        tags = ['生活', '日常', '种草', '颜值', '美女', '写真', '小姐姐', '模特', 'vlog', '韩国', '时尚', '穿搭']
        source = entry.video_url
        ydl.download([f'https://www.youtube.com/watch?v={entry.video_id}'])
        video_path = glob.glob('youtube-download-file*')[0]
        bilibili = Bilibili(os.getenv('BILIBILI_COOKIE', ''))
        with open('youtube-image-file.jpg', 'wb') as file:
            file.write(requests.get(entry.media_thumbnail).content)
        cover = bilibili.cover_up('youtube-image-file.jpg')
        print('start to upload', entry.video_id, title, f' total: {str(round(os.path.getsize(video_path) / (1024 * 1024), 3))}M')
        bilibili.upload(
            parts=[
                VideoPart(
                    path=video_path,
                    title=title,
                    desc=description
                )
            ],
            title=title,
            tid=daily_video_type,
            tag=tags,
            desc=description,
            source=source,
            cover=cover,
            dynamic=''
        )
        client.saved_youtubes.insert_one({
            'id': entry.video_id,
            'author': entry.author,
            'title': entry.title,
            'translated_title': title,
            'uploaded_at': str(beijing_time)
        })
