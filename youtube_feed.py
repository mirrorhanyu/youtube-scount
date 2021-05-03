import xmltodict


class YoutubeEntry:
    def __init__(self, youtube_entry):
        self.id = youtube_entry['id']
        self.video_id = youtube_entry['yt:videoId']
        self.video_url = youtube_entry['link']['@href']
        self.title = youtube_entry['title']
        self.author = youtube_entry['author']['name']
        self.published = youtube_entry['published']
        self.updated = youtube_entry['updated']
        self.media_description = youtube_entry['media:group']['media:description'] or ''
        self.media_thumbnail = youtube_entry['media:group']['media:thumbnail']['@url']

    def __str__(self):
        return '''
            id: %s,
            video_id: %s,
            video_url: %s,
            title: %s,
            author: %s,
            published: %s,
            updated: %s,
            media_description: %s,
            media_thumbnail: %s
        ''' % (self.id,
               self.video_id,
               self.video_url,
               self.title,
               self.author,
               self.published,
               self.updated,
               self.media_description,
               self.media_thumbnail)


class YoutubeFeed:
    def __init__(self, youtube_feed_xml):
        self.youtube_feed = xmltodict.parse(youtube_feed_xml)['feed']
        self.channel_id = self.youtube_feed['yt:channelId']
        self.title = self.youtube_feed['title']
        self.author = self.youtube_feed['author']['name']
        self.published = self.youtube_feed['published']
        if isinstance(self.youtube_feed['entry'], list):
            self.entries = [YoutubeEntry(entry) for entry in self.youtube_feed['entry']]
        else:
            self.entries = [YoutubeEntry(self.youtube_feed['entry'])]

    def __str__(self):
        return '''
            youtube_feed: %s,
            channel_id: %s,
            title: %s,
            author: %s,
            published: %s,
            entries: %s,
        ''' % (self.youtube_feed,
               self.channel_id,
               self.title,
               self.author,
               self.published,
               map(str, self.entries)
       )
