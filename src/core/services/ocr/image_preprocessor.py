"""
Image Preprocessor (SRP: Single Responsibility)
Only handles image preprocessing for better OCR results
"""

from PIL import Image, ImageEnhance, ImageFilter
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class PreprocessConfig:
    """Image preprocessing configuration"""
    convert_grayscale: bool = True
    contrast_factor: float = 2.0
    apply_sharpen: bool = True
    min_width: int = 1200
    crop_ratio: Optional[Tuple[float, float]] = None  # (top_ratio, bottom_ratio) - e.g., (0.4, 1.0) for bottom 60%


class ImagePreprocessor:
    """
    Image preprocessor for OCR optimization
    Separates image processing from OCR logic (SRP)
    """

    def __init__(self, config: Optional[PreprocessConfig] = None):
        """
        Initialize preprocessor

        Args:
            config: PreprocessConfig instance or None for defaults
        """
        self._config = config or PreprocessConfig()

    def process(self, image: Image.Image, fast_mode: bool = False) -> Image.Image:
        """
        Process image for better OCR recognition

        Args:
            image: PIL Image to process
            fast_mode: If True, only process bottom portion

        Returns:
            Processed PIL Image
        """
        processed = image.copy()

        # Convert to grayscale
        if self._config.convert_grayscale:
            processed = processed.convert('L')

        # Increase contrast
        if self._config.contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(self._config.contrast_factor)

        # Apply sharpening
        if self._config.apply_sharpen:
            processed = processed.filter(ImageFilter.SHARPEN)

        # Resize for better OCR (larger text = better recognition)
        width, height = processed.size
        if width < self._config.min_width:
            scale_factor = self._config.min_width / width
            new_size = (int(width * scale_factor), int(height * scale_factor))
            processed = processed.resize(new_size, Image.LANCZOS)

        # Crop to region of interest (for fast mode)
        if fast_mode or self._config.crop_ratio:
            processed = self._crop_region(processed, fast_mode)

        return processed

    def _crop_region(self, image: Image.Image, fast_mode: bool) -> Image.Image:
        """
        Crop image to region of interest

        Args:
            image: PIL Image to crop
            fast_mode: If True, use default bottom 60% crop

        Returns:
            Cropped PIL Image
        """
        width, height = image.size

        if fast_mode:
            # Fast mode: only check bottom 60% where approval dialogs usually appear
            top_ratio = 0.4
            bottom_ratio = 1.0
        elif self._config.crop_ratio:
            top_ratio, bottom_ratio = self._config.crop_ratio
        else:
            return image

        top = int(height * top_ratio)
        bottom = int(height * bottom_ratio)
        return image.crop((0, top, width, bottom))

    def process_for_region(
        self,
        image: Image.Image,
        top_ratio: float,
        bottom_ratio: float
    ) -> Image.Image:
        """
        Process image and crop to specific region

        Args:
            image: PIL Image to process
            top_ratio: Top crop ratio (0.0 to 1.0)
            bottom_ratio: Bottom crop ratio (0.0 to 1.0)

        Returns:
            Processed and cropped PIL Image
        """
        processed = self.process(image, fast_mode=False)
        width, height = processed.size
        top = int(height * top_ratio)
        bottom = int(height * bottom_ratio)
        return processed.crop((0, top, width, bottom))
