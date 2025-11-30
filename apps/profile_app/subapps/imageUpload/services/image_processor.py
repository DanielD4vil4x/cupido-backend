"""
Servicio de procesamiento de imágenes.
Lógica de negocio: Comprimir y redimensionar imágenes para cumplir con el límite
de 400KB antes de guardarlas en MinIO. Esto optimiza el almacenamiento y mejora
los tiempos de carga en el frontend.
"""
import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


class ImageProcessor:
    """
    Procesador de imágenes que comprime y redimensiona automáticamente
    para cumplir con los límites de tamaño establecidos.
    """
    
    # Tamaño máximo en bytes (400KB por defecto)
    MAX_SIZE_BYTES = getattr(settings, 'PHOTO_MAX_UPLOAD_SIZE', 400 * 1024)
    
    # Dimensión máxima (ancho o alto) para redimensionar
    MAX_DIMENSION = 1080
    
    # Calidad inicial de compresión JPEG
    INITIAL_QUALITY = 85
    
    # Calidad mínima aceptable (no bajar de esto)
    MIN_QUALITY = 40

    @classmethod
    def process_image(cls, uploaded_file) -> InMemoryUploadedFile:
        """
        Procesa una imagen subida: redimensiona y comprime si es necesario.
        
        Args:
            uploaded_file: Archivo subido (InMemoryUploadedFile o similar)
            
        Returns:
            InMemoryUploadedFile: Imagen procesada lista para guardar
            
        Lógica:
        1. Si la imagen ya está por debajo de 400KB, no hacer nada
        2. Redimensionar si excede MAX_DIMENSION
        3. Comprimir iterativamente hasta lograr el tamaño objetivo
        """
        # Leer la imagen original
        original_size = uploaded_file.size
        
        # Si ya está dentro del límite, devolver sin procesar
        if original_size <= cls.MAX_SIZE_BYTES:
            uploaded_file.seek(0)
            return uploaded_file
        
        # Abrir con Pillow
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        
        # Convertir a RGB si es necesario (para JPEG)
        if img.mode in ('RGBA', 'P'):
            # Crear fondo blanco para imágenes con transparencia
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar si excede dimensiones máximas
        img = cls._resize_if_needed(img)
        
        # Comprimir iterativamente hasta lograr el tamaño objetivo
        output_buffer = cls._compress_to_target_size(img)
        
        # Crear nuevo InMemoryUploadedFile
        output_buffer.seek(0)
        processed_file = InMemoryUploadedFile(
            file=output_buffer,
            field_name=uploaded_file.field_name if hasattr(uploaded_file, 'field_name') else 'imagen',
            name=cls._ensure_jpg_extension(uploaded_file.name),
            content_type='image/jpeg',
            size=output_buffer.getbuffer().nbytes,
            charset=None
        )
        
        return processed_file
    
    @classmethod
    def _resize_if_needed(cls, img: Image.Image) -> Image.Image:
        """
        Redimensiona la imagen si excede las dimensiones máximas.
        Mantiene la proporción original (aspect ratio).
        """
        width, height = img.size
        
        if width <= cls.MAX_DIMENSION and height <= cls.MAX_DIMENSION:
            return img
        
        # Calcular nuevo tamaño manteniendo proporción
        if width > height:
            new_width = cls.MAX_DIMENSION
            new_height = int(height * (cls.MAX_DIMENSION / width))
        else:
            new_height = cls.MAX_DIMENSION
            new_width = int(width * (cls.MAX_DIMENSION / height))
        
        # Usar LANCZOS para mejor calidad de redimensionado
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    @classmethod
    def _compress_to_target_size(cls, img: Image.Image) -> io.BytesIO:
        """
        Comprime la imagen iterativamente hasta lograr el tamaño objetivo.
        Reduce la calidad gradualmente si es necesario.
        """
        quality = cls.INITIAL_QUALITY
        
        while quality >= cls.MIN_QUALITY:
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            if buffer.getbuffer().nbytes <= cls.MAX_SIZE_BYTES:
                return buffer
            
            # Reducir calidad en 10% para siguiente intento
            quality -= 10
        
        # Si aún no cumple, devolver con calidad mínima
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=cls.MIN_QUALITY, optimize=True)
        return buffer
    
    @staticmethod
    def _ensure_jpg_extension(filename: str) -> str:
        """Asegura que el archivo tenga extensión .jpg"""
        if '.' in filename:
            name = filename.rsplit('.', 1)[0]
        else:
            name = filename
        return f"{name}.jpg"
