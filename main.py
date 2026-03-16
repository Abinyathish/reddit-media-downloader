from flask import Flask, request, jsonify, Response
import requests
import yt_dlp
from urllib.parse import urlparse, parse_qs, unquote

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.reddit.com',
}

def get_reddit_media(url):
    if '/s/' in url:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
        url = r.url
    json_url = url.split('?')[0].rstrip('/') + '.json'
    r = requests.get(json_url, headers=HEADERS, timeout=15)
    data = r.json()
    post = data[0]['data']['children'][0]['data']
    media_items = []
    if 'gallery_data' in post:
        for item in post['gallery_data']['items']:
            media_id = item['media_id']
            meta = post['media_metadata'][media_id]
            ext = meta['m'].split('/')[-1]
            media_url = f"https://i.redd.it/{media_id}.{ext}"
            media_items.append({'media_url': media_url, 'ext': ext, 'title': post.get('title', '')})
    elif post.get('url', '').endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')):
        media_url = post['url']
        ext = media_url.split('.')[-1]
        media_items.append({'media_url': media_url, 'ext': ext, 'title': post.get('title', '')})
    elif post.get('is_video'):
        video_url = post['media']['reddit_video']['fallback_url']
        media_items.append({'media_url': video_url, 'ext': 'mp4', 'title': post.get('title', '')})
    return media_items

def get_instagram_media(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    media_items = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                media_items.append({
                    'media_url': entry.get('url'),
                    'ext': entry.get('ext', 'jpg'),
                    'title': entry.get('title', 'instagram_media')
                })
        else:
            media_items.append({
                'media_url': info.get('url'),
                'ext': info.get('ext', 'jpg'),
                'title': info.get('title', 'instagram_media')
            })
    return media_items

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        if 'instagram.com' in url:
            media_items = get_instagram_media(url)
        else:
            media_items = get_reddit_media(url)
        return jsonify({'count': len(media_items), 'media': media_items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        return Response(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
