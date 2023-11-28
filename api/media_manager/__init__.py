"""Flask API for media manager."""

import logging
import organizer

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST'])
def process_request():
    """Process a POST request and handle photo refactoring."""

    if request.method == 'POST':
        req_body = request.get_json()
        req_type = req_body.get('req_type')

    try:
        logging.info('Flask API received a request.')

        if req_type == 'organize_media_folder':
            result, message = organizer.organize_media()
            if result == 'SUCCESS':
                return jsonify({'message': message}), 200
            else:
                raise ValueError(message)

        else:
            result = 'Unexpected req_type.'
            raise ValueError(result)

    except ValueError as e:
        error_message = f'Media organization failed: {e}, request received: {req_body}.'
        return jsonify({'error': error_message}), 400


if __name__ == '__main__':
    app.run()
