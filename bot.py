import os

import colorlog
import discord
import dotenv
from discord.commands import ApplicationContext, Option

try:
    import uvloop
    uvloop.install()
except(ModuleNotFoundError, ImportError):
    pass

colorlog.basicConfig(level="INFO", log_colors={"INFO": "green"})
bot = discord.Bot(
    activity=discord.Activity(name="your audio!", type=discord.ActivityType.listening),
)
connections = {}
dotenv.load_dotenv()


@bot.slash_command()
async def start(
    ctx: ApplicationContext,
    encoding: Option(
        str,
        choices=[
            "mp3",
            "wav",
            "pcm",
            "ogg",
            "mka",
            "mkv",
            "mp4",
            "m4a",
        ],
    ),
):
    """
    Record the audio of people in a Voice Channel!
    """
    voice = ctx.author.voice

    await ctx.defer()

    if not voice:
        return await ctx.send_followup("You're not in a Voice Channel right now")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    if encoding == "mp3":
        sink = discord.sinks.MP3Sink()
    elif encoding == "wav":
        sink = discord.sinks.WaveSink()
    elif encoding == "pcm":
        sink = discord.sinks.PCMSink()
    elif encoding == "ogg":
        sink = discord.sinks.OGGSink()
    elif encoding == "mka":
        sink = discord.sinks.MKASink()
    elif encoding == "mkv":
        sink = discord.sinks.MKVSink()
    elif encoding == "mp4":
        sink = discord.sinks.MP4Sink()
    elif encoding == "m4a":
        sink = discord.sinks.M4ASink()
    else:
        return await ctx.send_followup("Invalid encoding.")

    vc.start_recording(
        sink,
        finished_callback,
        ctx.channel,
    )
    await ctx.guild.get_member(bot.user.id).edit(nick=f"RECORDING | {bot.user.name}")

    await ctx.send_followup("The recording has started!")
    await ctx.send("If you don't want to be recorded, leave the voice channel or mute yourself.")


async def finished_callback(
    sink: discord.sinks.Sink, channel: discord.TextChannel, *args
):
    await sink.vc.disconnect()
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.guild.get_member(bot.user.id).edit(nick=f"{bot.user.name}")
    await channel.send(f"Recording has stopped, here is your audio.", files=files)


@bot.slash_command()
async def stop(ctx: ApplicationContext):
    """
    Stop recording a voice channel.
    """
    await ctx.defer()
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.send_followup("Done, audio will be coming shortly...")
    else:
        await ctx.send_followup("Not recording in this guild.")

bot.run(os.getenv("token"))
