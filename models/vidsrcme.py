import asyncio
from typing import List, Optional
from fastapi import HTTPException

from superembed import MultiembedExtractor
from vidsrcpro import VidsrcStreamExtractor
from utils import Utilities

class VidsrcMeExtractor:
    BASE_URL = "https://vidsrc.net" # vidsrc.me / vidsrc.in / vidsrc.pm / vidsrc.xyz / vidsrc.net
    RCP_URL = "https://vidsrc.stream/rcp"

    def __init__(self, **kwargs) -> None:
        self.fetch_subtitles = kwargs.get("fetch_subtitles")

    async def get_sources(self, url: str) -> dict:
        req = await asyncio.get_event_loop().run_in_executor(None, requests.get, url)

        if req.status_code != 200:
            
            return {}

        soup = BeautifulSoup(req.text, "html.parser")
        return {source.text: source.get("data-hash") for source in soup.find_all("div", {"class", "server"}) if source.text and source.get("data-hash")}

    async def get_source(self, hash: str, referrer: str) -> dict:
        url = f"{self.RCP_URL}/{hash}"
     

        req = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"Referer": referrer})
        if req.status_code != 200:
          
            return {"stream": None, "subtitle": []}

        soup = BeautifulSoup(req.text, "html.parser")
        encoded = soup.find("div", {"id": "hidden"}).get("data-h")
        seed = soup.find("body").get("data-i") # this is just the imdb id - the "tt" lol

        source = Utilities.decode_src(encoded, seed)
        if source.startswith("//"):
            source = f"https:{source}"

        source_url = await self.get_source_url(source, url)
        if not source_url:

            return {"stream": None, "subtitle": []}

        final_source_url = await self.get_source_url(source_url, url)
        if "vidsrc.stream" in final_source_url:
           

            extractor = VidsrcStreamExtractor()
            return await extractor.resolve_source(url=source_url, referrer=url)

        elif "multiembed.mov" in final_source_url:
            extractor = MultiembedExtractor()
            return await extractor.resolve_source(url=source_url, referrer=url)

        return {"stream": None, "subtitle": []}

    async def get_source_url(self, url: str, referrer: str) -> str:
       
        req = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"Referer": referrer})
        if req.status_code != 302:
            print(f"[VidSrcExtractor] Couldnt find redirect for \"{url}\", status code: {req.status_code}")
            return None

        return req.headers.get("location")

async def vidsrcmeget(dbid: str, s: Optional[int] = None, e: Optional[int] = None, l: str = 'eng') -> List[dict]:
    vse = VidsrcMeExtractor(
        fetch_subtitles=True
    )

    sources = []
    source_names = ["VidSrc PRO", "Superembed"]

    for source_name in source_names:
        source_data = await vse.get_source(dbid, f"https://vidsrc.net/embed/{dbid}")
        sources.append({"name": source_name, "data": source_data})

    return sources
