import cv2
import mediapipe as mp
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# Constants for configuration
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5
GAME_URL = "https://poki.com/en/g/subway-surfers"
SLEEP_TIME = 10

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=DETECTION_CONFIDENCE, min_tracking_confidence=TRACKING_CONFIDENCE)

# Initialize camera
cap = cv2.VideoCapture(0)
# Initialize Selenium WebDriver 
driver = webdriver.Chrome()
driver.get(GAME_URL)

# Wait for the game to load
time.sleep(SLEEP_TIME)

# Track the state of hands
class HandState:
    def __init__(self):
        self.left_raised = False
        self.right_raised = False
        self.both_raised = False
        self.head_lowered = False
        self.can_detect_new_movement = True

hand_state = HandState()

def perform_action(action: str) -> None:
    """Execute game controls based on detected movements."""
    actions = ActionChains(driver)
    if action == 'jump':
        actions.send_keys(Keys.ARROW_UP).perform()
    elif action == 'slide':
        actions.send_keys(Keys.ARROW_DOWN).perform()
    elif action == 'left':
        actions.send_keys(Keys.ARROW_LEFT).perform()
    elif action == 'right':
        actions.send_keys(Keys.ARROW_RIGHT).perform()

def check_hand_raised(landmarks, side: str) -> bool:
    """Check if a specific hand is raised above the shoulder."""
    if side == 'left':
        wrist = landmarks[15]  # Left wrist
        shoulder = landmarks[11]  # Left shoulder
    else:  # right  
        wrist = landmarks[16]  # Right wrist
        shoulder = landmarks[12]  # Right shoulder
    
    return wrist.y < shoulder.y

def is_neutral_position(landmarks) -> bool:
    """Check if hands are in neutral position (below shoulders)."""
    return (not check_hand_raised(landmarks, 'left') and 
            not check_hand_raised(landmarks, 'right') and 
            landmarks[0].y <= 0.5)  # Head not lowered

def is_jumping(landmarks) -> bool:
    """Check if both hands are raised to trigger jump instead of actual jumping."""
    return check_hand_raised(landmarks, 'left') and check_hand_raised(landmarks, 'right')

# Main loop to capture movements and perform actions
def main() -> None:
    """Main function to capture movements and perform actions."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Check if in neutral position
            if is_neutral_position(landmarks):
                hand_state.can_detect_new_movement = True
                hand_state.left_raised = False
                hand_state.right_raised = False
                hand_state.both_raised = False
                hand_state.head_lowered = False
            
            # Only detect new movements if we're allowed to
            if hand_state.can_detect_new_movement:
                left_raised = check_hand_raised(landmarks, 'left')
                right_raised = check_hand_raised(landmarks, 'right')
                head_lowered = landmarks[0].y > 0.5

                # Detect jump (if both hands are raised)
                if is_jumping(landmarks) and not hand_state.both_raised:
                    perform_action('jump')
                    hand_state.both_raised = True
                    hand_state.can_detect_new_movement = False

                # Detect slide (head lowered)
                elif head_lowered and not hand_state.head_lowered:
                    perform_action('slide')
                    hand_state.head_lowered = True
                    hand_state.can_detect_new_movement = False

                # Detect left movement (left hand raised)
                elif left_raised and not right_raised and not hand_state.left_raised:
                    perform_action('left')
                    hand_state.left_raised = True
                    hand_state.can_detect_new_movement = False

                # Detect right movement (right hand raised)
                elif right_raised and not left_raised and not hand_state.right_raised:
                    perform_action('right')
                    hand_state.right_raised = True
                    hand_state.can_detect_new_movement = False

        # Display the frame with mirrored view for better control
        frame = cv2.flip(frame, 1)
        
        # Add visual feedback about the current state
        cv2.putText(frame, f"Can detect: {'Yes' if hand_state.can_detect_new_movement else 'No'}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if hand_state.can_detect_new_movement else (0, 0, 255), 2)

        cv2.imshow('Game Control', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    driver.quit()

if __name__ == "__main__":
    main()
