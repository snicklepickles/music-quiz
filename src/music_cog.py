import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import youtube_dl
from src.song import Song
from thefuzz import fuzz

# TODO fix error msgs and ctx.send()


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = {}
        self.is_paused = {}
        self.queue = {}
        self.queue_index = {}
        self.vc = {}
        self.YTDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.queue[guild.id] = []  # create a queue for each guild
            self.queue_index[guild.id] = 0
            self.vc[guild.id] = None
            self.is_playing[guild.id] = self.is_paused[guild.id] = False
        print(f'{self.bot.user} has connected to Discord!')

    async def join_vc(self, ctx, channel):
        if self.vc[ctx.guild.id] is None or not self.vc[ctx.guild.id].is_connected():
            self.vc[ctx.guild.id] = await channel.connect()
            if self.vc[ctx.guild.id] is None:
                await ctx.send("Failed to join voice channel")
                return
        else:
            await self.vc[ctx.guild.id].move_to(channel)

    # TODO load songs during breaks, not at the start
    def get_songs(self, url):
        result = youtube_dl.YoutubeDL(self.YTDL_OPTIONS).extract_info(url, download=False)
        playlist = []
        for video in result['entries']:
            playlist.append(Song(video['title'], video['uploader'], video['url']))
        return playlist

    async def play_music(self, ctx):
        # Checks if there are any songs remaining in the queue
        if self.queue_index[ctx.guild.id] < len(self.queue[ctx.guild.id]):
            self.is_playing[ctx.guild.id] = True
            self.is_paused[ctx.guild.id] = False

            # First gets the queue for the guild, then gets the song at the index
            song = self.queue[ctx.guild.id][self.queue_index[ctx.guild.id]]

            await self.join_vc(ctx, ctx.user.voice.channel)
            # works up to here

            # FIXME await ctx.response.send_message(embed=song.get_embed())
            player = discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS, executable="C:\\ffmpeg\\ffmpeg.exe")
            self.vc[ctx.guild.id].play(player, after=lambda e: self.play_next(ctx))
        else:
            await ctx.send("Queue is empty")
            self.queue_index[ctx.guild.id] += 1
            self.is_playing[ctx.guild.id] = False

    def play_next(self, ctx):
        if not self.is_playing[ctx.guild.id]:
            return
        if self.queue_index[ctx.guild.id] + 1 < len(self.queue[ctx.guild.id]):
            self.is_playing[ctx.guild.id] = True
            self.queue_index[ctx.guild.id] += 1

            song = self.queue[ctx.guild.id][self.queue_index[ctx.guild.id]]
            # task = ctx.send(embed=song.get_embed())
            # asyncio.run_coroutine_threadsafe(task, self.bot.loop)

            player = discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS, executable="C:\\ffmpeg\\ffmpeg.exe")
            self.vc[ctx.guild.id].play(player, after=lambda e: self.play_next(ctx))
        else:
            self.queue_index[ctx.guild.id] += 1
            self.is_playing[ctx.guild.id] = False

    @app_commands.command(name="ping", description="Ping!")
    async def ping(self, ctx):
        await ctx.response.send_message("Pong!")

    @app_commands.command(name="play", description="Starts a round of music quiz")
    @app_commands.describe(url='Playlist URL')
    async def play(self, ctx, url: str = None):
        if self.is_playing[ctx.guild.id]:
            await ctx.response.send_message("Quiz is already running")
        elif ctx.user.voice:
            embed = discord.Embed(title="Music Quiz", description="Loading songs... get ready!")
            await ctx.response.send_message(embed=embed)
            self.queue[ctx.guild.id] = self.get_songs(url)
            await self.play_music(ctx)
        else:
            await ctx.response.send_message("Please join a voice channel first")

