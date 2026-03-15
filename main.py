from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        },
        'socket_timeout': 30,
    }

    media_items = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                for entry in info['entries']:
                    media_items.append({
                        'media_url': entry.get('url'),
                        'ext': entry.get('ext', 'jpg'),
                        'title': entry.get('title', 'reddit_media')
                    })
            else:
                media_items.append({
                    'media_url': info.get('url'),
                    'ext': info.get('ext', 'jpg'),
                    'title': info.get('title', 'reddit_media')
                })

        return jsonify({'count': len(media_items), 'media': media_items})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
