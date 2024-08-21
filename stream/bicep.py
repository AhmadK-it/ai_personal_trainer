import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass, field


@dataclass
class BicepCurlMetrics:
    rep_count: int = 0
    correct_rep_count: int = 0
    bad_rep_count: int = 0
    lowest_angle: float = float('inf')
    elbow_not_fully_extended: bool = False
    improper_wrist_alignment: bool = False
    shoulder_movement: bool = False
    bad_rep_feedback: list = field(default_factory=list)


class BicepCurlCounter:
    def __init__(self, config):
        self.config = config
        self.metrics = BicepCurlMetrics()
        self.angle_history = []
        self.direction = None

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def update(self, landmarks):
        left_shoulder, right_shoulder = landmarks['left_shoulder'], landmarks['right_shoulder']
        left_elbow, right_elbow = landmarks['left_elbow'], landmarks['right_elbow']
        left_wrist, right_wrist = landmarks['left_wrist'], landmarks['right_wrist']

        left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_angle = (left_angle + right_angle) / 2

        self.check_form(landmarks, left_angle, right_angle)
        self.update_rep_count(avg_angle)

        return self.get_metrics()

    def check_form(self, landmarks, left_angle, right_angle):
        left_elbow, right_elbow = landmarks['left_elbow'], landmarks['right_elbow']
        left_wrist, right_wrist = landmarks['left_wrist'], landmarks['right_wrist']
        left_shoulder, right_shoulder = landmarks['left_shoulder'], landmarks['right_shoulder']

        self.metrics.elbow_not_fully_extended = (left_angle < self.config['elbow_extension_threshold'] or
                                                 right_angle < self.config['elbow_extension_threshold'])

        wrist_to_elbow_dist = np.linalg.norm(np.array(left_wrist) - np.array(left_elbow))
        shoulder_to_elbow_dist = np.linalg.norm(np.array(left_shoulder) - np.array(left_elbow))
        self.metrics.improper_wrist_alignment = wrist_to_elbow_dist < self.config['wrist_alignment_threshold'] * shoulder_to_elbow_dist

        self.metrics.shoulder_movement = abs(left_angle - right_angle) > self.config['shoulder_movement_threshold']
        # print(f'{abs(left_angle - right_angle)}')
        # print(f'{wrist_to_elbow_dist}')
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
            feedback = self.get_bad_rep_feedback()
            self.metrics.bad_rep_feedback.append((self.metrics.rep_count, feedback))
        self.reset_rep_metrics()

    def is_correct_rep(self):
        return (not self.metrics.elbow_not_fully_extended and
                not self.metrics.improper_wrist_alignment)

    def reset_rep_metrics(self):
        self.metrics.lowest_angle = float('inf')
        self.metrics.elbow_not_fully_extended = False
        self.metrics.improper_wrist_alignment = False
        self.metrics.shoulder_movement = False

    def get_bad_rep_feedback(self):
        feedback = []
        if self.metrics.elbow_not_fully_extended:
            feedback.append("Elbows are not fully extended.")
        if self.metrics.improper_wrist_alignment:
            feedback.append("Wrist alignment is improper.")
        if self.metrics.shoulder_movement:
            feedback.append("Shoulder movement detected.")
        return "\n ".join(feedback)

    def get_metrics(self):
        return (self.metrics.lowest_angle, self.metrics.elbow_not_fully_extended, self.metrics.improper_wrist_alignment,
                self.metrics.shoulder_movement, self.metrics.rep_count,
                self.metrics.correct_rep_count, self.metrics.bad_rep_count, self.success_rate())

    def success_rate(self):
        return (self.metrics.correct_rep_count / self.metrics.rep_count * 100) if self.metrics.rep_count > 0 else 0

    def print_bad_rep_feedback(self):
        for rep_num, feedback in self.metrics.bad_rep_feedback:
            print(f"Rep {rep_num}:\n{feedback}\n")


