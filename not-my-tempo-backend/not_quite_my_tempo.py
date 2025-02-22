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
movement_threshold = 0.03  # Adjusted for smoother movement detection
curvature_threshold = 0.05  # Required curvature for arc detection
trajectory_length = 10  # Tracks last N positions for smoother motion detection
wrist_positions = deque(maxlen=trajectory_length)  # Stores last N wrist positions
last_gesture = None  # Stores last detected gesture
conductor_moving = False  # Flag for conductor's movement

# Message display settings
display_message = False
message_timer = 0  # Timestamp when the message started displaying
message_duration = 1  # Time in seconds to display the message

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
                    mp_hands.HandLandmark.RING_FINGER_TIP,
                    mp_hands.HandLandmark.PINKY_TIP
                ]
                finger_pips = [
                    mp_hands.HandLandmark.INDEX_FINGER_PIP,
                    mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
                    mp_hands.HandLandmark.RING_FINGER_PIP,
                    mp_hands.HandLandmark.PINKY_PIP
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

                    # Check if conductor is moving
                    if len(wrist_positions) >= trajectory_length:
                        positions = np.array(wrist_positions)
                        dx = positions[-1, 0] - positions[0, 0]
                        dy = positions[-1, 1] - positions[0, 1]
                        total_displacement = np.linalg.norm([dx, dy])

                        if total_displacement > movement_threshold:
                            conductor_moving = True
                        else:
                            conductor_moving = False

                elif open_fingers >= 3:  # Most fingers are extended
                    conductor_moving = False
                    gesture = "Open Palm"
                    color = (0, 255, 0)  # Green

                    # Ensure enough positions are recorded before checking movement
                    if len(wrist_positions) >= trajectory_length:
                        # Convert stored positions to NumPy array
                        positions = np.array(wrist_positions)

                        # Compute the displacement vectors
                        dx = positions[-1, 0] - positions[0, 0]
                        dy = positions[-1, 1] - positions[0, 1]
                        total_displacement = np.linalg.norm([dx, dy])

                        # Compute curvature by checking if middle points deviate from a straight line
                        mid_index = len(positions) // 2
                        mid_point = positions[mid_index]
                        expected_mid_x = (positions[0, 0] + positions[-1, 0]) / 2
                        expected_mid_y = (positions[0, 1] + positions[-1, 1]) / 2
                        curvature = np.linalg.norm(mid_point - np.array([expected_mid_x, expected_mid_y]))

                        # If the movement is large enough and curved, classify as semi-circular motion
                        if total_displacement > movement_threshold and curvature > curvature_threshold:
                            gesture = "Semi-Circular Motion"
                            color = (255, 0, 0)  # Blue

                else:  # Fingers are curled
                    conductor_moving = False
                    gesture = "Fist"
                    color = (0, 0, 255)  # Red
                    wrist_positions.clear()  # Reset trajectory when a fist is detected

                    # If the previous gesture was a semi-circular motion, trigger message display
                    if last_gesture == "Semi-Circular Motion":
                        display_message = True
                        message_timer = time.time()  # Start timer

                # Update last detected gesture
                last_gesture = gesture

                # Display the detected gesture
                cv2.putText(frame, gesture, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

                # Display conductor movement
                if conductor_moving:
                    cv2.putText(frame, "Conductor Moving", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3, cv2.LINE_AA)

        # Check if the message should be displayed
        if display_message:
            elapsed_time = time.time() - message_timer
            if elapsed_time < message_duration:
                # Get frame dimensions to center the text
                height, width, _ = frame.shape
                text = "Not Quite My Tempo"
                font_scale = 2  # Larger text
                thickness = 4
                font = cv2.FONT_HERSHEY_SIMPLEX

                # Get text size to center it
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                text_x = (width - text_size[0]) // 2  # Center horizontally
                text_y = (height + text_size[1]) // 2  # Center vertically

                # Display large centered text
                cv2.putText(frame, text, (text_x, text_y),
                            font, font_scale, (0, 255, 255), thickness, cv2.LINE_AA)
            else:
                display_message = False  # Hide message after duration

        # Display the frame
        cv2.imshow('Hand Gesture Recognition', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
