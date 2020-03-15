import json
import logging
import os
from urllib.parse import urlencode

from src.geo import LatLng, LatLngBounds
from src.geo import Point, Projection

MAX_SIZE = 9999

projection = Projection()
logger = logging.getLogger(__name__)


class Tile(object):
    def __init__(self, x, y, url_param_str):
        self.x = x
        self.y = y
        self.url_param_str = url_param_str

    def __str__(self):
        return self.url_param_str


class TileMachine(object):
    def __init__(self, size, zoom, scale, maptype, south_west, north_east, params=None):
        self.size = size
        self.zoom = zoom
        self.scale = scale
        self.zoom_scale = 1 << self.zoom
        self.maptype = maptype
        self.south_west = south_west
        self.north_east = north_east
        self.bounds = LatLngBounds(south_west, north_east)
        self.tiles_info_dict = None
        # self.extra_params = filter(lambda param: '=' in param, params) #TODO: add support for extra params?

    def calculate_tiles(self):
        primary_tiles = []
        half_way_tiles = []
        max_x = max_y = 0

        params = dict(zoom=self.zoom, scale=self.scale, size='{0}x{0}'.format(self.size),
                      maptype=self.maptype)

        """ generate an (x, y) grid based on the given bounds
            [*][*][*]
            [*][*][*]
        """
        for y in range(MAX_SIZE):
            for x in range(MAX_SIZE):
                if not self.add_tile(self.bounds, x, y, primary_tiles, half_way_tiles, params):
                    max_x = max(max_x, x)
                    break
            if not self.bounds.contains(self.get_latlng_from_tile_at(self.bounds, 0, y)):
                max_y = max(max_y, y)
                break

        """ then use skip_check=True to add (y+1) row and (x+1) column
            [*][*][*][ ]
            [*][*][*][ ]
            [ ][ ][ ][ ]
        """
        for y in range(max_y):
            self.add_tile(self.bounds, max_x, y, None, half_way_tiles, params, skip_check=True)

        for x in range(max_x):
            self.add_tile(self.bounds, x, max_y, None, half_way_tiles, params, skip_check=True)

        self.add_tile(self.bounds, max_x, max_y, None, half_way_tiles, params, skip_check=True)

        self.tiles_info_dict = {
            'config': {
                'zoom': self.zoom,
                'size': self.size,
                'scale': self.scale,
                'southwest': self.south_west,
                'northeast': self.north_east
            },
            'tiles': {
                'primary': [{'url_param_str': tile.url_param_str, 'x': tile.x, 'y': tile.y} for tile in primary_tiles],
                'half': [{'url_param_str': tile.url_param_str, 'x': tile.x, 'y': tile.y} for tile in half_way_tiles]
            }
        }

    def add_tile(self, bounds, x, y, primary_tiles, half_way_tiles, params, skip_check=False):
        latlng = self.get_latlng_from_tile_at(bounds, x, y)
        half_way_latlng = self.get_latlng_half_tile_away(latlng)

        if LatLng.valid_latlng(latlng) and (bounds.contains(latlng) or skip_check):
            if primary_tiles is not None:
                primary_tiles.append(self.latlng_to_tile(latlng, x, y, params))

            if not LatLng.valid_latlng(half_way_latlng):
                half_way_latlng = LatLng.coerce_to_valid_latlng(half_way_latlng)

            if bounds.contains(half_way_latlng) or skip_check:
                half_way_tiles.append(self.latlng_to_tile(half_way_latlng, x, y, params))
            return True

        return False

    def latlng_to_tile(self, latlng, x, y, params):
        url_param_str = self.generate_google_map_param_str_from_latlng(latlng, **params)
        return Tile(x, y, url_param_str)

    def get_latlng_from_tile_at(self, bounds, x, y):
        scale = self.size / float(self.zoom_scale)
        ne = bounds.getNorthEast()
        sw = bounds.getSouthWest()
        top_right = projection.fromLatLngToPoint(ne)
        bottom_left = projection.fromLatLngToPoint(sw)
        point = Point(float(x) * scale + bottom_left.x, float(y) * scale + top_right.y)

        return projection.fromPointToLatLng(point)

    def get_latlng_half_tile_away(self, latlng):
        center = projection.fromLatLngToPoint(latlng)
        half = -self.size / 2.0 / self.zoom_scale
        half_title_away = Point(half + center.x, half + center.y)
        return projection.fromPointToLatLng(half_title_away)

    @staticmethod
    def generate_google_map_param_str_from_latlng(latlng, **kwargs):
        params = dict(center='{0},{1}'.format(latlng.lat, latlng.lng))
        params.update(kwargs)
        return str(urlencode(params))

    def save_tile_info(self, out_file_name):
        logger.info(f"saving file: {out_file_name}")
        with open(out_file_name, 'w') as f:
            json.dump(self.tiles_info_dict, f)
