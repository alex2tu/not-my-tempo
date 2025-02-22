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

                # Convert wrist position to a 3D numpy array (x, y, z)
                current_wrist_position = np.array([wrist.x, wrist.y, wrist.z])
                # Store recent wrist positions
                wrist_positions.append(current_wrist_position)

                # Check if fingers are open (tip is significantly above the corresponding PIP joint)
                open_fingers = sum(
                    hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y
                    for tip, pip in zip(finger_tips, finger_pips)
                )

                # Gesture classification based on number of open fingers and movement
                if open_fingers == 2:  # Two fingers extended (conductor's gesture)
                    gesture = "Conductor's Gesture"
                    color = (255, 255, 0)

                    # Check if conductor is moving by analyzing the 3D wrist trajectory
                    if len(wrist_positions) >= trajectory_length:
                        positions = np.array(wrist_positions)
                        # Compute the displacement vector (3D) from the start to the end of the trajectory
                        displacement = positions[-1] - positions[0]
                        total_displacement = np.linalg.norm(displacement)
                        if total_displacement > movement_threshold:
                            conductor_moving = True
                        else:
                            conductor_moving = False

                elif open_fingers >= 3:  # Most fingers are extended ("Open Palm")
                    conductor_moving = False
                    gesture = "Open Palm"
                    color = (0, 255, 0)  # Green

                    # Only check movement if enough positions are recorded
                    if len(wrist_positions) >= trajectory_length:
                        positions = np.array(wrist_positions)
                        displacement = positions[-1] - positions[0]
                        total_displacement = np.linalg.norm(displacement)
                        # Compute curvature: compare the actual mid-point of the trajectory with the expected mid-point (straight line)
                        mid_index = len(positions) // 2
                        mid_point = positions[mid_index]
                        expected_mid = (positions[0] + positions[-1]) / 2
                        curvature = np.linalg.norm(mid_point - expected_mid)

                        if total_displacement > movement_threshold and curvature > curvature_threshold:
                            gesture = "Semi-Circular Motion"
                            color = (255, 0, 0)  # Blue

                else:  # Fist (fingers are curled)
                    conductor_moving = False
                    gesture = "Fist"
                    color = (0, 0, 255)  # Red
                    wrist_positions.clear()  # Reset trajectory when a fist is detected

                    # If the previous gesture was semi-circular motion, trigger the message display
                    if last_gesture == "Semi-Circular Motion":
                        display_message = True
                        message_timer = time.time()  # Start timer

                # Update the last detected gesture
                last_gesture = gesture

                # Display the detected gesture on the frame
                cv2.putText(frame, gesture, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

                # Optionally display an indicator if the conductor is moving
                if conductor_moving:
                    cv2.putText(frame, "Conductor Moving", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3, cv2.LINE_AA)

        # Outside the hand landmarks loop, display the motion vector in the top right corner
        if len(wrist_positions) >= trajectory_length:
            positions = np.array(wrist_positions)
            # Compute displacement from the first to the last recorded position
            displacement = positions[-1] - positions[0]
            dx, dy, dz = displacement
            dz_scaled = 1000000 * dz

            # Get frame dimensions to convert normalized coordinates to pixels
            h, w, _ = frame.shape
            margin = 100
            # Define the arrow's starting point (top right corner, with some margin)
            arrow_start = (w - margin, margin)
            # Scale the normalized displacement for visualization purposes
            factor = 300  # Adjust this factor based on your needs
            arrow_end = (int(arrow_start[0] + dx * factor), int(arrow_start[1] + dy * factor))

            # Draw the arrow representing the motion vector
            cv2.arrowedLine(frame, arrow_start, arrow_end, (255, 255, 255), 2, tipLength=0.3)
            # Display the numerical values of the displacement
            cv2.putText(frame, f"dx: {dx:.3f}, dy: {dy:.3f}, dz: {dz_scaled:.3f}", (w - 450, margin + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)



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
