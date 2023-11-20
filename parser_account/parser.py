import re

import jinja2
from tiktokpy import TikTokPy


async def fetch_video_max_view(api: TikTokPy, username: str,
                               video_count: int,
                               comment: str) \
        -> list[tuple[str, str, int, str]]:
    """Fetch max views of videos for a TikTok user."""
    result = []
    user_feed_items = await api.user_feed(username=username, amount=video_count)
    for item in user_feed_items:
        view = item.stats.plays
        video_url = item.video.id
        result.append((username, video_url, view, comment))
    return result


async def info_videos(video_count: int):
    """Fetch and print the max views of videos for TikTok
     users listed in a file.

    Args:
        file_url (str): Path to the file containing TikTok usernames
         or profile links.
        video_count (int): Number of videos to fetch for each user.

    Returns:
        list
    """

    async with TikTokPy() as bot:
        result = []
        with open('parser_account/accounts.txt', 'r', encoding='utf8') as file:
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
                    view_all = await fetch_video_max_view(api=bot,
                                                          username=username,
                                                          comment=comment,
                                                          video_count=video_count)
                    result.extend(view_all)
                except Exception as e:
                    return e

        return sorted(result, key=lambda x: x[2], reverse=True)


async def html_code(list_result: list):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates')
    )
    template = env.get_template('index.html')
    render_page = template.render(list_result=list_result)
    with open('result.html', 'w', encoding='utf8') as file:
        file.write(render_page)
