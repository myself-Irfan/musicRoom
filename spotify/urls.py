from django.urls import path
from .views import *

urlpatterns = [
    path('get_auth_url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('is_authenticated', IsAuthenticated.as_view()),
    path('cur_song', CurSong.as_view()),
    path('pause', PauseSong.as_view()),
    path('play', PlaySong.as_view()),
    path('skip', SkipSong.as_view())
]