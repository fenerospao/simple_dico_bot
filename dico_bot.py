import discord
from discord import app_commands
from discord import VoiceChannel
from discord.ext import commands,tasks
import discord.voice_state
import yt_download
from bot_embed import youtube_embed
import asyncio
import link_check
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='/',intents=intents)

link_queue = asyncio.Queue()  #음악 링크 대기열
          
async def play_music(vc):
    
    # try:
        # info, interaction = await asyncio.wait_for(link_queue.get(), timeout=10.0)
        # 최대 30초 동안 play_queue에 뭔가 들어올 때까지 기다린다.
    # except asyncio.TimeoutError:
    #     await vc.disconnect()
    #     return
    
    if link_queue.qsize() == 0 :
        print("대기열이 비어있음")
        return

    info, interaction = await link_queue.get()
    res = await yt_download.youtube_download.get_youtube_stream_url(info)

    if res=="ERROR":

        down_fail = discord.Embed(title = ":x: 재생에 실패하였습니다!", color = 0xFF0000)
        await interaction.edit_original_response(content = None, embed=down_fail)
            
        if link_queue.qsize()>0 :
            asyncio.run_coroutine_threadsafe(play_music(vc),bot.loop)
        else:
            return
            
    stream_url = res['url']
    source = discord.FFmpegPCMAudio(stream_url, **yt_download.FFMPEG_OPTIONS)
    vc.play(source, after=lambda e: after_play(vc))

    # 음악 임베드 전송
    yt_embed = youtube_embed.music_embed(res, interaction)
    await interaction.followup.send(embed=yt_embed)

def after_play(vc):
    fut = asyncio.run_coroutine_threadsafe(play_music(vc), bot.loop)
    fut.result()

async def join_channel(interaction):
   
    channel = interaction.user.voice.channel #유저가 접속한 음성채널
    vc = interaction.guild.voice_client #봇이 접속한 음성 채널

    if vc is None:

        vc = await channel.connect()
        await interaction.response.send_message("음성채널에 참여합니다.", ephemeral=False)
        
    elif vc.channel != channel:

        await vc.move_to(channel)
        await interaction.response.send_message("채널을 옮깁니다.", ephemeral=False)

    else:

        await interaction.response.send_message("이미 음성채널에 접속하였습니다.", ephemeral=False)

        

@tasks.loop(seconds=1.0)
async def check_user(interaction:discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients,guild=interaction.guild)

    if voice_client and voice_client.channel:
        vc = voice_client.channel
        if len(vc.members) == 1:
            print("stop checking loop")
            check_user.stop()
            await interaction.guild.voice_client.disconnect()
    else:
        print("stop checking loop")
        check_user.stop()

@bot.event
async def on_ready():

    print("봇 스타트")

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}개의 명령어 동기화")

    except Exception as e:
        print(e)

    await bot.change_presence(activity=discord.Game(name="버터 나비 쫓는 중..."))#봇 상태메시지

@bot.tree.command(name="접속",description="유저가 속한 음성채널에 접속합니다.")
async def join(interaction:discord.Interaction):

    if not interaction.user.voice:

        join_embed = discord.Embed(title=":warning: 먼저 음성 채널에 들어가주세요!", color=0xFF0000)
        await interaction.response.send_message(embed=join_embed, ephemeral=True)
        return

    await join_channel(interaction)

    if not check_user.is_running():
        check_user.start(interaction)
    

@bot.tree.command(name="재생",description="음악을 재생합니다.")
@app_commands.describe(link="유튜브 링크를 입력해주세요.")
async def play(interaction:discord.Interaction, link:str):

    if not interaction.user.voice:

        join_embed = discord.Embed(title=":warning: 먼저 음성 채널에 들어가주세요!", color=0xFF0000)
        await interaction.response.send_message(embed=join_embed, ephemeral=True)
        return
    
    if link_check.check_youtube_link(link)==False:

        err_embed = discord.Embed(title = ":x: 올바르지 않은 링크입니다!", color = 0xFF0000)
        await interaction.response.send_message(embed = err_embed,ephemeral=False)
        return

    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client

    if vc is None:#봇이 음성 채널에 없는 경우

        await join_channel(interaction)
        vc = interaction.guild.voice_client
        await interaction.edit_original_response(content = "음악 준비 중.....")

    elif vc.channel!=channel:#봇의 음성 채널과 유저의 음성 채널이 다를때

        await join_channel(interaction)
        await interaction.edit_original_response(content = "음악 준비 중.....")

    else:#봇과 같은 음성채널일때

        await interaction.response.send_message("음악 준비 중.....",ephemeral=False)

    if not check_user.is_running():
        check_user.start(interaction)
    
    await link_queue.put((link, interaction))

    if not vc.is_playing():
        await play_music(vc)

    else:
        # app_embed = youtube_embed.append_embed(str)
        # #대기열에 음악 추가했음을 알리는 임베드 생성 
        # await interaction.edit_original_response(content = None, embed = app_embed)
        # #음악 준비 중 메시지 수정

        await interaction.edit_original_response(content = f"대기열에 음악이 추가되었습니다.{link}")

bot.run(DISCORD_BOT_TOKEN)