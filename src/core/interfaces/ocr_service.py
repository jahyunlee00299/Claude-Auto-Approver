"""
OCR Service Interface (ISP: Interface Segregation Principle)
Defines contract for OCR text extraction operations only
"""

from abc import ABC, abstractmethod
from PIL import Image


class IOCRService(ABC):
    """
    OCR Service Interface (SRP: Single Responsibility)
    Only handles text extraction from images
    """

    @abstractmethod
    def extract_text(self, image: Image.Image, fast_mode: bool = False) -> str:
        """
        Extract text from image using OCR

        Args:
            image: PIL Image object to process
            fast_mode: If True, use faster but less accurate settings

        Returns:
            Extracted text as string
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if OCR service is available and properly configured

        Returns:
            True if OCR is ready to use
        """
        pass
