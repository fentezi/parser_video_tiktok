import logging
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
    logging.error(user_feed_items)
    for item in user_feed_items:
        view = item.stats.plays
        video_url = item.video.id
        result.append((username, video_url, view, comment))
    return result


async def info_videos(video_count: int):
    result = []
    with open('parser_account/accounts.txt', 'r', encoding='utf-8') as file:
        lines = file.read().strip().splitlines()
    async with TikTokPy() as bot:
        for line in lines:
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
                view_all = await fetch_video_max_view(api=bot, username=username,
                                                      comment=comment,
                                                      video_count=video_count)
                result.extend(view_all)
            except Exception as e:
                pass

    return sorted(result, key=lambda x: x[2], reverse=True)


def html_code(list_result: list):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates')
    )
    template = env.get_template('index.html')
    render_page = template.render(list_result=list_result)
    with open('result.html', 'w', encoding='utf8') as file:
        file.write(render_page)
    input("Нажмите Enter для выхода")
