import cv2
import os
import numpy as np
import tensorflow as tf
import mediapipe as mp
from abc import ABC, abstractmethod
from .bicep import BicepCurlVideoProcessor
from .Front_Side_View_Squat import SquatAnalyzer

class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(name='attention_weight', shape=(input_shape[-1], 1),
                                initializer='random_normal', trainable=True)
        self.b = self.add_weight(name='attention_bias', shape=(input_shape[1], 1),
                                initializer='zeros', trainable=True)
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        e = tf.keras.backend.tanh(tf.keras.backend.dot(x, self.W) + self.b)
        a = tf.keras.backend.softmax(e, axis=1)
        output = x * a
        return tf.keras.backend.sum(output, axis=1)

try:
    tf.keras.utils.get_custom_objects()['AttentionLayer'] = AttentionLayer
    print('custome obj regestered successfully')
except Exception as ex:
    print(f'loading error custom obj {ex}')

class PoseDetectionBase(ABC):

    def __init__(self, config):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=config.get('static_image_mode', False),
            model_complexity=config.get('model_complexity', 1),
            enable_segmentation=config.get('enable_segmentation', False),
            min_detection_confidence=config.get('min_detection_confidence', 0.5),
            min_tracking_confidence=config.get('min_tracking_confidence', 0.5)
        )
        self.model = self.load_model_safely(config['model_path'])
        self.class_names = config['class_names']
        self.MAX_FRAMES = config['max_frames']
        self.STATES = config['states']
        self.current_state = self.STATES[0]  # Start with the first state
        self.exercise_frames = []
        self.indices_to_keep = config['indices_to_keep']

    @abstractmethod
    def process_frame(self, frame):
        pass

    @abstractmethod
    def calculate_angles(self, landmarks):
        pass
    
    def load_model_safely(self, model_path):
        try:
            # Try loading the model using SavedModel format
            keras_path = f'{model_path}_gru_attention_model_full_data_new.keras'
            if os.path.exists(keras_path):
                return tf.keras.models.load_model(keras_path,custom_objects={'AttentionLayer': AttentionLayer})
            else:
                raise FileNotFoundError('keras path error')
        except Exception as e:
            # If loading fails, try to convert the HDF5 model to SavedModel format
            print(f'error msg is {e}')
            print('back to loading h5')
            h5_path = f"{model_path}_GRU_model_full_data.h5"
            if os.path.exists(h5_path):
                return tf.keras.models.load_model(h5_path, compile=False)
            else:
                raise FileNotFoundError(f"Model file not found at {model_path} or {h5_path}")
    
    def make_prediction(self, input_data):
        print('within final step')
        padded_input = tf.keras.preprocessing.sequence.pad_sequences(
            [input_data], maxlen=self.MAX_FRAMES, padding='post', value=999.0
        )
        print('start')
        prediction = self.model.predict(padded_input)
        print('end')
        return prediction[0]

class ShoulderPressPoseDetection(PoseDetectionBase):
    def __init__(self):
        # names = ['Good Job correct form', 'Good Job correct form', 'Good Job correct form']
        names = ['Good Job correct form', 'Lower your hands', 'Raise your hands']
        config = {
            'model_path': os.path.join('server', 'static','models','exercise_classification'),
            'class_names': names,
            'max_frames': 128,
            'states': ['WAITING', 'STARTED', 'RAISED'],
            'indices_to_keep': [11, 12, 13, 14, 15, 16, 23, 24]
        }
        super().__init__(config)
        self.ANGLE_THRESHOLD = 25

    def calculate_angles(self, landmarks):
        def calculate_angle(a, b, c):
            a = np.array(a)
            b = np.array(b)
            c = np.array(c)
            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)
            if angle > 180.0:
                angle = 360 - angle
            return angle

        left_shoulder_angle = calculate_angle(
            [landmarks[23].x, landmarks[23].y],
            [landmarks[11].x, landmarks[11].y],
            [landmarks[13].x, landmarks[13].y]
        )
        right_shoulder_angle = calculate_angle(
            [landmarks[24].x, landmarks[24].y],
            [landmarks[12].x, landmarks[12].y],
            [landmarks[14].x, landmarks[14].y]
        )
        return left_shoulder_angle, right_shoulder_angle

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        # print(f'meadiapipe res: {results}')
        # print(f'meadiapipe res landmarks: {results.pose_world_landmarks}')
        if results.pose_world_landmarks:
            print('hi i am ML model')
            landmarks = results.pose_world_landmarks.landmark
            keypoints = []
            for idx in self.indices_to_keep:
                keypoints.extend([landmarks[idx].x, landmarks[idx].y])

            left_shoulder_angle, right_shoulder_angle = self.calculate_angles(landmarks)
            keypoints.extend([left_shoulder_angle, right_shoulder_angle])

            if self.current_state == self.STATES[0]:  # WAITING
                if left_shoulder_angle < self.ANGLE_THRESHOLD and right_shoulder_angle < self.ANGLE_THRESHOLD:
                    self.current_state = self.STATES[1]  # STARTED
                    self.exercise_frames = [keypoints]
            elif self.current_state == self.STATES[1]:  # STARTED
                self.exercise_frames.append(keypoints)
                if left_shoulder_angle > self.ANGLE_THRESHOLD and right_shoulder_angle > self.ANGLE_THRESHOLD:
                    self.current_state = self.STATES[2]  # RAISED
            elif self.current_state == self.STATES[2]:  # RAISED
                self.exercise_frames.append(keypoints)
                if left_shoulder_angle < self.ANGLE_THRESHOLD and right_shoulder_angle < self.ANGLE_THRESHOLD:
                    if len(self.exercise_frames) > self.MAX_FRAMES:
                        self.exercise_frames = self.exercise_frames[-self.MAX_FRAMES:]
                    print('mL prediction step')
                    prediction = self.make_prediction(self.exercise_frames)
                    predicted_class = self.class_names[np.argmax(prediction)]
                    confidence = np.max(prediction)

                    self.current_state = self.STATES[0]  # Back to WAITING
                    self.exercise_frames = []

                    return {
                        'prediction': predicted_class,
                        'confidence': float(confidence),
                        'state': 'Exercise Completed'
                    }

        return {
            'state': self.current_state
        }

