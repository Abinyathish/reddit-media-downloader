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
    }

    media_items = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # Gallery post — multiple images/videos
        if 'entries' in info:
            for entry in info['entries']:
                media_items.append({
                    'media_url': entry.get('url'),
                    'ext': entry.get('ext', 'jpg'),
                    'title': entry.get('title', 'reddit_media')
                })

        # Single image or video
        else:
            media_items.append({
                'media_url': info.get('url'),
                'ext': info.get('ext', 'jpg'),
                'title': info.get('title', 'reddit_media')
            })

    return jsonify({
        'count': len(media_items),
        'media': media_items
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
