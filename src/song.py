import discord


class Song:
    def __init__(self, title, artist, url):
        self.title = title
        self.artist = artist
        self.url = url

    def get_embed(self):
        embed = discord.Embed(title=self.title, description=self.artist, url=self.url)
        return embed
