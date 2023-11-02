import asyncio
import re

from TikTokApi import TikTokApi

ms_tokens = [
    'mZ6R-dP4XEbRlthkD97XGYHw4p3r7ZVUN7VrV3llMnbWcSARKApy24l-kOBAoswUqqLCpmVMz8nccJ3NWIWsavPCJGfL6SuuIkRC2Vw1jj9NcpggTuJVXiuirHvkT6b4mQY-zgH_HE2OxG4=',
]


async def fetch_video_max_view(api: TikTokApi, username: str,
                               video_count: int,
                               comment: str) \
        -> list[tuple[str, str, int, str]]:
    """Fetch max views of videos for a TikTok user."""
    result = []
    async for video in api.user(username=username).videos(count=video_count):
        video_stats = video.stats['playCount']
        view = video_stats
        video_url = video.id
        result.append((username, video_url, view, comment))
        await asyncio.sleep(2.5)
    return result


async def info_videos(file_url: str,
                      video_count: int):
    """Fetch and print the max views of videos for TikTok
     users listed in a file.

    Args:
        file_url (str): Path to the file containing TikTok usernames
         or profile links.
        video_count (int): Number of videos to fetch for each user.

    Returns:
        list
    """
    if not file_url:
        print('Выберите файл с аккаунтами!')
        raise FileExistsError(file_url)

    async with (TikTokApi() as api):

        await api.create_sessions(
            num_sessions=3, sleep_after=3, ms_tokens=ms_tokens)
        result = []
        with open(file_url, 'r', encoding='utf8') as file:
            for line in file.readlines():
                line = line.strip()
                match = re.search(r'@([^/]+)', line)

                if match:
                    params = match.group(1).split('#')
                    username = params[0].strip()
                    comment = params[1].strip() if len(params) > 1 else ''

                else:
                    params = line.split('#')
                    username = params[0].strip()
                    comment = params[1].strip() if len(params) > 1 else ''

                try:
                    view_all = await fetch_video_max_view(api=api,
                                                          username=username,
                                                          comment=comment,
                                                          video_count=video_count)
                    result.extend(view_all)
                except Exception as e:
                    return e

        return sorted(result, key=lambda x: x[2], reverse=True)
