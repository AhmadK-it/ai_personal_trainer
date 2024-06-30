import uuid 
import os
import aiofiles
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import VideoSession
from datetime import datetime


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
                print('done creating the folder')
            file_path = os.path.join(directory, f'{self.room_id}.webm')
            async with aiofiles.open(file_path, 'ab') as f:
                print('working')
                await f.write(bytes_data)
                print('working')


class VideoSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        """
        y. this function must be rechecked since the client could call deactivated session 
        y. the client could call the function using any uuid he wants even if the session wasn't created resulting in db failuer
        """
        
        
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'session_{self.session_id}'
        #. Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        

    async def disconnect(self, close_code):
        #. Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f'disconnection for {self.room_group_name}')
        
        #. Retrieve and deactivate the session
        video_session = await self.get_video_session(self.session_id)
        await sync_to_async(self.set_session_inactive)(video_session)
        
    async def receive(self, text_data=None, bytes_data=None):
            if bytes_data:
                # Ensure the directory exists
                directory = 'video_uploads'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    print('created')
                print('already exists')
                # Save file using the video session's session_id
                file_path = os.path.join(directory, f'{self.session_id}.webm')
                print(f'file path : {file_path}')
                async with aiofiles.open(file_path, 'ab') as f:
                    print(f'it is working baby {self.session_id}')
                    await f.write(bytes_data)

    @staticmethod
    def set_session_inactive(video_session):
        # Mark the session as inactive in the database
        video_session.active = False
        video_session.end_time= datetime.now()
        video_session.save()
        
    @staticmethod
    async def get_video_session(session_id):
        # Asynchronously get the video session instance
        return await sync_to_async(VideoSession.objects.get)(session_id=session_id)

