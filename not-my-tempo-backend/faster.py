import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time

# Initialize MediaPipe Hands and Drawing modules
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Variables for movement tracking
movement_threshold = 0.03  # Threshold for movement detection
speed_threshold = 0.125  # Speed threshold for feedback
speedy_threshold = 0.25  # Higher speed threshold
trajectory_length = 10  # Tracks last N positions for speed tracking
wrist_positions = deque(maxlen=trajectory_length)  # Stores last N wrist positions
last_gesture = None  # Stores last detected gesture
conductor_speed = 0  # Tracks movement speed
feedback_message = ""  # Message for speed feedback
feedback_color = (255, 255, 255)  # Default white color

# Direction tracking
last_direction = None  # Tracks the last movement direction

# Define hand tracking parameters
with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape  # Get frame dimensions for centering text
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process the frame and detect hands
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract key landmarks for gesture recognition
                finger_tips = [
                    mp_hands.HandLandmark.INDEX_FINGER_TIP,
                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                ]
                finger_pips = [
                    mp_hands.HandLandmark.INDEX_FINGER_PIP,
                    mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
                ]
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                # Convert wrist position to numpy array
                current_wrist_position = np.array([wrist.x, wrist.y])

                # Store recent wrist positions
                wrist_positions.append(current_wrist_position)

                # Check if fingers are open (tips should be significantly above PIP joints)
                open_fingers = sum(
                    hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y
                    for tip, pip in zip(finger_tips, finger_pips)
                )

                # Gesture classification
                if open_fingers == 2:  # Two fingers extended (conductor's gesture)
                    gesture = "Conductor's Gesture"
                    color = (255, 255, 0)

                    # Check if conductor is moving & calculate speed
                    if len(wrist_positions) >= trajectory_length:
                        positions = np.array(wrist_positions)
                        dx = positions[-1, 0] - positions[0, 0]  # Change in x
                        dy = positions[-1, 1] - positions[0, 1]  # Change in y

                        current_direction = np.sign(dx)  # +1 for right, -1 for left

                        # If direction changes, maintain speed instead of resetting
                        if last_direction is not None and current_direction != last_direction:
                            conductor_speed = max(conductor_speed, np.linalg.norm([dx, dy]))
                        else:
                            conductor_speed = np.linalg.norm([dx, dy])

                        last_direction = current_direction  # Update last direction

                        # Speed-based feedback
                        if conductor_speed < speed_threshold:
                            feedback_message = "Faster!"
                            feedback_color = (0, 0, 255)  # Red
                        elif conductor_speed < speedy_threshold:
                            feedback_message = "Even Faster!"
                            feedback_color = (0, 0, 255)
                        else:
                            feedback_message = "Good Boy!"
                            feedback_color = (0, 255, 0)  # Green

                else:  # Other gestures
                    feedback_message = ""  # Reset feedback if no conductor gesture detected

                # Display the detected gesture
                cv2.putText(frame, gesture, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        # Display speed feedback
        if feedback_message:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 4
            text_size = cv2.getTextSize(feedback_message, font, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2

            cv2.putText(frame, feedback_message, (text_x, text_y),
                        font, font_scale, feedback_color, thickness, cv2.LINE_AA)

        # Display the frame
        cv2.imshow('Conductor Gesture Recognition', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
