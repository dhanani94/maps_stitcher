import grequests
import json
import os
import os.path as path
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class TileDownloader(object):
    def __init__(self, tiles_info_dict, output_dir, api_key, style_url=None):
        self.api_key = api_key
        self.config = tiles_info_dict['config']
        self.primary = tiles_info_dict['tiles']['primary']
        self.half = tiles_info_dict['tiles']['half']
        self.output_dir = output_dir
        self.style_url = style_url
        self.base_url = 'https://maps.googleapis.com/maps/api/staticmap'

    def create_url(self, tile):
        url = f'{self.base_url}?{tile["url_param_str"]}&key={self.api_key}'
        if not self.style_url:
            return url
        else:
            query_params = urlparse(self.style_url).query
            for param in query_params.split("&"):
                if param.split("=")[0] == "style":
                    url += f"&{param}"
        return url

    def download(self, redownload=True):
        self.download_tiles(self.primary, redownload=redownload)
        self.download_tiles(self.half, prefix='half-', redownload=redownload)

    def download_tiles(self, tiles, prefix='', batch_size=10, redownload=True):
        for start_index in range(0, len(tiles), batch_size):
            end_index = min(start_index + batch_size, len(tiles))
            batch = tiles[start_index:end_index]

            tile_file_paths = [create_tile_path(self.output_dir, prefix, tile['x'], tile['y']) for tile in batch]
            tile_urls = [self.create_url(tile) for tile in batch]
            logger.info(f'downloading images: {start_index} to {end_index} out of {len(tiles)}')

            if redownload is False:
                filtered_tile_urls = []
                filtered_file_paths = []
                ignore_count = 0
                for index in range(len(tile_file_paths)):
                    if not os.path.exists(tile_file_paths[index]):
                        filtered_file_paths.append(tile_file_paths[index])
                        filtered_tile_urls.append(tile_urls[index])
                    else:
                        ignore_count += 1
                tile_urls = filtered_tile_urls
                tile_file_paths = filtered_file_paths
                if ignore_count > 0:
                    logger.info(f'ignoring {ignore_count} files since already downloaded')

            rs = (grequests.get(url) for url in tile_urls)
            responses = grequests.map(rs)

            for index in range(len(tile_file_paths)):
                response = responses[index]
                tile_file = tile_file_paths[index]
                if response.status_code == 200:
                    with open(tile_file, 'wb') as f:
                        for chunk in response.iter_content():
                            f.write(chunk)
                else:
                    logger.error(response)


def create_tile_path(directory, prefix, x, y):
    return path.join(directory, '{prefix:s}{x:d}x{y:d}'.format(prefix=prefix, x=x, y=y))
