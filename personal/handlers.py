import cv2
import face_recognition
import mediapipe as mp

from .services import identify_person_from_video


def check_head_turn(video_path):
    """
    Проверяет, повернул ли пользователь голову налево и направо.

    :param video_path: Путь к видео.
    :return: True, если движение выполнено, иначе False.
    """
    video_capture = cv2.VideoCapture(video_path)
    frame_count = 0
    head_positions = []  

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 10 != 0:  
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            center_x = (left + right) / 2  
            head_positions.append(center_x)

    video_capture.release()

    if len(head_positions) < 2:
        return False

    min_x = min(head_positions)
    max_x = max(head_positions)
    if max_x - min_x > 50:  
        return True
    return False



def check_raise_hand(video_path):
    """
    Проверяет, поднимал ли пользователь левую руку и затем опустил её.

    :param video_path: Путь к видео.
    :return: True, если действие выполнено, иначе False.
    """
    mp_hands = mp.solutions.hands
    video_capture = cv2.VideoCapture(video_path)
    hand_raised = False

    with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_label = results.multi_handedness[0].classification[0].label
                    if hand_label == "Left":
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                        elbow = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
                        if wrist.y < elbow.y: 
                            hand_raised = True
                        elif hand_raised and wrist.y > elbow.y: 
                            video_capture.release()
                            return True
    video_capture.release()
    return False


def check_head_up_and_down(video_path):
    """
    Проверяет, смотрел ли пользователь вверх, затем вниз.

    :param video_path: Путь к видео.
    :return: True, если действие выполнено, иначе False.
    """
    video_capture = cv2.VideoCapture(video_path)
    head_positions = []  

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            center_y = (top + bottom) / 2  
            head_positions.append(center_y)

    video_capture.release()

    if len(head_positions) < 2:
        return False

    min_y = min(head_positions)
    max_y = max(head_positions)
    if max_y - min_y > 50: 
        return True
    return False


def check_turn_right_then_left(video_path):
    """
    Проверяет, повернул ли пользователь голову вправо, затем влево.

    :param video_path: Путь к видео.
    :return: True, если действие выполнено, иначе False.
    """
    video_capture = cv2.VideoCapture(video_path)
    head_positions = []  

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            center_x = (left + right) / 2  
            head_positions.append(center_x)

    video_capture.release()

    if len(head_positions) < 3:
        return False

    first_move = head_positions[1] - head_positions[0]
    second_move = head_positions[2] - head_positions[1]
    if first_move > 50 and second_move < -50: 
        return True
    return False



def verify_instruction_and_user(video_path, selected_instruction):
    if selected_instruction == "Посмотрите налево, затем направо.":
        if not check_head_turn(video_path):
            return {"status": "failed", "message": "Инструкция не выполнена."}
    
    elif selected_instruction == "Посмотрите вверх, затем вниз.":
        if not check_head_up_and_down(video_path):
            return {"status": "failed", "message": "Инструкция не выполнена."}
    
    else:
        return {"status": "failed", "message": "Инструкция не поддерживается."}

    return identify_person_from_video(video_path)



