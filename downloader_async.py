import asyncio
import json
import os

import aiohttp

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36' \
             ' (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'

TIKTOK_HEADERS = {'user-agent': USER_AGENT}
DOWNLOAD_HEADERS = {'user-agent': 'TelegramBot (like TwitterBot)'}


async def main(link):
    print('Getting direct url with watermark...')
    watermark_url = await get_video_url(link)

    print('Getting direct url without watermark...')
    without_watermark_url = await get_video_wwm_url(watermark_url)

    if without_watermark_url is None:
        print('Seems, this video was published after 27 of July. Can not download this video.')
        return

    print('Downloading the video without watermark')
    file_dir = await download_file(without_watermark_url)
    print('Video downloaded! File directory: {}'.format(file_dir))


async def get_video_url(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=TIKTOK_HEADERS) as get_request:
            get_request_content = await get_request.content.read()
            get_request_json_str = str(get_request_content, 'utf-8').split(
                'application/json" crossorigin="anonymous">')[1].split('</script><script crossorigin')[0]

            result_json = json.loads(get_request_json_str)
            page_json = result_json['props']['pageProps']

            watermark_url = page_json['videoData']['itemInfos']['video']['urls'][0]

            return watermark_url


async def get_video_wwm_url(video_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, headers=TIKTOK_HEADERS) as get_video:
                video_url_content = await get_video.content.read()
                correct_encoding = str(video_url_content, 'CP866')
                vid = correct_encoding.split('vid:')[1][0:32]

                video_url = 'https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={}'.format(vid)

                return video_url

    except Exception as err:
        print(err)
        return None


async def download_file(download_url):
    file_name = download_url.split('=')[1]
    file_dir = 'videos/{}.mp4'.format(file_name)

    if not os.path.exists('videos'):
        os.mkdir('videos')

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url, headers=DOWNLOAD_HEADERS, allow_redirects=True) as get_video:
            with open(file_dir, "wb") as file_stream:
                video_content = await get_video.content.read()
                file_stream.write(video_content)

    return file_dir


if __name__ == '__main__':
    input_url = input('Paste TikTok video url: ')
    asyncio.run(main(input_url))

