# serializers convert a django model instance to python data type

from rest_framework import serializers
from .models import Room


# defining RoomSerializer
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        # defining Room as model for this class
        model = Room
        # specifying fields to be included in the output
        fields = ('id', 'code', 'host', 'guest_can_pause', 'votes_to_skip', 'created_at')


class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('guest_can_pause', 'votes_to_skip')


class UpdateRoomSerializer(serializers.ModelSerializer):
    # only characters, using this since model has a unique=True constraint
    code = serializers.CharField(validators=[])

    class Meta:
        model = Room
        fields = ('guest_can_pause', 'votes_to_skip', 'code')