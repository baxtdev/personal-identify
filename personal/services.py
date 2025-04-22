import face_recognition
import numpy as np
import cv2

from personal.models import Personal


def identify_person(photo_path):
    """
    Идентификация пользователя по фотографии.

    :param photo_path: Путь к фотографии для анализа.
    :return: Данные пользователя или сообщение о том, что лицо не найдено.
    """
    try:
        input_image = face_recognition.load_image_file(photo_path)
        input_face_encodings = face_recognition.face_encodings(input_image)

        if not input_face_encodings:
            return {"status": "error", "message": "Лицо на изображении не найдено."}

        input_encoding = input_face_encodings[0]

        for person in Personal.objects.exclude(face_encoding__isnull=True):
            saved_encoding = np.array(person.face_encoding)  #
            match = face_recognition.compare_faces([saved_encoding], input_encoding)

            if match[0]:
                return {
                    "status": "success",
                    "data": {
                        "name": person.name,
                        "age": person.age,
                        "city": person.city,
                        "email": person.email,
                        "phone": person.phone,
                        "avatar_url": person.avatar.url if person.avatar else None,
                    },
                }

        return {"status": "not_found", "message": "Пользователь не найден."}

    except Exception as e:
        return {"status": "error", "message": str(e)}






def identify_person_from_video(video_path):
    """
    Идентификация пользователя по видео.

    :param video_path: Путь к видеофайлу.
    :return: Данные пользователя или сообщение о том, что лицо не найдено.
    """
    try:
        video_capture = cv2.VideoCapture(video_path)
        frame_count = 0

        if not video_capture.isOpened():
            return {"status": "error", "message": "Не удалось открыть видео."}

        saved_persons = [
            {
                "person": person,
                "encoding": np.array(person.face_encoding),
            }
            for person in Personal.objects.exclude(face_encoding__isnull=True)
        ]

        if not saved_persons:
            return {"status": "error", "message": "Нет сохранённых лиц в базе данных."}

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_count += 1

            if frame_count % 10 != 0:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_encodings = face_recognition.face_encodings(rgb_frame)

            for input_encoding in face_encodings:
                for saved_person in saved_persons:
                    match = face_recognition.compare_faces(
                        [saved_person["encoding"]], input_encoding
                    )

                    if match[0]:
                        video_capture.release()
                        return {
                            "status": "success",
                            "data": {
                                "name": saved_person["person"].name,
                                "age": saved_person["person"].age,
                                "city": saved_person["person"].city,
                                "email": saved_person["person"].email,
                                "phone": saved_person["person"].phone,
                                "avatar_url": saved_person["person"].avatar.url
                                if saved_person["person"].avatar
                                else None,
                            },
                        }

        video_capture.release()
        return {"status": "not_found", "message": "Лицо пользователя не найдено."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
