import os
import uuid
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from PIL import Image
from app.models import ProductPhoto, Product
from app.schemas.product_photo import ProductPhotoCreate, ProductPhotoUpdate
from fastapi import HTTPException, status, UploadFile


class ProductPhotoService:
    """Сервис для работы с фото товаров"""
    
    UPLOAD_DIR = Path("app/static/uploads/products")
    MAX_PHOTOS_PER_PRODUCT = 6
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def ensure_upload_dir(cls):
        """Создаёт директорию для загрузки, если её нет"""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_valid_file(cls, file: UploadFile) -> bool:
        """Проверяет, подходит ли файл для загрузки"""
        if not file.filename:
            return False
        
        # Проверяем расширение
        ext = Path(file.filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False
        
        # Проверяем MIME-тип
        if not file.content_type or not file.content_type.startswith('image/'):
            return False
        
        return True
    
    @classmethod
    async def save_photo(cls, file: UploadFile, product_id: int, db: Session, is_main: bool = False, sort_order: int = 0) -> ProductPhoto:
        """Сохраняет загруженное фото"""
        cls.ensure_upload_dir()
        
        if not cls.is_valid_file(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неподдерживаемый тип файла"
            )
        
        # Проверяем количество фото для товара
        existing_photos = db.query(ProductPhoto).filter(ProductPhoto.product_id == product_id).count()
        if existing_photos >= cls.MAX_PHOTOS_PER_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Максимальное количество фото для товара: {cls.MAX_PHOTOS_PER_PRODUCT}"
            )
        
        # Генерируем уникальное имя файла
        ext = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4()}{ext}"
        file_path = cls.UPLOAD_DIR / filename
        
        # Сохраняем файл
        content = await file.read()
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл слишком большой"
            )
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Сжимаем изображение
        try:
            with Image.open(file_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Сжимаем если изображение слишком большое
                if img.width > 1920 or img.height > 1080:
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    img.save(file_path, quality=85, optimize=True)
        except Exception as e:
            # Если не удалось обработать изображение, удаляем файл
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обработки изображения: {str(e)}"
            )
        
        # Создаём запись в БД
        photo_data = ProductPhotoCreate(
            product_id=product_id,
            filename=filename,
            original_filename=file.filename,
            file_path=str(file_path).replace('\\', '/'),  # Нормализуем путь для веб
            file_size=len(content),
            mime_type=file.content_type,
            is_main=is_main,
            sort_order=sort_order
        )
        
        photo = ProductPhoto(**photo_data.dict())
        db.add(photo)
        db.commit()
        db.refresh(photo)
        
        return photo
    
    @staticmethod
    def get_product_photos(db: Session, product_id: int) -> List[ProductPhoto]:
        """Получает все фото товара"""
        return db.query(ProductPhoto).filter(
            ProductPhoto.product_id == product_id
        ).order_by(ProductPhoto.sort_order, ProductPhoto.created_at).all()
    
    @staticmethod
    def get_main_photo(db: Session, product_id: int) -> Optional[ProductPhoto]:
        """Получает главное фото товара"""
        return db.query(ProductPhoto).filter(
            ProductPhoto.product_id == product_id,
            ProductPhoto.is_main == True
        ).first()
    
    @staticmethod
    def delete_photo(db: Session, photo_id: int) -> bool:
        """Удаляет фото товара"""
        photo = db.query(ProductPhoto).filter(ProductPhoto.id == photo_id).first()
        if not photo:
            return False
        
        # Удаляем файл
        try:
            if os.path.exists(photo.file_path):
                os.remove(photo.file_path)
        except OSError:
            pass  # Игнорируем ошибки удаления файла
        
        # Удаляем запись из БД
        db.delete(photo)
        db.commit()
        return True
    
    @staticmethod
    def update_photo(db: Session, photo_id: int, photo_data: ProductPhotoUpdate) -> Optional[ProductPhoto]:
        """Обновляет фото товара"""
        photo = db.query(ProductPhoto).filter(ProductPhoto.id == photo_id).first()
        if not photo:
            return None
        
        # Если устанавливаем как главное, убираем главное у других фото
        if photo_data.is_main:
            db.query(ProductPhoto).filter(
                ProductPhoto.product_id == photo.product_id,
                ProductPhoto.is_main == True
            ).update({"is_main": False})
        
        # Обновляем поля
        for field, value in photo_data.dict(exclude_unset=True).items():
            setattr(photo, field, value)
        
        db.commit()
        db.refresh(photo)
        return photo
    
    @staticmethod
    def reorder_photos(db: Session, product_id: int, photo_ids: List[int]) -> bool:
        """Изменяет порядок фото товара"""
        for index, photo_id in enumerate(photo_ids):
            db.query(ProductPhoto).filter(
                ProductPhoto.id == photo_id,
                ProductPhoto.product_id == product_id
            ).update({"sort_order": index})
        
        db.commit()
        return True
