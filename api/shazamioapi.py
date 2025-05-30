import ssl
import aiohttp
import asyncio
from shazamio import Shazam

async def main():
    # Correct the file path by adding the leading "/"
    path_to_audio = "/Users/otsoreijonen/Downloads/Rarin - YESSIR! (Official Visualizer).mp3"
    
    # Initialize Shazam
    shazam = Shazam()
    
    # Recognize the audio file
    out = await shazam.recognize(path_to_audio)
    print(out)

async def test_ssl():
    url = "https://amp.shazam.com"
    ssl_context = ssl.create_default_context()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url) as response:
            print(response.status)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
asyncio.run(test_ssl())