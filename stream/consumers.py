import uuid 
import os
import aiofiles
import json
import base64
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as ts
from collections import deque
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
                print(type(bytes_data), self.session_id)
                await self.send({
                    'type': 'server_response',
                    'data': bytes_data
                })
                directory = 'server/static/videos'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                # Save file using the video session's session_id
                file_path = os.path.join(directory, f'{self.session_id}.webm')
                async with aiofiles.open(file_path, 'ab') as f:
                    await f.write(bytes_data)

    
    async def send_json_to_client(self, data):
        await self.send(text_data=json.dumps)
    
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
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'pose_session_{self.session_id}'

        # Validate session_id
        if not await self.is_valid_session(self.session_id):
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Initialize pose detection components
        self.initialize_pose_detection()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f'Disconnection for {self.room_group_name}')

        # Retrieve and deactivate the session
        pose_session = await self.get_pose_session(self.session_id)
        await sync_to_async(self.set_session_inactive)(pose_session)

        # Clean up pose detection components
        self.pose.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            frame_data = text_data_json['frame']
            print(f'data: {frame_data}')
            
            await self.send_json_to_client({'received_data': frame_data})
            # Decode base64 frame data
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame and get results
            results = await self.process_frame(frame)

            # Send the results back to the client
            await self.send_json_to_client(results)

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

    @staticmethod
    async def get_pose_session(session_id):
        return await sync_to_async(VideoSession.objects.get)(session_id=session_id)

    def initialize_pose_detection(self):
        # Load the trained model
        self.model = tf.keras.models.load_model(os.path.join('server', 'static', 'h5','exercise_classification_model_full_data.h5'))

        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False,
                                    min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # Initialize variables for variable-length sliding window
        self.max_window_size = 128
        self.min_window_size = 30
        self.current_window_size = self.min_window_size
        self.frame_buffer = deque(maxlen=self.max_window_size)

        # Mapping of class indices to class names
        self.class_names = ['correct form', 'too high', 'too low']

        # Variables for adaptive window sizing
        self.confidence_threshold = 0.7
        self.low_confidence_count = 0
        self.high_confidence_count = 0

    async def process_frame(self, frame):
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Pose
        results = self.pose.process(rgb_frame)

        if results.pose_world_landmarks:
            keypoints = self.process_landmarks(results.pose_world_landmarks.landmark)

            # Add keypoints to frame buffer
            self.frame_buffer.append(keypoints)

            # Make prediction if we have enough frames
            if len(self.frame_buffer) >= self.current_window_size:
                input_data = list(self.frame_buffer)[-self.current_window_size:]
                prediction = self.make_prediction(input_data)
                predicted_class = self.class_names[np.argmax(prediction)]
                confidence = np.max(prediction)

                # Adjust window size based on prediction confidence
                self.adjust_window_size(confidence)

                return {
                    'prediction': predicted_class,
                    'confidence': float(confidence),
                    'window_size': self.current_window_size
                }

        return None

    def process_landmarks(self, landmarks):
        keypoints = []
        indices_to_keep = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

        for idx in indices_to_keep:
            keypoints.extend([landmarks[idx].x, landmarks[idx].y])

        # Calculate shoulder angles
        left_shoulder_angle = self.calculate_angle(
            [landmarks[23].x, landmarks[23].y],
            [landmarks[11].x, landmarks[11].y],
            [landmarks[13].x, landmarks[13].y]
        )
        right_shoulder_angle = self.calculate_angle(
            [landmarks[24].x, landmarks[24].y],
            [landmarks[12].x, landmarks[12].y],
            [landmarks[14].x, landmarks[14].y]
        )

        # Add angles to keypoints
        keypoints.extend([left_shoulder_angle, right_shoulder_angle])

        return keypoints

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def make_prediction(self, input_data):
        # Pad the input data to max length (128) with 999
        padded_input = tf.keras.preprocessing.sequence.pad_sequences(
            [input_data], maxlen=self.max_window_size, padding='post', value=999.0
        )
        prediction = self.model.predict(padded_input)
        return prediction[0]

    def adjust_window_size(self, confidence):
        if confidence < self.confidence_threshold:
            self.low_confidence_count += 1
            self.high_confidence_count = 0
            if self.low_confidence_count >= 5 and self.current_window_size < self.max_window_size:
                self.current_window_size = min(self.current_window_size + 5, self.max_window_size)
                self.low_confidence_count = 0
        else:
            self.high_confidence_count += 1
            self.low_confidence_count = 0
            if self.high_confidence_count >= 10 and self.current_window_size > self.min_window_size:
                self.current_window_size = max(self.current_window_size - 5, self.min_window_size)
                self.high_confidence_count = 0