class SquatPoseDetection(PoseDetectionBase):
    def __init__(self):
        config = {
            'model_path': 'path/to/squat_model.h5',
            'class_names': ['correct form', 'too shallow', 'knees over toes'],
            'max_frames': 128,
            'states': ['STANDING', 'DESCENDING', 'BOTTOM'],
            'indices_to_keep': [23, 24, 25, 26, 27, 28]  # Hip, knee, and ankle landmarks
        }
        super().__init__(config)
        self.ANGLE_THRESHOLD = 100  # Example threshold for knee angle

    def calculate_angles(self, landmarks):
        def calculate_angle(a, b, c):
            a = np.array(a)
            b = np.array(b)
            c = np.array(c)
            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)
            if angle > 180.0:
                angle = 360 - angle
            return angle

        left_knee_angle = calculate_angle(
            [landmarks[23].x, landmarks[23].y],  # Left hip
            [landmarks[25].x, landmarks[25].y],  # Left knee
            [landmarks[27].x, landmarks[27].y]   # Left ankle
        )
        right_knee_angle = calculate_angle(
            [landmarks[24].x, landmarks[24].y],  # Right hip
            [landmarks[26].x, landmarks[26].y],  # Right knee
            [landmarks[28].x, landmarks[28].y]   # Right ankle
        )
        return left_knee_angle, right_knee_angle

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        if results.pose_world_landmarks:
            landmarks = results.pose_world_landmarks.landmark
            keypoints = []
            for idx in self.indices_to_keep:
                keypoints.extend([landmarks[idx].x, landmarks[idx].y])

            left_knee_angle, right_knee_angle = self.calculate_angles(landmarks)
            keypoints.extend([left_knee_angle, right_knee_angle])

            if self.current_state == self.STATES[0]:  # STANDING
                if left_knee_angle > self.ANGLE_THRESHOLD and right_knee_angle > self.ANGLE_THRESHOLD:
                    self.current_state = self.STATES[1]  # DESCENDING
                    self.exercise_frames = [keypoints]
            elif self.current_state == self.STATES[1]:  # DESCENDING
                self.exercise_frames.append(keypoints)
                if left_knee_angle < self.ANGLE_THRESHOLD and right_knee_angle < self.ANGLE_THRESHOLD:
                    self.current_state = self.STATES[2]  # BOTTOM
            elif self.current_state == self.STATES[2]:  # BOTTOM
                self.exercise_frames.append(keypoints)
                if left_knee_angle > self.ANGLE_THRESHOLD and right_knee_angle > self.ANGLE_THRESHOLD:
                    if len(self.exercise_frames) > self.MAX_FRAMES:
                        self.exercise_frames = self.exercise_frames[-self.MAX_FRAMES:]

                    prediction = self.make_prediction(self.exercise_frames)
                    predicted_class = self.class_names[np.argmax(prediction)]
                    confidence = np.max(prediction)

                    self.current_state = self.STATES[0]  # Back to STANDING
                    self.exercise_frames = []

                    return {
                        'prediction': predicted_class,
                        'confidence': float(confidence),
                        'state': 'Exercise Completed'
                    }

        return {
            'state': self.STATES[self.current_state]
        }

class PoseDetectionFactory:
    @staticmethod
    def get_pose_detection(exercise_type):
        if exercise_type == 'Lateral_Raises':
            return ShoulderPressPoseDetection()
        elif exercise_type == 'squat':
            return SquatPoseDetection()
        elif exercise_type == 'bicep':
            return BicepCurlVideoProcessor(config)
        elif exercise_type == 'front_squat':
            return SquatAnalyzer.process_video()
        # Add more exercise types here
        else:
            raise ValueError(f"Unsupported exercise type: {exercise_type}")