import discord
import youtube_dl
import random

from src.song import Song

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
ytdl_options = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(ytdl_options)


class MusicQuiz:
    def __init__(self, interaction, url):
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.voice_channel = interaction.user.voice.channel
        self.url = url
        self.songs = None
        self.guessed = False
        self.voice_client = None
        self.current_song = None

    async def start(self):
        self.songs = await self.get_songs()
        if self.songs is None:
            await self.voice_channel.send("Playlist contains no songs")
            await self.finish()
        self.voice_client = await self.voice_channel.connect()
        await self.start_playing()

    async def start_playing(self):
        self.current_song = self.songs.pop()
        player = discord.FFmpegPCMAudio(self.current_song.url, **ffmpeg_options, executable="C:\\ffmpeg\\ffmpeg.exe")
        await self.channel.send(embed=self.current_song.get_embed())
        self.voice_client.play(player)
        # self.guessed = False
        # player = discord.FFmpegPCMAudio(self.current_song.url, **ffmpeg_options, executable="C:\\ffmpeg\\ffmpeg.exe")
        # self.voice_client.play(player) # , after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(),
        # # self.guild.loop).result()

    async def play_next(self):
        if len(self.songs) > 0:
            await self.finish()
        else:
            await self.start_playing()

# TODO load songs during breaks, not at the start
    async def get_songs(self):
        result = ytdl.extract_info(self.url, download=False)
        playlist = []
        for video in result['entries']:
            playlist.append(Song(video['title'], video['uploader'], video['url']))
        random.shuffle(playlist)
        return playlist

    async def finish(self):
        await self.voice_client.disconnect()
