"""
OCR Engine for text extraction
SOLID: Single Responsibility - Only handles OCR text extraction
"""
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

from .config import OCRSettings


class OCREngine:
    """Extracts text from images using Tesseract OCR"""

    def __init__(self, settings: OCRSettings):
        self.settings = settings
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path

    def preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results

        Args:
            img: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        img = img.convert('L')

        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(self.settings.contrast_factor)

        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)

        # Scale up if needed
        width, height = img.size
        if width < self.settings.min_scale_width:
            scale_factor = self.settings.min_scale_width / width
            new_size = (int(width * scale_factor), int(height * scale_factor))
            img = img.resize(new_size, Image.LANCZOS)

        return img

    def extract_text(self, img: Image.Image, fast_mode: bool = False) -> str:
        """
        Extract text from image using OCR

        Args:
            img: PIL Image object
            fast_mode: If True, use faster OCR with reduced accuracy

        Returns:
            Extracted text string
        """
        try:
            # Preprocess
            img = self.preprocess_image(img)

            if fast_mode:
                # Fast mode: scan bottom 60% only
                config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,?!():-\' '
                width, height = img.size
                bottom_region = img.crop((0, int(height * 0.4), width, height))
                text = pytesseract.image_to_string(
                    bottom_region,
                    lang=self.settings.language,
                    config=config
                )
            else:
                # Normal mode: full image
                config = r'--psm 6 --oem 3'
                text = pytesseract.image_to_string(
                    img,
                    lang=self.settings.language,
                    config=config
                )

                # If too little text, try bottom half
                if len(text) < 50:
                    width, height = img.size
                    bottom_region = img.crop((0, int(height * 0.5), width, height))
                    text = pytesseract.image_to_string(
                        bottom_region,
                        lang=self.settings.language,
                        config=config
                    )

            return text

        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
            return ""

    def extract_text_from_region(
        self,
        img: Image.Image,
        top_percent: float = 0.0,
        bottom_percent: float = 1.0
    ) -> str:
        """
        Extract text from specific region of image

        Args:
            img: PIL Image object
            top_percent: Start from this percentage of height (0.0 = top)
            bottom_percent: End at this percentage of height (1.0 = bottom)

        Returns:
            Extracted text string
        """
        try:
            img = self.preprocess_image(img)
            width, height = img.size

            region = img.crop((
                0,
                int(height * top_percent),
                width,
                int(height * bottom_percent)
            ))

            config = r'--psm 6 --oem 3'
            return pytesseract.image_to_string(
                region,
                lang=self.settings.language,
                config=config
            )

        except Exception as e:
            print(f"[ERROR] OCR region extraction failed: {e}")
            return ""

    def is_available(self) -> bool:
        """Check if Tesseract OCR is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
