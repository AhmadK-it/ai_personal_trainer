import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass, field

@dataclass
class SquatMetrics:
    rep_count: int = 0
    correct_rep_count: int = 0
    bad_rep_count: int = 0
    lowest_angle: float = float('inf')
    knees_too_close: bool = False
    feet_too_wide: bool = False
    asymmetric_squat: bool = False
    insufficient_depth: bool = False
    extended_knee: bool = False
    ankle_raised: bool = False
    back_rounded: bool = False
    knees_caving_in: bool = False
    bad_rep_feedback: list = field(default_factory=list)

class SquatCounter:
    def __init__(self, config):
        self.config = config
        self.metrics = SquatMetrics()
        self.angle_history = []
        self.direction = None
        self.initial_hip_height = None
        self.lowest_hip_height = float('inf')
        self.initial_ankle_position = None
        self.viewpoint = None
        self.view_buffer = []
        self.initial_hip_shoulder_ratio = None

    def determine_viewpoint(self, landmarks):
        left_hip = np.array(landmarks['left_hip'])
        right_hip = np.array(landmarks['right_hip'])
        left_shoulder = np.array(landmarks['left_shoulder'])
        right_shoulder = np.array(landmarks['right_shoulder'])

        hip_distance = np.linalg.norm(left_hip - right_hip)
        shoulder_distance = np.linalg.norm(left_shoulder - right_shoulder)
        hip_shoulder_ratio = hip_distance / shoulder_distance

        if self.initial_hip_shoulder_ratio is None:
            self.initial_hip_shoulder_ratio = hip_shoulder_ratio

        ratio_change = hip_shoulder_ratio / self.initial_hip_shoulder_ratio

        if 0.9 <= ratio_change <= 1.1:
            return 'front'
        else:
            return 'side'

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def update(self, landmarks):
        current_viewpoint = self.determine_viewpoint(landmarks)
        self.view_buffer.append(current_viewpoint)

        if len(self.view_buffer) < 30:
            current_viewpoint = self.view_buffer[0]

        front_count = self.view_buffer.count('front')
        side_count = self.view_buffer.count('side')

        if side_count < front_count:
            metrics = self.update_front_view(landmarks)
        else:
            metrics = self.update_side_view(landmarks)

        if len(self.view_buffer) > 30:
            self.view_buffer.pop(0)

        return metrics

    def provide_real_time_feedback(self, frame, metrics):
        feedback = []

        if self.viewpoint == 'front':
            if metrics[1]:  
                feedback.append("Keep your knees in line with your toes.")
            if metrics[2]:  
                feedback.append("Bring your feet closer together.")
            if metrics[3]:  
                feedback.append("Try to squat evenly on both legs.")
            if metrics[4]:  
                feedback.append("Try to squat deeper if comfortable.")
        else:
            if metrics[0] > self.config['hip_knee_ankle_threshold']:  
                feedback.append("Try to lower your hips more.")
            if self.metrics.extended_knee:
                feedback.append("Keep your knees behind your toes.")
            if self.metrics.ankle_raised:
                feedback.append("Keep your heels on the ground.")
            if self.metrics.back_rounded:
                feedback.append("Keep your back straight.")

        if feedback:
            cv2.putText(frame, "Real-time feedback:" + "\n" + "\n".join(feedback), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
        else:
            cv2.putText(frame, "Good Work", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)

    def update_front_view(self, landmarks):
        left_hip, right_hip = landmarks['left_hip'], landmarks['right_hip']
        left_knee, right_knee = landmarks['left_knee'], landmarks['right_knee']
        left_ankle, right_ankle = landmarks['left_ankle'], landmarks['right_ankle']

        left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        avg_angle = (left_angle + right_angle) / 2

        self.check_form_front(landmarks, left_angle, right_angle)
        self.update_rep_count(avg_angle)

        return self.get_metrics()

    def update_side_view(self, landmarks):
        hip, knee, ankle = landmarks['right_hip'], landmarks['right_knee'], landmarks['right_ankle']
        toe, shoulder, opposite_knee = landmarks['right_toe'], landmarks['right_shoulder'], landmarks['left_knee']

        angle = self.calculate_angle(hip, knee, ankle)
        back_angle = self.calculate_angle(shoulder, hip, knee)

        self.check_form_side(angle, back_angle, knee, ankle, toe, opposite_knee)
        self.update_rep_count(angle)

        return self.get_metrics()

    def check_form_front(self, landmarks, left_angle, right_angle):
        left_knee, right_knee = landmarks['left_knee'], landmarks['right_knee']
        left_ankle, right_ankle = landmarks['left_ankle'], landmarks['right_ankle']
        left_hip, right_hip = landmarks['left_hip'], landmarks['right_hip']

        knee_distance = np.linalg.norm(np.array(left_knee) - np.array(right_knee))
        ankle_distance = np.linalg.norm(np.array(left_ankle) - np.array(right_ankle))
        self.metrics.knees_too_close = knee_distance < ankle_distance * self.config['knee_distance_threshold']

        hip_distance = np.linalg.norm(np.array(left_hip) - np.array(right_hip))
        self.metrics.feet_too_wide = ankle_distance > hip_distance * self.config['feet_width_threshold']

        self.metrics.asymmetric_squat = abs(left_angle - right_angle) > self.config['asymmetry_threshold']

        current_hip_height = (left_hip[1] + right_hip[1]) / 2
        if self.initial_hip_height is None:
            self.initial_hip_height = float('inf')
        self.initial_hip_height = max(self.initial_hip_height, current_hip_height)
        self.lowest_hip_height = min(self.lowest_hip_height, current_hip_height)

        hip_drop = (self.initial_hip_height - current_hip_height) / self.initial_hip_height
        max_hip_drop = (self.initial_hip_height - self.lowest_hip_height) / self.initial_hip_height

        self.metrics.insufficient_depth = hip_drop < self.config['depth_threshold'] * max_hip_drop

    def check_form_side(self, angle, back_angle, knee, ankle, toe, opposite_knee):
        self.metrics.back_rounded = back_angle < self.config['back_round_threshold']

        knee_distance = np.linalg.norm(np.array(knee) - np.array(opposite_knee))
        ankle_distance = np.linalg.norm(np.array(ankle) - np.array(toe))
        self.metrics.knees_caving_in = knee_distance < ankle_distance * self.config['knee_caving_threshold']

        self.metrics.extended_knee = knee[0] > toe[0]

        if self.initial_ankle_position is None:
            self.initial_ankle_position = ankle[1]
        elif ankle[1] < self.initial_ankle_position - self.config['ankle_raise_threshold']:
            self.metrics.ankle_raised = True

    def update_rep_count(self, angle):
        self.angle_history.append(angle)
        if len(self.angle_history) > self.config['window_size']:
            self.angle_history.pop(0)

        if len(self.angle_history) == self.config['window_size']:
            mean_angle = np.mean(self.angle_history)
            self.metrics.lowest_angle = min(self.metrics.lowest_angle, mean_angle)

            if self.direction is None and mean_angle < self.config['threshold_down']:
                self.direction = 'down'
            elif self.direction == 'down' and mean_angle > self.config['threshold_up']:
                self.complete_rep()
            elif self.direction == 'up' and mean_angle < self.config['threshold_down']:
                self.direction = 'down'

    def complete_rep(self):
        self.direction = 'up'
        self.metrics.rep_count += 1
        if self.is_correct_rep():
            self.metrics.correct_rep_count += 1
        else:
            self.metrics.bad_rep_count += 1
            self.metrics.bad_rep_feedback.append(self.get_metrics())

    def is_correct_rep(self):
        return (not self.metrics.knees_too_close and not self.metrics.feet_too_wide and not self.metrics.asymmetric_squat and not self.metrics.insufficient_depth)

    def get_metrics(self):
        return (self.metrics.lowest_angle,
                self.metrics.knees_too_close,
                self.metrics.feet_too_wide,
                self.metrics.asymmetric_squat,
                self.metrics.insufficient_depth,
                self.metrics.back_rounded,
                self.metrics.knees_caving_in,
                self.metrics.extended_knee,
                self.metrics.ankle_raised)

class SquatAnalyzer:
    def __init__(self, video_path, config):
        self.video_path = video_path
        self.config = config
        self.squat_counter = SquatCounter(config)
        self.cap = self.initialize_video_capture(video_path)
        self.pose = self.initialize_mediapipe()

    def initialize_mediapipe(self):
        mp_pose = mp.solutions.pose
        return mp_pose.Pose(static_image_mode=False, model_complexity=1,
                            enable_segmentation=False, min_detection_confidence=0.5)

    def initialize_video_capture(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")
        return cap

    def resize_frame(self, frame, max_width, max_height):
        height, width, _ = frame.shape
        if width > max_width or height > max_height:
            scaling_factor = min(max_width / width, max_height / height)
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)
            frame = cv2.resize(frame, (new_width, new_height))
        return frame

    def extract_landmarks(self, pose_landmarks, mp_pose):
        landmarks = pose_landmarks.landmark
        return {
            'left_hip': [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y],
            'right_hip': [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y],
            'left_knee': [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y],
            'right_knee': [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y],
            'left_ankle': [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y],
            'right_ankle': [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y],
            'left_shoulder': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
            'right_shoulder': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
            'right_toe': [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y],
            'left_toe': [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
        }

    def draw_pose(self, frame, pose_landmarks, mp_pose):
        mp.solutions.drawing_utils.draw_landmarks(frame, pose_landmarks, mp_pose.POSE_CONNECTIONS)

    def process_frame(self, frame, pose):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)
        if result.pose_landmarks:
            landmarks = self.extract_landmarks(result.pose_landmarks, mp.solutions.pose)
            return landmarks, result.pose_landmarks
        return None, None

    def display_metrics(self, frame, metrics):
        cv2.putText(frame, f"Reps: {self.squat_counter.metrics.rep_count}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
        cv2.putText(frame, f"Correct Reps: {self.squat_counter.metrics.correct_rep_count}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
        cv2.putText(frame, f"Bad Reps: {self.squat_counter.metrics.bad_rep_count}", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)

    def process_video(self):
        # Process the video frame by frame and update the squat counter
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("End of video stream.")
                break

            frame = self.resize_frame(frame, self.config['max_width'], self.config['max_height'])
            landmarks, pose_landmarks = self.process_frame(frame, self.pose)

            if landmarks:
                metrics = self.squat_counter.update(landmarks)
                self.squat_counter.provide_real_time_feedback(frame, metrics)
                if pose_landmarks:
                    self.draw_pose(frame, pose_landmarks, mp.solutions.pose)
                self.display_metrics(frame, metrics)

            cv2.imshow('Squat Counter', frame)
            if cv2.waitKey(1) in [ord('q'), 27]:  # 'q' or 'Esc'
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    config = {
        'threshold_down': 70,
        'threshold_up': 160,
        'window_size': 4,
        'hip_knee_ankle_threshold': 170,
        'depth_threshold': 0.5,
        'knee_distance_threshold': 0.7,
        'feet_width_threshold': 2.0,
        'asymmetry_threshold': 10,
        'back_round_threshold': 180,
        'knee_caving_threshold': 0.7,
        'ankle_raise_threshold': 0.02,
        'max_width': 1280,
        'max_height': 720
    }

    video_path = "IMG_2083.mp4"
    analyzer = SquatAnalyzer(video_path, config)
    analyzer.process_video()
