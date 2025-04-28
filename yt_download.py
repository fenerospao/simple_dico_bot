import yt_dlp
import asyncio

# FFmpeg 실행 경로
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 16M',
    'executable': "C:/ffmpeg/bin/ffmpeg.exe", 
}

class youtube_download:
    async def get_youtube_stream_url(url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,  # 플레이리스트가 아니라 단일 영상만 로드
            'playlist_items': '1',  # 플레이리스트의 첫 번째 영상만 가져옴
            'quiet': False,  # 불필요한 로그 출력 방지
            'outtmpl': '-',
            'cachedir': False,  # 캐시를 사용하지 않도록 설정 (속도 향상 가능)
            # 'ratelimit': 5000000,
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'N':8,
        }
        loop = asyncio.get_event_loop()
        try:
            
            info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download = False))
            return info
            # info = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download = False)
            # return info
        except:
            errlog = "올바르지 않은 링크"
            return errlog
        

    