from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
import face_recognition
from .models import Personal


@receiver(post_save, sender=Personal)
def process_avatar_face_encoding(sender, instance, created, **kwargs):
    if instance.avatar and created:
        try:
            image_path = instance.avatar.path
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if face_encodings:
                instance.face_encoding = face_encodings[0].tolist()
                instance.save()
                
        except Exception as e:
            print(f"Ошибка при обработке лица: {e}")