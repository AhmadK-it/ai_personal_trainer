import os
import aiofiles
from channels.generic.websocket import AsyncWebsocketConsumer
import uuid 

class VideoConsumer(AsyncWebsocketConsumer):
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