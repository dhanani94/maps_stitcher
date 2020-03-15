Maps Stitcher
=============

Downloads and generates an image of a map given a latitude and longitude bounds. This was largely based off [Haochi's work](https://github.com/haochi/maps_stitcher) and is only slightly modified. 

Environment
-----------

Running this script requires Python, plus some libraries.
You can see the dependencies in the `requirements.txt` file.

I've verified that this works with python 3.8 using a [conda](https://www.anaconda.com/distribution/#download-section) environment

Usage
-----

To use this, there are a few pre-reqs:
* Get an API key from [Google Developers](https://developers.google.com/maps/gmp-get-started#api-key)
    * Specifically using the "Maps Static API"
* Know the latitude, longitude, and zoom variables for the area you want to capture
    * specifically the northeast corner and the southwest corner
* Have python 3.8 enabled (conda, virtualenv, etc.)
* After cloning the repo, be sure to update the `GOOGLE_API_KEY` value in the config/configuration.json file

Actually run the program (example below):
```shell script
git clone git@github.com:dhanani94/maps_stitcher.git
cd maps_stitcher
pip -r requirements.txt
python main.py -c ./config/taufiq_config.json --southwest=42.2964353,-71.1283869 --northeast=42.3711888,-71.0059885 --zoom=16 --scale=2 --dir ./output/boston
```
For more options run `python main.py -h`

## Customising (optional)
Using this [Styling Wizard](https://mapstyle.withgoogle.com/), customize the google map as you please. When you're done, click the "finish" button and `COPY URL`. Then in the config, create a new key called "STYLE_URL" and paste the entire content as a string for the value. 

#### Example

##### Boston:
`python main.py --southwest=42.2764353,-71.1283869 --northeast=42.3911888,-71.0026712 --zoom=16 --scale=2 --dir ./output/boston`
##### San Francisco
`python main.py -southwest=37.708894,-122.502316 --northeast=37.808034,-122.358378 --zoom=15 --scale=2 --dir ./output/san_francisco`
##### Atlanta
`python main.py --southwest=41.8392585,-87.7476355 --northeast=41.9905838,-87.5991916 --zoom=15 --scale=2 --dir ./output/chicago`
##### Chicago 
`python main.py --southwest=41.8392585,-87.7476355 --northeast=41.9905838,-87.5991916 --zoom=15 --scale=2 --dir ./output/chicago`
##### Toronto
`python main.py --southwest=43.5635821,-79.5803259 --northeast=43.7526241,-79.2872906 --zoom=13 --scale=2 --dir ./output/toronto`