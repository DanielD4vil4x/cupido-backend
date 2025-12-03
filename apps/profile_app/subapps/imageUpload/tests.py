from django.urls import reverse
from django.test import override_settings
from django.core.files.storage import FileSystemStorage
from rest_framework.test import APITestCase
from apps.auth_app.models import Usuario
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import io
import tempfile
from PIL import Image


def create_image_file(name='test.jpg', size=(100, 100), color=(255, 0, 0)):
    """Crea un archivo de imagen de prueba en memoria"""
    file_obj = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file_obj, 'JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type='image/jpeg')


# Usar FileSystemStorage temporal para tests (no depender de MinIO)
TEST_STORAGE = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": tempfile.mkdtemp(),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


@override_settings(STORAGES=TEST_STORAGE)
class ImageUploadTests(APITestCase):
    """
    Tests para el feature de subida de imágenes.
    Usa FileSystemStorage temporal para no depender de MinIO en CI.
    """
    
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='user@example.com', 
            contrasena='123abc', 
            nombres='Test', 
            apellidos='User',
            fechanacimiento='1990-01-01'
        )
        self.client.force_authenticate(user=self.user)

    def test_upload_image_success(self):
        """Verifica que se puede subir una imagen correctamente"""
        url = reverse('profile:photo-list-create')
        image = create_image_file()
        response = self.client.post(url, {'imagen': image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('imagen', response.data)
        self.assertEqual(response.data['usuario'], self.user.usuario_id)

    def test_upload_non_image_failure(self):
        """Verifica que se rechaza un archivo que no es imagen"""
        url = reverse('profile:photo-list-create')
        dummy = SimpleUploadedFile('file.txt', b'just some text', content_type='text/plain')
        response = self.client.post(url, {'imagen': dummy}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_max_images_limit(self):
        """Verifica que no se pueden subir más de 3 imágenes por usuario"""
        url = reverse('profile:photo-list-create')
        for i in range(3):
            image = create_image_file(name=f'test{i}.jpg')
            r = self.client.post(url, {'imagen': image}, format='multipart')
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # La cuarta imagen debe fallar
        image4 = create_image_file(name='test3.jpg')
        response = self.client.post(url, {'imagen': image4}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_principal_image_toggle(self):
        """Verifica que solo puede haber una imagen principal por usuario"""
        url = reverse('profile:photo-list-create')
        image_a = create_image_file(name='a.jpg')
        image_b = create_image_file(name='b.jpg')
        r1 = self.client.post(url, {'imagen': image_a}, format='multipart')
        r2 = self.client.post(url, {'imagen': image_b}, format='multipart')
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)

        # Establecer la segunda imagen como principal
        photo_id = r2.data.get('id') or r2.data.get('imagen_id')
        detail_url = reverse('profile:photo-detail', args=[photo_id])
        patch_res = self.client.patch(detail_url, {'es_principal': True}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)

        # Verificar que la primera imagen ya no es principal
        first_id = r1.data.get('id') or r1.data.get('imagen_id')
        first_detail = reverse('profile:photo-detail', args=[first_id])
        first_res = self.client.get(first_detail)
        self.assertEqual(first_res.status_code, status.HTTP_200_OK)
        self.assertFalse(first_res.data.get('es_principal'))

    def test_delete_image(self):
        """Verifica que se puede eliminar una imagen"""
        url = reverse('profile:photo-list-create')
        image = create_image_file(name='delete_test.jpg')
        r = self.client.post(url, {'imagen': image}, format='multipart')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        
        photo_id = r.data.get('id')
        detail_url = reverse('profile:photo-detail', args=[photo_id])
        delete_res = self.client.delete(detail_url)
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que ya no existe
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)
