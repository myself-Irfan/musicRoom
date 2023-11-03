import logging
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.spotify.com/v1/me/"


def get_usr_tokens(session_key):
    logger.info(f'Searching for {session_key}')
    # filter the SpotifyToken table in user column with session key and return first row
    usr_token = SpotifyToken.objects.filter(user=session_key).first()

    if not usr_token:
        logger.error(f'No object found in SpotifyToken model for {session_key}')

    # return usr_token if has value else None
    return usr_token if usr_token else None


def update_or_create_usr_token(session_key, access_token, token_type, expires_in, refresh_token):
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    try:
        tokens, created = SpotifyToken.objects.update_or_create(
            user=session_key,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in,
                'token_type': token_type
            }
        )

        if created:
            logger.info(f'SpotifyToken for {session_key} was created')
        else:
            print(f'SpotifyToken for {session_key} was updated')

    except Exception as e:
        logger.info(f'Error occured: {e}')


# takes session key from views
def is_spotify_authenticated(session_key):
    token = get_usr_tokens(session_key)

    if token:
        expiry = token.expires_in
        if expiry <= timezone.now():
            new_token = refresh_spotify_token(session_key)
            if not new_token:
                logger.error(f'Failed to refresh spotify token for session key {session_key}')
                return False
        logger.info('Token is yet to expire')
        return True

    logger.error(f'No spotify token found for the provided session key {token}')
    return False


def refresh_spotify_token(session_key):
    refresh_token = get_usr_tokens(session_key).refresh_token

    # api fetch refresh_token
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    if response.status_code != 200:
        logger.error(f'Failed to refresh token for {session_key}\nResponse: {response.json()}')
        return

    response_json = response.json()

    access_token = response_json.get('access_token')
    token_type = response_json.get('token_type')
    expires_in = response_json.get('expires_in')

    # calls function to create or update local model
    update_or_create_usr_token(session_key, access_token, token_type, expires_in, refresh_token)


def execute_spotify_api_request(session_key, endpoint, post_=False, put_=False):
    token = get_usr_tokens(session_key)

    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token.access_token}

    if post_:
        post(BASE_URL + endpoint, headers=header)
    elif put_:
        response = put(BASE_URL + endpoint, headers=header)
    else:
        response = get(BASE_URL + endpoint, {}, headers=header)

    try:
        return response.json()
    except Exception as e:
        logger.error(f'Issue with execute_spotify_api_request {e}')
        return {'Error': f'Issue with execute_spotify_api_request {e}'}


def pause_song(session_id):
    logger.info('Will request to pause')
    return execute_spotify_api_request(session_id, "player/pause", put_=True)


def play_song(session_id):
    logger.info('Will request to play')
    return execute_spotify_api_request(session_id, "player/play", put_=True)


def skip_song(session_id):
    logger.info('Will request to skip')
    return execute_spotify_api_request(session_id, "player/next", post_=True)