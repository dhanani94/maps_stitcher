#!/usr/bin/env python

import argparse
import json
import logging
import os
import os.path as path
from pathlib import Path

from src.TileDownloader import TileDownloader
from src.TileMachine import TileMachine
from src.TileStitcher import TileStitcher

logger = logging.getLogger(__name__)


def initialise_logger(logging_mode="INFO"):
    if logging_mode.upper() == "INFO":
        level = logging.INFO
    else:
        level = logging.DEBUG

    date_format = "%Y-%m-%d %H:%M:%S"
    console_log_format = "%(asctime)-13s [%(levelname)s] %(name)-12s: %(message)s"
    stream_log_format = logging.Formatter(fmt=console_log_format, datefmt=date_format)

    main_logger = logging.getLogger("")
    main_logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(stream_log_format)
    main_logger.addHandler(stream_handler)


def main(args, config_data):
    api_key = config_data["GOOGLE_API_KEY"]
    style_url = config_data.get("STYLE_URL")
    tile_info_file = config_data.get("TILE_INFO_FILE", None)

    logger.info(f"initialising project directory: {args.project_dir}")
    Path(args.project_dir).mkdir(parents=True, exist_ok=True)
    tiles_path = path.join(args.project_dir, 'tiles')
    output_image_path = path.join(args.project_dir, f"output.{args.file_type}")

    logger.info("initialising tile counts, offsets, and urls")
    tile_machine = TileMachine(args.size, args.zoom, args.scale, args.maptype, args.south_west,
                               args.north_east)
    tile_machine.calculate_tiles()
    if tile_info_file is not None:
        logger.info(f"saving tile info file to: {tile_info_file}")
        tiles_info_output_file = os.path.join(args.project_dir, tile_info_file)
        tile_machine.save_tile_info(tiles_info_output_file)

    logger.info("downloading tiles")
    Path(tiles_path).mkdir(parents=True, exist_ok=True)
    tile_downloader = TileDownloader(tile_machine.tiles_info_dict, tiles_path, api_key, style_url=style_url)
    tile_downloader.download()

    logger.info("stitching tiles")
    stitcher = TileStitcher(tiles_path, tile_machine.tiles_info_dict)
    stitcher.stitch()
    stitcher.save_image(output_image_path)


if __name__ == '__main__':
    initialise_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', dest='config', default='config/configuration.json',
                        help='file that contains the configuration values')
    parser.add_argument('--zoom', '-z', dest='zoom', type=int, default=1,
                        help='Zoom level between 0 (world) to 21+ (street).')
    parser.add_argument('--scale', dest='scale', type=int, default=1, help='Scale of image (1, 2, 4)')
    parser.add_argument('--size', dest='size', type=int, default=640, help='Size of image')
    parser.add_argument('--maptype', dest='maptype', default='roadmap', help='Map type')
    parser.add_argument('--southwest', dest='south_west', required=True,
                        help='Southwest latitude and longitude. e.g. --southwest=39.1,-83.2')
    parser.add_argument('--northeast', dest='north_east', required=True,
                        help='Northeast latitude and longitude, e.g. --northeast=40.3,-82.4')
    parser.add_argument('--ftype', dest='file_type', default='png', help='Output file type')
    parser.add_argument('--dir', dest='project_dir', default='./output', help='Project directory name')
    args = parser.parse_args()

    logger.info("reading configuration")
    with open(args.config, 'r') as f:
        config_data = json.load(f)

    main(args, config_data)
