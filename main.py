import asyncio
import os
from sys import version_info
from urllib.parse import urlparse

import aiohttp


class ChanDownloader:
    def __init__(self, url):
        self.session = None
        asyncio.run(self.queue_downloads(url))

    async def queue_downloads(self, url):
        tasks = []
        board = urlparse(url).path.split('/')[1]
        thread_id = urlparse(url).path.split('/')[3]
        desiredpath = os.path.join(os.getcwd(), thread_id)
        if not os.path.exists(desiredpath):
            os.makedirs(desiredpath)
        timeout = aiohttp.ClientTimeout(total=60)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as self.session:
            async with self.session.get(f'http://a.4cdn.org/{board}/thread/{thread_id}.json') as response:
                json = await response.json()
            for item in json['posts']:
                if 'tim' in item:
                    pictureid = str(item['tim'])
                    extension = item['ext']
                    picture_url = f'https://i.4cdn.org/{board}/{pictureid}{extension}'
                    picture_path = os.path.join(desiredpath, f'{pictureid}{extension}')
                    if not os.path.isfile(picture_path):
                        tasks.append(asyncio.create_task(self.download(picture_url, picture_path)))
            await asyncio.gather(*tasks)

    async def download(self, picture_url, picture_path):
        async with self.session.get(picture_url) as r:
            if r.status == 200:
                with open(picture_path, 'wb') as f:
                    print(f'Downloading {picture_url}')
                    f.write(await r.read())
            else:
                print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urlinput = input('Enter thread URL: ')
    ChanDownloader(urlinput)


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
