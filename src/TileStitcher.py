from PIL import Image
import os.path as path
import logging

logger = logging.getLogger(__name__)


class TileStitcher(object):
    def __init__(self, tiles_path, tiles_info_dict):
        tiles = tiles_info_dict['tiles']

        self.tiles_path = tiles_path
        self.config = tiles_info_dict['config']
        self.primary = tiles['primary']
        self.half = tiles['half']

        last_tile = self.primary[-1]
        self.size = self.config['size'] * self.config['scale']
        self.crop = (0, 0, self.size, self.size - 30 * self.config['scale'])
        self.x_tiles = last_tile['x'] + 1
        self.y_tiles = last_tile['y'] + 1
        self.composite_image = None

    def stitch(self):
        self.composite_image = Image.new('RGB', (self.size * self.x_tiles, self.size * self.y_tiles))
        half_offset = int(-self.size / 2)
        self.combine_tiles(self.composite_image, self.primary)
        self.combine_tiles(self.composite_image, self.half, prefix='half-', offset=half_offset, crop=True)

    def combine_tiles(self, image, tiles, prefix='', offset=0, crop=False):
        for tile in tiles:
            x, y = tile['x'], tile['y']
            tile_image_path = path.join(self.tiles_path, '{prefix:s}{x:d}x{y:d}'.format(x=x, y=y, prefix=prefix))
            img = Image.open(tile_image_path)
            if crop:
                img = img.crop(self.crop)

            image.paste(img, (x * self.size + offset, y * self.size + offset))

    def save_image(self, output_image_path):
        logger.info(f"saving composite image to: {output_image_path}")
        self.composite_image.save(output_image_path)
