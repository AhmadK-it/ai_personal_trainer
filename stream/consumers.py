import uuid 
import os
import aiofiles
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import VideoSession


class VideoConsumerTestedEdition(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = uuid.uuid4()
        self.room_name = f'video_room_{self.room_id}'
        self.room_group_name = f'video_{self.room_name}'
        print(self.room_group_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Ensure the directory exists
            directory = 'video_uploads'
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_path = os.path.join(directory, f'{self.room_id}.webm')
            async with aiofiles.open(file_path, 'ab') as f:
                await f.write(bytes_data)


class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create a new video session and assign a unique room based on its ID
        self.video_session = await sync_to_async(VideoSession.objects.create, thread_sensitive=True)(active=True)
        self.room_name = f'video_room_{self.video_session.session_id}'
        self.room_group_name = f'video_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Set the session to inactive
        await sync_to_async(self.set_session_inactive, thread_sensitive=True)(self.video_session)

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Ensure the directory exists
            directory = 'video_uploads'
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Save file using the video session's session_id
            file_path = os.path.join(directory, f'{self.video_session.session_id}.webm')
            async with aiofiles.open(file_path, 'ab') as f:
                await f.write(bytes_data)

    @staticmethod
    def set_session_inactive(video_session):
        # Mark the session as inactive in the database
        video_session.active = False
        video_session.save()

