import discord

def get_time(t):
    hour = t//3600
    minute = (t % 3600)//60
    second = (t % 3600) % 60
    
    yt_duration = f"{hour:02d}:{minute:02d}:{second:02d}"
    
    return yt_duration

class youtube_embed:
    def music_embed(youtube_info,interaction):
        yt_embed = discord.Embed(title = f":notes: {youtube_info['title']}", color = 0xFF0000)
        yt_embed.set_author(name = youtube_info['uploader'])
        yt_embed.set_thumbnail(url=youtube_info['thumbnail'])
        yt_embed.add_field(name="곡 길이", value = get_time(youtube_info['duration']),inline = True)
        yt_embed.add_field(name = ":link: 음원", value = "[%s](%s)" % ("링크" , youtube_info['webpage_url']),inline = True)
        yt_embed.set_footer(icon_url = interaction.user.display_avatar, text = f"요청자: {interaction.user.display_name}")
        return yt_embed
    
    def append_embed(youtube_info):
        app_embed = discord.Embed(title = ":dvd: 대기열에 음악을 추가합니다.", color = 0xFF0000)
        app_embed.set_thumbnail(url=youtube_info['thumbnail'])
        app_embed.add_field(name = youtube_info['title'] ,value = "%s" % (youtube_info['webpage_url']), inline = True)
        return app_embed
        