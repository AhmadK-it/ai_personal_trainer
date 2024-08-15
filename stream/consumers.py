import uuid 
import aiofiles
import json
import base64
import cv2
import os
import numpy as np
from collections import deque
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import VideoSession
from .pose_detection_init import PoseDetectionFactory
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
                print(type(bytes_data), self.session_id)
                # await self.send(bytes_data)
                directory = 'server/static/videos'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                # Save file using the video session's session_id
                file_path = os.path.join(directory, f'{self.session_id}.webm')
                async with aiofiles.open(file_path, 'ab') as f:
                    await f.write(bytes_data)

    
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
        

class PoseDetectionConsumer(AsyncWebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pose_detection = None
        self.video_writer = None
        self.output_dir = os.path.join('server','static','videos')  # Directory to store videos
        self.frame_count = 0
        self.max_frames = 300  # M
    
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'pose_session_{self.session_id}'

        if not await self.is_valid_session(self.session_id):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        self.pose_detection = None

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pose_session = await self.get_pose_session(self.session_id)
        await sync_to_async(self.set_session_inactive)(pose_session)

        if self.pose_detection:
            self.pose_detection.pose.close()

    # async def receive(self, text_data=None, bytes_data=None):
    #     if text_data:
    #         text_data_json = json.loads(text_data)
    #         if 'exercise_type' in text_data_json:
    #             self.pose_detection = PoseDetectionFactory.get_pose_detection(text_data_json['exercise_type'])
    #             await self.send_json_to_client({'status': 'Pose detection initialized'})
    #         elif 'frame' in text_data_json:
    #             try:
    #                 frame_data = text_data_json['frame']
    #                 # print(f'frame: {frame_data}')
    #                 # frame_bytes = base64.b64decode(frame_data)
    #                 # nparr = np.frombuffer(frame_bytes, np.uint8)
    #                 # frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #                 rgb_frame, frame = self.decode_and_process_frame(frame_data)
                    
    #                 if self.pose_detection:
    #                     if frame is not None:
    #                         results = self.pose_detection.process_frame(frame)
    #                         print(f'results: {results}')
    #                         # Only send back the prediction results, not the entire frame
    #                         await self.send_json_to_client(results)
    #                     else:
    #                         print(f'frame:{frame} rgb: {rgb_frame}')
    #                         await self.send_json_to_client({'error': f'frame is corrupted: {frame_data}'})
    #                 else:
    #                         await self.send_json_to_client({'error': 'Pose detection not initialized'})
    #             except:
    #                 frame_data = text_data_json['frame']
    #                 print(f'frame: within biggest try')
    #                 await self.send_json_to_client({'error': f'frame is corrupted: {frame_data}'})

    async def receive(self, text_data):
        
        if text_data:
            text_data_json = json.loads(text_data)
            # print(text_data_json)
            if 'exercise_type' in text_data_json:
                self.pose_detection = PoseDetectionFactory.get_pose_detection(text_data_json['exercise_type'])
                print('Pose detection initialized')
                await self.send_json_to_client({'status': 'Pose detection initialized'})
            elif 'frame' in text_data_json:
                try:
                    frame_data = text_data_json['frame']
                    
                    _,frame = self.decode_and_process_frame(frame_data)
                    
                    if frame is not None:
                        try:
                            self.write_frame_to_video(frame)
                        except Exception as e:
                            print(f'error with writing video{e}')
                            
                        if self.pose_detection:
                            results = self.pose_detection.process_frame(frame)
                            print(f'results: {results}')
                            await self.send_json_to_client(results)
                        else:
                            await self.send_json_to_client({'error': 'Pose detection not initialized'})
                            print('Pose detection not initialized')
                    else:
                        print('failed to decode YUV420 frame')
                        await self.send_json_to_client({'error': 'Failed to decode frame'})
                except Exception as e:
                    print("f'Error processing frame: {str(e)}'")
                    await self.send_json_to_client({'error': f'Error processing frame: {str(e)}'})


    async def send_json_to_client(self, data):
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def is_valid_session(self, session_id):
        try:
            session = VideoSession.objects.get(session_id=session_id, active=True)
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def set_session_inactive(pose_session):
        pose_session.active = False
        pose_session.end_time = datetime.now()
        pose_session.save()



    def check_image_format(self,frame):
        if not isinstance(frame, np.ndarray):
            print("Error: Frame is not a NumPy array")
            return False
        
        if frame.dtype != np.uint8:
            print("Error: Frame data type is not uint8")
            return False
        
        if len(frame.shape) != 3:
            print("Error: Frame does not have 3 dimensions (height, width, channels)")
            return False
        
        if frame.shape[2] != 3:
            print("Error: Frame does not have 3 color channels")
            return False
        
        return True


    def decode_and_process_frame(self, base64_string):
        try:
            # Decode base64 string
            image_data = base64.b64decode(base64_string)
            print(f"Decoded base64 string. Length: {len(image_data)}")
        except base64.binascii.Error as e:
            print(f"Error: Invalid base64 string: {e}")
            return None, None
        
        try:
            # Convert to NumPy array
            np_array = np.frombuffer(image_data, np.uint8)
            print(f"Converted to NumPy array. Shape: {np_array.shape}")
        except ValueError as e:
            print(f"Error: Could not convert data to NumPy array: {e}")
            return None, None
        
        # Attempt to decode the image
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("Error: Could not decode image data")
            return None, None

        if frame.size == 0:
            print("Error: Decoded frame is empty")
            return None, None
        
        print(f"Decoded frame shape: {frame.shape}")
        
        if not self.check_image_format(frame):
            return None, None

        try:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print(f"Converted to RGB. Shape: {rgb_frame.shape}")
            
        except cv2.error as e:
            print(f"OpenCV Error: {str(e)}")
            return None, None

        return rgb_frame, frame
    

    def write_frame_to_video(self, frame):
        if self.video_writer is None:
            self.initialize_video_writer(frame.shape[1], frame.shape[0])

        self.video_writer.write(frame)
        self.frame_count += 1

        if self.frame_count >= self.max_frames:
            self.close_video_writer()

    def initialize_video_writer(self, width, height):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.session_id}_{timestamp}.mp4"
        filepath = os.path.join(self.output_dir, filename)
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filepath, fourcc, 30.0, (width, height))
        except cv2.error as err:
            print(f'cv writer error {err}')
            
        self.frame_count = 0
        print(f"Initialized video writer: {filepath}")

    def close_video_writer(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            print("Closed video writer")
    
    @database_sync_to_async
    def get_pose_session(self, session_id):
        return VideoSession.objects.get(session_id=session_id)