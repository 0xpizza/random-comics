

import io
import json
import random

import requests

from PIL import Image


class Comic():
    def __init__(self, series, title, url, image: Image):
        self.series = series
        self.title = title
        self.url = url
        self.image = image
        

def get_xkcd_comic():
    url = 'https://c.xkcd.com/random/comic/'
    with requests.Session() as sess:
        resp = sess.get(url, allow_redirects=False)
        resp.raise_for_status()
        im_url = resp.next.url
        resp = sess.get(resp.next.url + '/info.0.json')
        resp.raise_for_status()
        try:
            content = json.loads(resp.content)
        except json.decoder.JSONDecodeError as e:
            e.args = (
                'The server returned malformed JSON data:\n\n{}'.format(
                    resp.content),)
            raise e
        img = sess.get(content['img'])
        img = Image.open(io.BytesIO(img.content))
        
        series = 'XKCD'
        title = '#{}: "{}"'.format(
            content.get('num', ''),
            content.get('safe_title', ''),
        )
        return Comic(series, title, im_url, img)
    
def get_random_comic():
    # very diverse yes indeed
    return random.choice((
        get_xkcd_comic,
    ))()