class BicepCurlVideoProcessor:
    def __init__(self, config):
        self.config = config
        self.counter = BicepCurlCounter(config)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False,
                                      min_detection_confidence=0.5)

    def process_video(self):
        cap = cv2.VideoCapture(self.config['video_path'])

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from video. Exiting...")
                break

            frame = self.resize_frame(frame)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.pose.process(frame_rgb)

            if result.pose_landmarks:
                landmarks = self.extract_landmarks(result.pose_landmarks)
                metrics = self.counter.update(landmarks)
                self.draw_pose(frame, result.pose_landmarks)
                self.display_metrics(frame, metrics)
            else:
                print("No pose landmarks detected in this frame.")

            cv2.imshow('Bicep Curl Counter', frame)
            if cv2.waitKey(1) in [ord('q'), 27]:  # 'q' or 'Esc'
                break

        cap.release()
        cv2.destroyAllWindows()
        self.counter.print_bad_rep_feedback()

    def resize_frame(self, frame):
        height, width, _ = frame.shape
        if width > self.config['max_width'] or height > self.config['max_height']:
            scaling_factor = min(self.config['max_width'] / width, self.config['max_height'] / height)
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)
            frame = cv2.resize(frame, (new_width, new_height))
        return frame

    def extract_landmarks(self, pose_landmarks):
        landmarks = pose_landmarks.landmark
        return {
            'left_shoulder': [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                              landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
            'right_shoulder': [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
            'left_elbow': [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                           landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
            'right_elbow': [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                            landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
            'left_wrist': [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                           landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y],
            'right_wrist': [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y],
        }

    def draw_pose(self, frame, pose_landmarks):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(frame, pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

    def display_metrics(self, frame, metrics):
        lowest_angle, elbow_not_fully_extended, improper_wrist_alignment, shoulder_movement, rep_count, correct_rep_count, bad_rep_count, success_rate = metrics

        text = f"Reps: {rep_count}, Correct: {correct_rep_count}, Bad: {bad_rep_count}, Success Rate: {success_rate:.2f}%"
        cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if elbow_not_fully_extended:
            cv2.putText(frame, "Warning: Elbows not fully extended!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        if improper_wrist_alignment:
            cv2.putText(frame, "Warning: Improper wrist alignment!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        if shoulder_movement:
            cv2.putText(frame, "Warning: Shoulder movement detected!", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


if __name__ == "__main__":
    config = {
        'video_path': 'b2.mp4',
        'threshold_up': 110,
        'threshold_down': 50,
        'elbow_extension_threshold': 120,
        'wrist_alignment_threshold': 0.7,
        'shoulder_movement_threshold': 110,
        'max_width': 1280,
        'max_height': 720,
        'window_size': 4
    }

    processor = BicepCurlVideoProcessor(config)
    processor.process_video()







# import cv2
# import mediapipe as mp
# import numpy as np
# from dataclasses import dataclass, field
#
#
# @dataclass
# class BicepCurlMetrics:
#     rep_count: int = 0
#     correct_rep_count: int = 0
#     bad_rep_count: int = 0
#     lowest_angle: float = float('inf')
#     elbow_not_fully_extended: bool = False
#     improper_wrist_alignment: bool = False
#     shoulder_movement: bool = False
#     bad_rep_feedback: list = field(default_factory=list)
#
#
# class BicepCurlCounter:
#     def __init__(self, config):
#         self.config = config
#         self.metrics = BicepCurlMetrics()
#         self.angle_history = []
#         self.direction = None
#
#     def calculate_angle(self, a, b, c):
#         a, b, c = np.array(a), np.array(b), np.array(c)
#         radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
#         angle = np.abs(radians * 180.0 / np.pi)
#         return 360 - angle if angle > 180.0 else angle
#
#     def update(self, landmarks):
#         left_shoulder, right_shoulder = landmarks['left_shoulder'], landmarks['right_shoulder']
#         left_elbow, right_elbow = landmarks['left_elbow'], landmarks['right_elbow']
#         left_wrist, right_wrist = landmarks['left_wrist'], landmarks['right_wrist']
#
#         left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
#         right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
#         avg_angle = (left_angle + right_angle) / 2
#
#         self.check_form(landmarks, left_angle, right_angle)
#         self.update_rep_count(avg_angle)
#
#         return self.get_metrics()
#
#     def check_form(self, landmarks, left_angle, right_angle):
#         left_elbow, right_elbow = landmarks['left_elbow'], landmarks['right_elbow']
#         left_wrist, right_wrist = landmarks['left_wrist'], landmarks['right_wrist']
#         left_shoulder, right_shoulder = landmarks['left_shoulder'], landmarks['right_shoulder']
#
#         # Check for full elbow extension
#         self.metrics.elbow_not_fully_extended = (left_angle > self.config['elbow_extension_threshold'] or
#                                                  right_angle > self.config['elbow_extension_threshold'])
#
#         # Check for wrist misalignment (example: wrist not in line with elbow during curl)
#         wrist_to_elbow_dist = np.linalg.norm(np.array(left_wrist) - np.array(left_elbow))
#         shoulder_to_elbow_dist = np.linalg.norm(np.array(left_shoulder) - np.array(left_elbow))
#         self.metrics.improper_wrist_alignment = wrist_to_elbow_dist < self.config['wrist_alignment_threshold'] * shoulder_to_elbow_dist
#
#         # Check for shoulder movement
#         self.metrics.shoulder_movement = abs(left_angle - right_angle) > self.config['shoulder_movement_threshold']
#
#     def update_rep_count(self, angle):
#         self.angle_history.append(angle)
#         if len(self.angle_history) > self.config['window_size']:
#             self.angle_history.pop(0)
#
#         if len(self.angle_history) == self.config['window_size']:
#             mean_angle = np.mean(self.angle_history)
#             self.metrics.lowest_angle = min(self.metrics.lowest_angle, mean_angle)
#
#             if self.direction is None and mean_angle < self.config['threshold_down']:
#                 self.direction = 'down'
#             elif self.direction == 'down' and mean_angle > self.config['threshold_up']:
#                 self.complete_rep()
#             elif self.direction == 'up' and mean_angle < self.config['threshold_down']:
#                 self.direction = 'down'
#
#     def complete_rep(self):
#         self.direction = 'up'
#         self.metrics.rep_count += 1
#         if self.is_correct_rep():
#             self.metrics.correct_rep_count += 1
#         else:
#             self.metrics.bad_rep_count += 1
#             feedback = self.get_bad_rep_feedback()
#             self.metrics.bad_rep_feedback.append((self.metrics.rep_count, feedback))
#         self.reset_rep_metrics()
#
#     def is_correct_rep(self):
#         return (not self.metrics.elbow_not_fully_extended and
#                 not self.metrics.improper_wrist_alignment)
#
#     def reset_rep_metrics(self):
#         self.metrics.lowest_angle = float('inf')
#         self.metrics.elbow_not_fully_extended = False
#         self.metrics.improper_wrist_alignment = False
#         self.metrics.shoulder_movement = False
#
#     def get_bad_rep_feedback(self):
#         feedback = []
#         if self.metrics.elbow_not_fully_extended:
#             feedback.append("Elbows are not fully extended.")
#         if self.metrics.improper_wrist_alignment:
#             feedback.append("Wrist alignment is improper.")
#         if self.metrics.shoulder_movement:
#             feedback.append("Shoulder movement detected.")
#         return "\n ".join(feedback)
#
#     def get_metrics(self):
#         return (self.metrics.lowest_angle, self.metrics.elbow_not_fully_extended, self.metrics.improper_wrist_alignment,
#                 self.metrics.shoulder_movement, self.metrics.rep_count,
#                 self.metrics.correct_rep_count, self.metrics.bad_rep_count, self.success_rate())
#
#     def success_rate(self):
#         return (self.metrics.correct_rep_count / self.metrics.rep_count * 100) if self.metrics.rep_count > 0 else 0
#
#     def print_bad_rep_feedback(self):
#         for rep_num, feedback in self.metrics.bad_rep_feedback:
#             print(f"Rep {rep_num}:\n{feedback}\n")
#
# def resize_frame(frame, max_width, max_height):
#     height, width, _ = frame.shape
#     if width > max_width or height > max_height:
#         scaling_factor = min(max_width / width, max_height / height)
#         new_width = int(width * scaling_factor)
#         new_height = int(height * scaling_factor)
#         frame = cv2.resize(frame, (new_width, new_height))
#     return frame
#
#
# def extract_landmarks(pose_landmarks, mp_pose):
#     landmarks = pose_landmarks.landmark
#     return {
#         'left_shoulder': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
#                           landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
#         'right_shoulder': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
#                            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
#         'left_elbow': [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
#                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
#         'right_elbow': [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
#                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
#         'left_wrist': [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
#                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y],
#         'right_wrist': [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
#                         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y],
#     }
#
#
# def draw_pose(frame, pose_landmarks, mp_pose):
#     mp_drawing = mp.solutions.drawing_utils
#     mp_drawing.draw_landmarks(frame, pose_landmarks, mp_pose.POSE_CONNECTIONS)
#
#
# def display_metrics(frame, metrics):
#     lowest_angle, elbow_not_fully_extended, improper_wrist_alignment, shoulder_movement, rep_count, correct_rep_count, bad_rep_count, success_rate = metrics
#
#     text = f"Reps: {rep_count}, Correct: {correct_rep_count}, Bad: {bad_rep_count}, Success Rate: {success_rate:.2f}%"
#     cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#
#     feedback = []
#     if elbow_not_fully_extended:
#         feedback.append("Elbows not fully extended.")
#     if improper_wrist_alignment:
#         feedback.append("Wrist alignment is off.")
#     if shoulder_movement:
#         feedback.append("Shoulder movement detected.")
#
#     for i, line in enumerate(feedback):
#         cv2.putText(frame, line, (10, 60 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
#
# def main():
#     config = {
#         'threshold_down': 50,  # Minimum angle for down position (bicep contraction)
#         'threshold_up': 150,  # Maximum angle for up position (bicep extension)
#         'window_size': 5,
#         'elbow_extension_threshold': 160,  # Threshold for full elbow extension
#         'wrist_alignment_threshold': 0.7,  # Ratio to detect improper wrist alignment
#         'shoulder_movement_threshold': 15,  # Threshold for shoulder movement asymmetry
#         'video_path': 'b2.mp4',
#         'max_width': 720,
#         'max_height': 480
#     }
#
#     counter = BicepCurlCounter(config)
#     mp_pose = mp.solutions.pose
#     pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False,
#                         min_detection_confidence=0.5)
#
#     cap = cv2.VideoCapture(config['video_path'])
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to read frame from video. Exiting...")
#             break
#
#         frame = resize_frame(frame, config['max_width'], config['max_height'])
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         result = pose.process(frame_rgb)
#
#         if result.pose_landmarks:
#             landmarks = extract_landmarks(result.pose_landmarks, mp_pose)
#             metrics = counter.update(landmarks)
#             draw_pose(frame, result.pose_landmarks, mp_pose)
#             display_metrics(frame, metrics)
#         else:
#             print("No pose landmarks detected in this frame.")
#
#         cv2.imshow('Bicep Curl Counter', frame)
#         if cv2.waitKey(1) in [ord('q'), 27]:  # 'q' or 'Esc'
#             break
#
#     cap.release()
#     cv2.destroyAllWindows()
#     counter.print_bad_rep_feedback()
#
# if __name__ == '__main__':
#     main()







# import cv2
# from ultralytics import YOLO
# import torch
# import numpy as np
#
#
# class BicepCurlCounter:
#     def __init__(self, threshold_down=80, threshold_up=100, window_size=5, full_extension_threshold=160,
#                  full_contraction_threshold=40, elbow_movement_threshold=10):
#         self.rep_count = 0
#         self.correct_rep_count = 0
#         self.threshold_down = threshold_down
#         self.threshold_up = threshold_up
#         self.full_extension_threshold = full_extension_threshold
#         self.full_contraction_threshold = full_contraction_threshold
#         self.elbow_movement_threshold = elbow_movement_threshold
#         self.angle_history = []
#         self.elbow_positions = []
#         self.direction = None
#         self.window_size = window_size
#         self.in_full_extension = False
#         self.in_full_contraction = False
#
#     def calculate_angle(self, a, b, c):
#         """ Calculate the angle between three points. """
#         ba = a - b
#         bc = c - b
#         cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#         angle = np.degrees(np.arccos(cosine_angle))
#         return angle
#
#     def update(self, shoulder, elbow, wrist):
#         """ Update the counter with new keypoints. """
#         # Calculate the angle
#         angle = self.calculate_angle(np.array(shoulder), np.array(elbow), np.array(wrist))
#
#         # Add angle to history
#         self.angle_history.append(angle)
#         if len(self.angle_history) > self.window_size:
#             self.angle_history.pop(0)
#
#         # Add elbow position to history
#         self.elbow_positions.append(np.array(elbow))
#         if len(self.elbow_positions) > self.window_size:
#             self.elbow_positions.pop(0)
#
#         print(f"Current angle: {angle:.2f} degrees")  # Debug: print the current angle
#         print(f"Angle history: {self.angle_history}")  # Debug: print the angle history
#
#         # Check for full extension and full contraction
#         if angle >= self.full_extension_threshold:
#             self.in_full_extension = True
#         if angle <= self.full_contraction_threshold:
#             self.in_full_contraction = True
#
#         # Determine direction and count reps
#         if len(self.angle_history) == self.window_size:
#             mean_angle = np.mean(self.angle_history)
#             print(f"Mean angle: {mean_angle:.2f} degrees")  # Debug: print the mean angle
#
#             if self.direction is None:
#                 if mean_angle < self.threshold_down:
#                     self.direction = 'down'
#                     print("Initial direction: down")  # Debug: print the initial direction
#             elif self.direction == 'down' and mean_angle > self.threshold_up:
#                 self.direction = 'up'
#                 self.rep_count += 1
#                 print("Direction change: up, Rep counted")  # Debug: print the direction change and rep count
#                 if self.in_full_extension and self.in_full_contraction:
#                     elbow_displacement = np.linalg.norm(self.elbow_positions[-1] - self.elbow_positions[0])
#                     print(f"Elbow displacement: {elbow_displacement:.2f}")  # Debug: print elbow displacement
#                     if elbow_displacement <= self.elbow_movement_threshold:
#                         self.correct_rep_count += 1
#                         print("Correct rep counted")  # Debug: print correct rep count
#                     else:
#                         print(
#                             "MISTAKE you should not move your elbow too much, you are using you're using your "
#                             "shoulder to help you curl")  # Debug: print mistake message for elbow movement
#                 else:
#                     if not self.in_full_extension:
#                         print(
#                             "MISTAKE not reaching a full range of motion, you should extend your bicep muscle more")  # Debug: print mistake message for full extension
#                     if not self.in_full_contraction:
#                         print(
#                             "MISTAKE not reaching a full range of motion, you should contract your bicep muscle more")  # Debug: print mistake message for full contraction
#                 # Reset full extension and contraction flags
#                 self.in_full_extension = False
#                 self.in_full_contraction = False
#             elif self.direction == 'up' and mean_angle < self.threshold_down:
#                 self.direction = 'down'
#                 print("Direction change: down")  # Debug: print the direction change
#
#         return self.rep_count, self.correct_rep_count
#
#
# # Setting device on GPU if available, else CPU
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#
# # Initialize YOLO model
# model = YOLO('yolov8n-pose.pt')
# model.to(device)  # Explicitly set the device for the model
#
# # Predefined keypoint labels (this is an example, update as per your keypoint structure)
# keypoint_labels = [
#     'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
#     'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
#     'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
#     'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
# ]
#
# # Path to your video file
# video_path = 's3.mp4'
#
# # Open video capture
# cap = cv2.VideoCapture(0)
#
# # Define maximum dimensions
# max_width = 1280
# max_height = 720
#
# counter = BicepCurlCounter()
#
#
# def get_center_keypoint(keypoints):
#     """ Calculate the average position of keypoints to get the approximate center. """
#     x_coords = [kp[0] for kp in keypoints if kp[0] > 0]
#     y_coords = [kp[1] for kp in keypoints if kp[1] > 0]
#     if len(x_coords) == 0 or len(y_coords) == 0:
#         return 0, 0
#     return sum(x_coords) // len(x_coords), sum(y_coords) // len(y_coords)
#
#
# def evaluate_bicep_curl(keypoints):
#     """ Evaluate the bicep curl exercise based on keypoints from the right side. """
#     right_shoulder = keypoints[keypoint_labels.index('right_shoulder')]
#     right_elbow = keypoints[keypoint_labels.index('right_elbow')]
#     right_wrist = keypoints[keypoint_labels.index('right_wrist')]
#
#     if all([kp[0] > 0 and kp[1] > 0 for kp in [right_shoulder, right_elbow, right_wrist]]):
#         right_shoulder_point = np.array(right_shoulder)
#         right_elbow_point = np.array(right_elbow)
#         right_wrist_point = np.array(right_wrist)
#         right_angle = counter.calculate_angle(right_shoulder_point, right_elbow_point, right_wrist_point)
#         reps, correct_reps = counter.update(right_shoulder_point, right_elbow_point, right_wrist_point)
#         print(f"Right arm angle: {right_angle:.2f} degrees")
#         print(f"Reps: {reps}, Correct Reps: {correct_reps}")
#     else:
#         print("Right arm keypoints not fully visible.")
#
#
# # Main loop
# while True:
#     # Read a frame from the video
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     # Get frame dimensions
#     height, width, _ = frame.shape
#
#     # Check if resizing is needed
#     if width > max_width or height > max_height:
#         scaling_factor = min(max_width / width, max_height / height)
#         new_width = int(width * scaling_factor)
#         new_height = int(height * scaling_factor)
#         frame = cv2.resize(frame, (new_width, new_height))
#
#     # Ensure frame dimensions are divisible by 32
#     new_height = (frame.shape[0] // 32) * 32
#     new_width = (frame.shape[1] // 32) * 32
#     frame_resized = cv2.resize(frame, (new_width, new_height))
#
#     # Convert frame to tensor and perform object detection and pose estimation
#     frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
#     frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).float().to(device) / 255.0
#     frame_tensor = frame_tensor.unsqueeze(0)  # Add batch dimension
#
#     # Perform object detection and pose estimation
#     results = model(frame_tensor)
#
#     best_keypoints = None
#
#     # Check the number of detected people
#     if len(results[0].keypoints) == 1:
#         # If only one person detected, use their keypoints directly
#         best_keypoints = results[0].keypoints.xy.cpu().numpy()[0]
#     else:
#         # Find the detection closest to the center
#         center_frame = (new_width // 2, new_height // 2)
#         min_distance = float('inf')
#         for result in results:
#             if result.keypoints is not None:
#                 for person_keypoints in result.keypoints.xy.cpu().numpy():
#                     center_keypoint = get_center_keypoint(person_keypoints)
#                     distance = ((center_keypoint[0] - center_frame[0]) ** 2 + (
#                                 center_keypoint[1] - center_frame[1]) ** 2) ** 0.5
#                     if distance < min_distance:
#                         min_distance = distance
#                         best_keypoints = person_keypoints
#
#     if best_keypoints is not None:
#         evaluate_bicep_curl(best_keypoints)
#
#         # Draw keypoints on the frame
#         for kp_name in ['right_shoulder', 'right_elbow', 'right_wrist']:
#             kp_index = keypoint_labels.index(kp_name)
#             kp = best_keypoints[kp_index]
#             if len(kp) == 2 and kp[0] > 0 and kp[1] > 0:  # Check if kp has 2 coordinates and is not [0, 0]
#                 cv2.circle(frame_resized, tuple(kp.astype(int)), 3, (0, 0, 255), -1)
#                 cv2.putText(frame_resized, kp_name, tuple(kp.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0),
#                             1, cv2.LINE_AA)
#
#     # Show the frame
#     cv2.imshow('Frame', frame_resized)
#
#     # Check for exit key
#     key = cv2.waitKeyEx(1)
#     if key == ord('q') or key == 27:  # 'q' key or Esc key
#         print("Exiting...")
#         break
#
# # Release video capture and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()
