from django.shortcuts import redirect, get_object_or_404

from api.models import Room
from .models import Vote
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .utils import *

# Create your views here.
BASE_URL = "https://api.spotify.com/v1/me/"

class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        # prepare an URL
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    print(f'Spotify response: {response}')

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_usr_token(session_key=request.session.session_key, access_token=access_token, token_type=token_type, expires_in=expires_in, refresh_token=refresh_token)

    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


class CurSong(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = get_object_or_404(Room, code=room_code)

        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)

        if 'error' in response or 'item' not in response:
            print(f'Found error or no item, {response}')
            return Response({'Message': f'Music may not be playing {response}'}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_str = ""

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_str += ","
            name = artist.get('name')
            artist_str += name

        votes = len(Vote.objects.filter(room=room, song_id= song_id))

        song = {
            'title': item.get('name'),
            'artist': artist_str,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': votes,
            'votes_required': room.votes_to_skip,
            'id': song_id
        }

        self.update_room_song(room, song_id)

        # print(f'Sending song details: {song}')
        return Response(song, status=status.HTTP_200_OK)

    def update_room_song(self, room, song_id):
        cur_song = room.cur_song

        if cur_song != song_id:
            room.cur_song = song_id
            room.save(update_fields=['cur_song'])
            votes = Vote.objects.filter(room=room).delete


class PauseSong(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()

        if self.request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({'Message': 'Song paused...'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'Message': 'User is not host'}, status=status.HTTP_403_FORBIDDEN)


class PlaySong(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()

        if self.request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({'Message': 'Song started...'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'Message': 'User is not host'}, status=status.HTTP_403_FORBIDDEN)


class SkipSong(APIView):
    def post(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()
        votes = Vote.objects.filter(room=room, song_id=room.cur_song)
        votes_needed = room.votes_to_skip

        if self.request.session.session_key == room.host or len(votes)+1 >= votes_needed:
            print('Deleting votes...')
            votes.delete()
            print('Skipping Song...')
            skip_song(room.host)
        else:
            vote = Vote(user=self.request.session.session_key, room=room, song_id=room.cur_song)
            vote.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)