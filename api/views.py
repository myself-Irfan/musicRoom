from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import JsonResponse


# generics.ListAPIView is used to handle HTTP Get requests
class RoomView(generics.ListAPIView):
    # fetches all room objects
    queryset = Room.objects.all()
    # defines the serializer to use
    serializer_class = RoomSerializer


class GetRoom(APIView):
    # defining the parameter to be extracted
    lookup_url_kwargs = 'code'

    # defining GET method
    def get(self, request, format=None):
        # extracting the parameter from the request and saving to a var
        code = request.GET.get(self.lookup_url_kwargs)

        # if code is empty
        if not code:
            return Response({'Bad Request': 'Code parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)

        # retrieves room obj from Room db filtering with code var in code col and if failed, raises 404
        room = get_object_or_404(Room, code=code)
        # converts to JSON
        data = RoomSerializer(room).data
        # if db room host == request session_key then adds a boolean field to JSON data, true if matched else false
        data['is_host'] = self.request.session.session_key == room.host
        # return JSON data with 200 status
        return Response(data, status=status.HTTP_200_OK)


class JoinRoom(APIView):
    # defining parameter to be extracted from the URL
    lookup_url_kwargs = 'code'

    # defining POST method
    def post(self, request, format=None):
        # if user request session does not exist
        if not self.request.session.exists(self.request.session.session_key):
            # create a session
            self.request.session.create()

        # fetch data from URL of request and save to a var
        code = request.data.get(self.lookup_url_kwargs)
        # if code empty
        if not code:
            return Response({'Bad Request': f'Invalid POST request, failed to find {code}'}, status=status.HTTP_400_BAD_REQUEST)

        # fetch room obj from db using code var in code col or raise 404 error if not found
        room = get_object_or_404(Room, code=code)
        # stores the code in user's session as room_code
        self.request.session['room_code'] = code
        return Response({'message': 'Joined room successfully!'}, status=status.HTTP_200_OK)


# APIView is used for all HTTP requests but method must be defined for all request type
class CreateRoomView(APIView):
    # defines the serializer to use
    serializer_class = CreateRoomSerializer

    # definition for POST request
    def post(self, request, format=None):
        # if session does not exist then create a new session for the user
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # passes the incoming HTTP data and serializes it
        serializer = self.serializer_class(data=request.data)

        # if serializer is valid
        if serializer.is_valid():
            # saving converted request data to var
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            # saving request session_keu to var
            host = self.request.session.session_key

            # transaction ensures either all db operation are executed successfully or none
            with transaction.atomic():
                # checks Room db with host
                queryset = Room.objects.filter(host=host)
                # if Room exists for this user
                if queryset.exists():
                    # saving room data
                    room = queryset[0]
                    # updates room properties with the var values
                    room.guest_can_pause = guest_can_pause
                    room.votes_to_skip = votes_to_skip
                    # updates room property with current time
                    room.created_at = timezone.now()
                    # saves the updated fields in db
                    room.save(update_fields=['guest_can_pause', 'votes_to_skip', 'created_at'])
                else:
                    # creates a new instance with var values
                    room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                    # save to db
                    room.save()
            # attaches room code to request session
            self.request.session['room_code'] = room.code
            # return a successful response  with room data that has been converted using RoomSerializer and 201 status
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        # return custom msg with 400 status
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)


class UserInRoom(APIView):
    # def get method
    def get(self, request, format=None):
        # if user request does not have a session
        if not self.request.session.exists(self.request.session.session_key):
            # create a session
            self.request.session.create()

        # python dict with code as a param
        data = {
            'code': self.request.session.get('room_code')
        }

        # return 200 response along with the data converted to JSON
        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    def post(self, request, format=None):
        # fetches room_code attached to the user request session
        room_code = self.request.session.get('room_code')

        # if room_code exists
        if room_code:
            # removes the room_code from the user's session
            self.request.session.pop('room_code')
            # saving the user session_key to a var
            host_id = self.request.session.session_key
            # searching Room model with host_id in host column and fetches the first result
            room = Room.objects.filter(host=host_id).first()

            # if room found
            if room:
                # delete the room the user is holding
                room.delete()
            # return 200 response with custom msg
            return Response({'message': 'Room left successfully'}, status=status.HTTP_200_OK)
        else:
            # return 400 response with custom msg
            return Response({'message': 'Not in a room'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateRoom(APIView):
    # defining serializer to use
    serializer_class = UpdateRoomSerializer

    # defining patch/update request
    def patch(self, request, format=None):
        # if user request session does not exist
        if not self.request.session.exists(self.request.session.session_key):
            # create session for user
            self.request.session.create()

        # conv incoming data
        serializer = self.serializer_class(data=request.data)

        # if data is valid
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            # search with code in Room model and return Room or 404
            room = get_object_or_404(Room, code=code)

            if room.host != request.session.session_key:
                return Response({'error': 'You are not the host of this room'}, status=status.HTTP_403_FORBIDDEN)

            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])

            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        else:
            return Response({'error': "Invalid Data", 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
