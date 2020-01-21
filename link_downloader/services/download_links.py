import asyncio
import cgi
import os
import tempfile
from typing import Dict, List, Optional, Tuple
from zipfile import ZipFile

import httpx
from httpx.exceptions import ConnectTimeout, NetworkError, HTTPError


async def download_files_to_zip(urls: List[str]) -> str:
    loop = asyncio.get_event_loop()

    files = [f async for f in download_files(urls)]

    return await loop.run_in_executor(None, write_files_to_zip, files)


def write_files_to_zip(files: List[Tuple[str, bytes]]) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as f:
        with ZipFile(f, 'w') as zipf:
            for filename, content in files:
                zipf.writestr(filename, content)

        return f.name


async def remove_tempfile(file_path: str) -> None:
    os.remove(file_path)


async def download_files(urls: List[str]) -> List[Tuple[str, bytes]]:
    async with httpx.AsyncClient(timeout=10) as client:
        futures = [
            client.get(url)
            for url in urls
        ]
        for future in asyncio.as_completed(futures):
            try:
                response = await future
                response.raise_for_status()
            except (NetworkError, ConnectTimeout, HTTPError):
                continue  # TODO: return an error message to the client

            filename = get_filename(response)
            yield (filename, response.content)


def get_filename(response) -> str:
    return (
        get_filename_from_headers(response.headers) or
        get_filename_from_url(response.url) or
        f'file_from_{response.url}'
    )


def get_filename_from_headers(headers: Dict[str, str]) -> Optional[str]:
    disposition = headers.get('Content-Disposition')

    if disposition:
        value, params = cgi.parse_header(disposition)
        return (value == 'attachment') and params.get('file')


def get_filename_from_url(url: httpx.URL) -> str:
    return url.path.split('/')[-1]
