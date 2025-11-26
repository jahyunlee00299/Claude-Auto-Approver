"""
Tesseract OCR Service Implementation (SRP: Single Responsibility)
Only handles OCR text extraction using Tesseract
"""

from typing import Optional
from PIL import Image

from ...interfaces import IOCRService
from .image_preprocessor import ImagePreprocessor

# Tesseract import - lazy loaded
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class TesseractOCRService(IOCRService):
    """
    Tesseract-based OCR service implementation
    Implements IOCRService interface (DIP: depends on abstraction)
    """

    DEFAULT_TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def __init__(
        self,
        tesseract_path: Optional[str] = None,
        preprocessor: Optional[ImagePreprocessor] = None,
        language: str = 'eng'
    ):
        """
        Initialize Tesseract OCR Service

        Args:
            tesseract_path: Path to tesseract executable
            preprocessor: ImagePreprocessor instance (DIP: dependency injection)
            language: OCR language code
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract is not installed. Install with: pip install pytesseract")

        self._tesseract_path = tesseract_path or self.DEFAULT_TESSERACT_PATH
        self._preprocessor = preprocessor or ImagePreprocessor()
        self._language = language

        # Configure pytesseract
        pytesseract.pytesseract.tesseract_cmd = self._tesseract_path

    def extract_text(self, image: Image.Image, fast_mode: bool = False) -> str:
        """
        Extract text from image using Tesseract OCR

        Args:
            image: PIL Image to process
            fast_mode: If True, use faster but less accurate settings

        Returns:
            Extracted text as string
        """
        try:
            # Preprocess image
            processed_image = self._preprocessor.process(image, fast_mode=fast_mode)

            # OCR configuration
            if fast_mode:
                config = self._get_fast_config()
            else:
                config = self._get_normal_config()

            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                lang=self._language,
                config=config
            )

            # If too little text in normal mode, try bottom half
            if not fast_mode and len(text) < 50:
                bottom_image = self._preprocessor.process_for_region(image, 0.5, 1.0)
                text = pytesseract.image_to_string(
                    bottom_image,
                    lang=self._language,
                    config=config
                )

            return text

        except Exception:
            return ""

    def _get_fast_config(self) -> str:
        """Get Tesseract config for fast mode"""
        # PSM 6: Assume a single uniform block of text
        # OEM 3: Default, based on what is available
        whitelist = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,?!():-\' '
        return f'--psm 6 --oem 3 -c tessedit_char_whitelist={whitelist}'

    def _get_normal_config(self) -> str:
        """Get Tesseract config for normal mode"""
        return '--psm 6 --oem 3'

    def is_available(self) -> bool:
        """
        Check if Tesseract is available and properly configured

        Returns:
            True if Tesseract is ready to use
        """
        if not TESSERACT_AVAILABLE:
            return False

        try:
            # Try to get Tesseract version
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def get_tesseract_version(self) -> Optional[str]:
        """
        Get Tesseract version string

        Returns:
            Version string or None if not available
        """
        try:
            return str(pytesseract.get_tesseract_version())
        except Exception:
            return None
