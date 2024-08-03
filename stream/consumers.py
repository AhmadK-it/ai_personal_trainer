import uuid 
import os
import aiofiles
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import VideoSession
from datetime import datetime
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

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
        # Validate session_id
        if not await self.is_valid_session(self.session_id):
            await self.close()
            return        
        
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
                directory = 'server/static/videos'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    print('created')
                print('already exists')
                # Save file using the video session's session_id
                file_path = os.path.join(directory, f'{self.session_id}.webm')
                print(f'file path : {file_path}, session: {self.session_id}')
                async with aiofiles.open(file_path, 'ab') as f:
                    await f.write(bytes_data)
    
    @database_sync_to_async
    def is_valid_session(self, session_id):
        # Implement your session validation logic here
        # For example:
        try:
            session = VideoSession.objects.get(session_id=session_id, active=True)
            return True
        except ObjectDoesNotExist:
            return False
        

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

class JSONSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_name = f'json_session_{self.session_id}'
        
        # Validate session_id
        if not await self.is_valid_session(self.session_id):
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        
        # Deactivate the session
        session = await self.get_session(self.session_id)
        await sync_to_async(self.deactivate_session)(session)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'client_data':
                # Process the received data
                processed_data = await self.process_client_data(text_data_json.get('data'))
                
                # Send processed data back to the client
                await self.send_json_to_client({
                    'type': 'server_response',
                    'data': processed_data
                })
            else:
                await self.send_json_to_client({
                    'type': 'error',
                    'message': 'Unknown message type'
                })
        except json.JSONDecodeError:
            await self.send_json_to_client({
                'type': 'error',
                'message': 'Invalid JSON format'
            })

    async def send_json_to_client(self, data):
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def is_valid_session(self, session_id):
        # Implement your session validation logic here
        # For example:
        try:
            session = VideoSession.objects.get(session_id=session_id, active=True)
            return True
        except ObjectDoesNotExist:
            return False
        

    # @database_sync_to_async
    # def deactivate_session(self, session_id):
    #     video_session = await self.get_video_session(session_id)
    #     await sync_to_async(self.set_session_inactive)(video_session)
        
        
    @staticmethod
    def deactivate_session(video_session):
        # Mark the session as inactive in the database
        video_session.active = False
        video_session.end_time= datetime.now()
        video_session.save()
        
    @staticmethod
    async def get_session(session_id):
        # Asynchronously get the video session instance
        return await sync_to_async(VideoSession.objects.get)(session_id=session_id)

    async def process_client_data(self, data):
        # Implement your data processing logic here
        # This is where you would handle the received data and generate a response
        
        processed_data = {'result': f'hey yoo {data["name"]}'}
        return processed_data
        