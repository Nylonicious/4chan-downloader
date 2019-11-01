import asyncio
import pathlib
from sys import version_info
from urllib.parse import urlparse

import aiohttp


async def queue_downloads(url):
    tasks = []
    board = urlparse(url).path.split('/')[1]
    thread_id = urlparse(url).path.split('/')[3]
    desired_path = pathlib.Path.cwd() / thread_id
    desired_path.mkdir(parents=False, exist_ok=True)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'http://a.4cdn.org/{board}/thread/{thread_id}.json') as response:
            data = await response.json()
            for item in data['posts']:
                if 'tim' in item:
                    pictureid = str(item['tim'])
                    extension = item['ext']
                    picture_url = f'https://i.4cdn.org/{board}/{pictureid}{extension}'
                    picture_path = desired_path / f'{pictureid}{extension}'
                    if picture_path.is_file() is False:
                        tasks.append(asyncio.create_task(download(session, picture_url, picture_path)))
            await asyncio.gather(*tasks)


async def download(session, picture_url, picture_path):
    async with session.get(picture_url) as r:
        if r.status == 200:
            picture_path.write_bytes(await r.read())
            print(f'Downloaded {picture_url}')
        else:
            print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urlinput = input('Enter thread URL: ')
    asyncio.run(queue_downloads(urlinput))


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
