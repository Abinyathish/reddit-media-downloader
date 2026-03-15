from flask import Flask, request, jsonify
import requests
from urllib.parse import urlparse, parse_qs, unquote
import re

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def resolve_short_url(url):
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
        return r.url
    except:
        return url

def get_reddit_media(url):
    # Resolve short /s/ links to full URL
    if '/s/' in url:
        url = resolve_short_url(url)

    # Append .json to get post data
    json_url = url.split('?')[0].rstrip('/') + '.json'
    
    r = requests.get(json_url, headers=HEADERS, timeout=15)
    data = r.json()

    post = data[0]['data']['children'][0]['data']
    media_items = []

    # Gallery post (multiple images)
    if 'gallery_data' in post:
        for item in post['gallery_data']['items']:
            media_id = item['media_id']
            meta = post['media_metadata'][media_id]
            ext = meta['m'].split('/')[-1]
            media_url = f"https://i.redd.it/{media_id}.{ext}"
            media_items.append({'media_url': media_url, 'ext': ext, 'title': post.get('title', '')})

    # Single image
    elif post.get('url', '').endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')):
        url = post['url']
        ext = url.split('.')[-1]
        media_items.append({'media_url': url, 'ext': ext, 'title': post.get('title', '')})

    # Video
    elif post.get('is_video'):
        video_url = post['media']['reddit_video']['fallback_url']
        media_items.append({'media_url': video_url, 'ext': 'mp4', 'title': post.get('title', '')})

    return media_items

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        media_items = get_reddit_media(url)
        return jsonify({'count': len(media_items), 'media': media_items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

Also update `requirements.txt` to:
```
flask
requests
