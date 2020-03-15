import grequests
import json
import os
import os.path as path
import logging

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

        # self.skip = skip #TODO: implement later

    def create_url(self, tile):
        url = f'{self.base_url}?{tile["url_param_str"]}&key={self.api_key}'
        # todo: add in style url stuff too
        return url

    def download(self):
        self.download_tiles(self.primary)
        self.download_tiles(self.half, prefix='half-')

    def download_tiles(self, tiles, prefix='', batch_size=10):
        for start_index in range(0, len(tiles), batch_size):
            end_index = min(start_index + batch_size, len(tiles))
            batch = tiles[start_index:end_index]
            logger.debug(f'working with batch_size: {len(batch)}')

            tile_file_paths = [create_tile_path(self.output_dir, prefix, tile['x'], tile['y']) for tile in batch]
            tile_urls = [self.create_url(tile) for tile in batch]
            rs = (grequests.get(url) for url in tile_urls)
            responses = grequests.map(rs)

            for index in range(len(batch)):
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
