import googleapiclient.discovery
import json
import logging
from analysis import sentiment

def sentimentGET(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # For more information about CORS and CORS preflight requests, see:
    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    request_json = request.get_json()
    video_id = None
    if request.args and 'videoId' in request.args:
        video_id = request.args.get('videoId')
    elif request_json and 'videoId' in request_json:
        video_id = request_json['videoId']
    if not video_id:
        return ('videoId is required', 400, headers)
    else:
        comments = _fetchComments(video_id)
        result = sentiment.analyze_sentiment(comments)
        return (json.dumps(result), 200, headers)

def _fetchComments(videoId):
    '''Fetch YouTube comments for the given video'''
    logging.info("YTSGET: Fetching comments for video %s", videoId)

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "API_KEY"  # Obfuscated
    max_results = 100  # Max acceptable value by YT data API

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=max_results,
        order="relevance",  # Same as YouTube watch UI. Default is sort by time reversed.
        textFormat="plainText",
        videoId=videoId
    )
    logging.info("YTSGET: Fetch comments request executing...")
    response = request.execute()
    logging.info("YTSGET: Fetch comments complete")
    comments = [
        item['snippet']['topLevelComment']['snippet']['textDisplay']
        for item in response['items']
    ]
    return comments

    
