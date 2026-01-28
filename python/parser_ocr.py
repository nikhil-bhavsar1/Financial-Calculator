
import logging
import re
import time
from typing import List, Dict, Optional, Tuple, Any, Union, Callable
from collections import defaultdict

# Import configuration and constants
from parser_config import (
    ParserConfig, OCRResult, OCRStatus,
    CV2_AVAILABLE, PYMUPDF_AVAILABLE, TESSERACT_AVAILABLE, EASYOCR_AVAILABLE
)

# Re-import optional dependencies to ensure symbols are available in this module's scope
if CV2_AVAILABLE:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
else:
    cv2 = None
    np = None
    Image = None

if PYMUPDF_AVAILABLE:
    import fitz
else:
    fitz = None

if TESSERACT_AVAILABLE:
    import pytesseract
else:
    pytesseract = None

if EASYOCR_AVAILABLE:
    import easyocr
else:
    easyocr = None

logger = logging.getLogger(__name__)

# =============================================================================
# OCR Module
# =============================================================================

class ImagePreprocessor:
    """
    Preprocesses images for better OCR accuracy.
    Handles deskewing, contrast enhancement, noise removal, and thresholding.
    """
    
    @staticmethod
    def is_available() -> bool:
        """Check if image processing is available."""
        return CV2_AVAILABLE
    
    @staticmethod
    def deskew(image: np.ndarray, max_angle: float = 10.0) -> np.ndarray:
        """
        Correct skew in the image.
        
        Args:
            image: Input image
            max_angle: Maximum angle to correct (degrees)
        """
        if not CV2_AVAILABLE:
            return image
            
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Use Hough transform to detect lines
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is None or len(lines) < 5:
                # Fallback to minAreaRect method
                coords = np.column_stack(np.where(gray > 0))
                if len(coords) < 100:
                    return image
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
            else:
                # Calculate median angle from detected lines
                angles = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if x2 - x1 != 0:
                        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                        if abs(angle) < max_angle:
                            angles.append(angle)
                
                if not angles:
                    return image
                angle = np.median(angles)
            
            # Only correct if angle is significant
            if abs(angle) < 0.5:
                return image
            
            # Limit correction angle
            angle = np.clip(angle, -max_angle, max_angle)
            
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
            
        except Exception as e:
            logger.debug(f"Deskew failed: {e}")
            return image
    
    @staticmethod
    def enhance_contrast(image: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """
        Enhance image contrast using CLAHE.
        
        Args:
            image: Input image
            clip_limit: Threshold for contrast limiting
        """
        if not CV2_AVAILABLE:
            return image
            
        try:
            # Convert toLAB color space for better contrast enhancement
            if len(image.shape) == 3:
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
                l = clahe.apply(l)
                enhanced = cv2.merge([l, a, b])
                return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            else:
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
                return clahe.apply(image)
                
        except Exception as e:
            logger.debug(f"Contrast enhancement failed: {e}")
            return image
    
    @staticmethod
    def remove_noise(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Remove noise from image using Non-local Means Denoising.
        
        Args:
            image: Input image
            strength: Filter strength (higher = more denoising)
        """
        if not CV2_AVAILABLE:
            return image
            
        try:
            if len(image.shape) == 3:
                return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
            else:
                return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)
                
        except Exception as e:
            logger.debug(f"Noise removal failed: {e}")
            # Fallback to bilateral filter
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
                return cv2.bilateralFilter(gray, 9, 75, 75)
            except:
                return image
    
    @staticmethod
    def apply_threshold(image: np.ndarray, method: str = 'adaptive') -> np.ndarray:
        """
        Apply thresholding to make text more distinct.
        
        Args:
            image: Input image
            method: 'adaptive', 'otsu', or 'binary'
        """
        if not CV2_AVAILABLE:
            return image
            
        try:
            # Ensure grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            if method == 'adaptive':
                thresh = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    11, 2
                )
            elif method == 'otsu':
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif method == 'sauvola':
                # Sauvola thresholding (good for documents)
                window_size = 25
                k = 0.2
                mean = cv2.blur(gray.astype(np.float64), (window_size, window_size))
                mean_sq = cv2.blur(gray.astype(np.float64) ** 2, (window_size, window_size))
                std = np.sqrt(mean_sq - mean ** 2)
                threshold = mean * (1 + k * (std / 128 - 1))
                thresh = (gray > threshold).astype(np.uint8) * 255
            else:
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            return thresh
            
        except Exception as e:
            logger.debug(f"Thresholding failed: {e}")
            return image
    
    @staticmethod
    def resize_for_ocr(image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """
        Resize image to target DPI for optimal OCR.
        
        Args:
            image: Input image
            target_dpi: Target DPI (300 is optimal for most OCR engines)
        """
        if not CV2_AVAILABLE:
            return image
            
        try:
            height, width = image.shape[:2]
            
            # Assume input is 72 DPI if small, estimate actual DPI
            # Standard A4 at 72 DPI is about 595x842
            estimated_dpi = 72 if width < 1000 else 150
            
            scale = target_dpi / estimated_dpi
            
            if scale > 0.9 and scale < 1.1:
                return image
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Use INTER_CUBIC for upscaling, INTER_AREA for downscaling
            interpolation = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
            
            return cv2.resize(image, (new_width, new_height), interpolation=interpolation)
            
        except Exception as e:
            logger.debug(f"Resize failed: {e}")
            return image
    
    @staticmethod
    def remove_borders(image: np.ndarray, border_percent: float = 0.02) -> np.ndarray:
        """
        Remove borders from image (common in scanned documents).
        
        Args:
            image: Input image
            border_percent: Percentage of image to remove from each edge
        """
        if not CV2_AVAILABLE:
            return image
            
        try:
            h, w = image.shape[:2]
            border_h = int(h * border_percent)
            border_w = int(w * border_percent)
            
            return image[border_h:h-border_h, border_w:w-border_w]
            
        except Exception as e:
            logger.debug(f"Border removal failed: {e}")
            return image
    
    @classmethod
    def preprocess_for_ocr(
        cls,
        image: np.ndarray,
        deskew: bool = True,
        enhance_contrast: bool = True,
        remove_noise: bool = True,
        threshold: bool = True,
        resize: bool = True,
        remove_borders: bool = False
    ) -> np.ndarray:
        """
        Full preprocessing pipeline for OCR.
        
        Args:
            image: Input image (numpy array)
            deskew: Whether to correct skew
            enhance_contrast: Whether to enhance contrast
            remove_noise: Whether to remove noise
            threshold: Whether to apply thresholding
            resize: Whether to resize for optimal OCR
            remove_borders: Whether to remove borders
            
        Returns:
            Preprocessed image
        """
        if not CV2_AVAILABLE:
            logger.warning("Image processing not available")
            return image
            
        try:
            result = image.copy()
            
            if remove_borders:
                result = cls.remove_borders(result)
            
            if resize:
                result = cls.resize_for_ocr(result)
            
            if deskew:
                result = cls.deskew(result)
            
            if remove_noise:
                result = cls.remove_noise(result)
            
            if enhance_contrast:
                result = cls.enhance_contrast(result)
            
            if threshold:
                result = cls.apply_threshold(result, method='adaptive')
            
            return result
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return image


class OCREngine:
    """
    OCR Engine wrapper supporting multiple backends.
    Primary: Tesseract (pytesseract)
    Fallback: EasyOCR (if available)
    """
    
    def __init__(self, preferred_engine: str = 'tesseract'):
        self.preferred_engine = preferred_engine
        self.tesseract_available = self._check_tesseract()
        self.easyocr_available = EASYOCR_AVAILABLE
        self.easyocr_reader = None
        self._init_status_logged = False
        
        if not self.tesseract_available and not self.easyocr_available:
            logger.warning("No OCR engine available. Install pytesseract or easyocr.")
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available and working."""
        if not TESSERACT_AVAILABLE:
            return False
            
        try:
            version = pytesseract.get_tesseract_version()
            if not self._init_status_logged:
                logger.info(f"Tesseract version: {version}")
            return True
        except Exception as e:
            logger.debug(f"Tesseract not available: {e}")
            return False
    
    def _init_easyocr(self):
        """Initialize EasyOCR reader on demand (lazy loading)."""
        if self.easyocr_reader is None and self.easyocr_available:
            try:
                import easyocr as easyocr_module
                # Support English and Hindi (common in Indian financial reports)
                self.easyocr_reader = easyocr_module.Reader(
                    ['en', 'hi'],
                    gpu=False,
                    verbose=False
                )
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                self.easyocr_available = False
    
    @property
    def is_available(self) -> bool:
        """Check if any OCR engine is available."""
        return self.tesseract_available or self.easyocr_available
    
    def get_active_engine(self) -> str:
        """Get the name of the active OCR engine."""
        if self.preferred_engine == 'tesseract' and self.tesseract_available:
            return 'tesseract'
        elif self.preferred_engine == 'easyocr' and self.easyocr_available:
            return 'easyocr'
        elif self.tesseract_available:
            return 'tesseract'
        elif self.easyocr_available:
            return 'easyocr'
        return 'none'
    
    def recognize(
        self,
        image: np.ndarray,
        preprocess: bool = True,
        config: Optional[Dict] = None
    ) -> Tuple[str, float]:
        """
        Perform OCR on an image.
        
        Args:
            image: Input image (numpy array)
            preprocess: Whether to preprocess the image
            config: Additional OCR configuration
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not self.is_available:
            raise RuntimeError("No OCR engine available")
        
        if config is None:
            config = {}
        
        # Preprocess if requested
        if preprocess and CV2_AVAILABLE:
            image = ImagePreprocessor.preprocess_for_ocr(image)
        
        active_engine = self.get_active_engine()
        
        if active_engine == 'tesseract':
            return self._tesseract_ocr(image, config)
        elif active_engine == 'easyocr':
            return self._easyocr_ocr(image, config)
        
        return "", 0.0
    
    def _tesseract_ocr(self, image: np.ndarray, config: Dict) -> Tuple[str, float]:
        """Perform OCR using Tesseract."""
        if not self.tesseract_available:
            return "", 0.0
        
        # Custom config optimized for financial documents
        psm = config.get('psm', 6)  # Assume uniform block of text
        custom_config = f'--oem 3 --psm {psm}'
        
        # Add character whitelist for financial documents
        if config.get('financial_mode', True):
            custom_config += ' -c tessedit_char_whitelist="0123456789.,()$₹%&/-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "'
        
        try:
            # Get detailed data with confidence scores
            data = pytesseract.image_to_data(
                image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            text_parts = []
            confidences = []
            current_line = []
            last_line_num = 0
            
            for i, text in enumerate(data['text']):
                line_num = data['line_num'][i]
                conf = float(data['conf'][i])
                
                # New line
                if line_num != last_line_num and current_line:
                    text_parts.append(' '.join(current_line))
                    current_line = []
                    last_line_num = line_num
                
                # Filter low confidence words
                if conf > 30 and text.strip():
                    current_line.append(text)
                    confidences.append(conf)
            
            # Don't forget last line
            if current_line:
                text_parts.append(' '.join(current_line))
            
            full_text = '\n'.join(text_parts)
            avg_confidence = float(np.mean(confidences)) if confidences else 0.0
            
            return full_text, avg_confidence
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            
            # Fallback to simple string extraction
            try:
                text = pytesseract.image_to_string(image, config=custom_config)
                return text, 50.0
            except Exception as e2:
                logger.error(f"Tesseract fallback failed: {e2}")
                return "", 0.0
    
    def _easyocr_ocr(self, image: np.ndarray, config: Dict) -> Tuple[str, float]:
        """Perform OCR using EasyOCR."""
        self._init_easyocr()
        
        if not self.easyocr_reader:
            return "", 0.0
        
        try:
            # EasyOCR expects RGB images
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Perform OCR
            results = self.easyocr_reader.readtext(
                image,
                paragraph=config.get('paragraph', False),
                min_size=config.get('min_size', 10)
            )
            
            # Sort by vertical position for proper line ordering
            results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
            
            text_parts = []
            confidences = []
            
            for (bbox, text, conf) in results:
                if text.strip():
                    text_parts.append(text)
                    confidences.append(conf * 100)
            
            full_text = ' '.join(text_parts)
            avg_confidence = float(np.mean(confidences)) if confidences else 0.0
            
            return full_text, avg_confidence
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return "", 0.0


class OCRProcessor:
    """
    High-level OCR processor for PDF documents.
    Handles page extraction, OCR, and caching.
    """
    
    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()
        self.ocr_engine = OCREngine(preferred_engine=self.config.ocr_engine)
        self.cache: Dict[str, OCRResult] = {}
        self.preprocessor = ImagePreprocessor()
        self._stats = defaultdict(int)
    
    @property
    def is_available(self) -> bool:
        """Check if OCR is available."""
        return self.ocr_engine.is_available and CV2_AVAILABLE and PYMUPDF_AVAILABLE
    
    def _get_cache_key(self, pdf_path: str, page_num: int) -> str:
        """Generate cache key for a page."""
        return f"{pdf_path}_{page_num}"
    
    def needs_ocr(self, page) -> bool:
        """
        Determine if a page needs OCR processing.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            True if OCR is needed
        """
        try:
            text = page.get_text("text").strip()
            
            # If we have substantial text with numbers, no need for OCR
            word_count = len(text.split())
            number_count = len(re.findall(r'\d+', text))
            
            if word_count > 50 and number_count > 10:
                return False
            
            # Check for images
            image_list = page.get_images(full=True)
            
            # If very little text but has large images, likely needs OCR
            if word_count < 20 and image_list:
                # Check if images are substantial
                for img_info in image_list:
                    xref = img_info[0]
                    try:
                        img = page.parent.extract_image(xref)
                        if img and img.get('width', 0) > 200 and img.get('height', 0) > 200:
                            return True
                    except:
                        pass
            
            # Check page size vs text amount
            page_area = page.rect.width * page.rect.height
            text_density = len(text) / page_area if page_area > 0 else 0
            
            # Very low text density with images suggests OCR needed
            if text_density < 0.001 and image_list:
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking if page needs OCR: {e}")
            return False
    
    def extract_page_image(self, page, zoom: float = 2.0) -> np.ndarray:
        """
        Extract page as image for OCR processing.
        
        Args:
            page: PyMuPDF page object
            zoom: Zoom factor for higher resolution
            
        Returns:
            numpy array of the page image
        """
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF not available")
        
        try:
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to numpy array
            img_data = pix.tobytes("png")
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to extract page image: {e}")
            raise
    
    def process_page(
        self,
        page,
        page_num: int,
        pdf_path: str = "",
        force_ocr: bool = False,
        preprocess: bool = True
    ) -> OCRResult:
        """
        Process a single page with OCR.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
            pdf_path: Path to PDF for caching
            force_ocr: Force OCR even if text is extractable
            preprocess: Apply image preprocessing
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(pdf_path, page_num)
        if self.config.cache_ocr_results and cache_key in self.cache and not force_ocr:
            cached = self.cache[cache_key]
            self._stats['cache_hits'] += 1
            return OCRResult(
                page_num=cached.page_num,
                text=cached.text,
                confidence=cached.confidence,
                status=OCRStatus.CACHED,
                processing_time=0.0,
                method=cached.method
            )
        
        # Check if OCR is needed
        if not force_ocr and not self.needs_ocr(page):
            try:
                text = page.get_text("text")
                processing_time = time.time() - start_time
                
                result = OCRResult(
                    page_num=page_num,
                    text=text,
                    confidence=100.0,
                    status=OCRStatus.NOT_NEEDED,
                    processing_time=processing_time,
                    method="native"
                )
                
                if self.config.cache_ocr_results:
                    self.cache[cache_key] = result
                
                self._stats['native_extractions'] += 1
                return result
                
            except Exception as e:
                logger.debug(f"Native text extraction failed: {e}")
        
        # Perform OCR
        if not self.is_available:
            return OCRResult(
                page_num=page_num,
                text="",
                confidence=0.0,
                status=OCRStatus.FAILED,
                processing_time=time.time() - start_time,
                method="none",
                error_message="OCR not available"
            )
        
        try:
            # Extract image
            image = self.extract_page_image(page)
            
            # Perform OCR
            text, confidence = self.ocr_engine.recognize(
                image,
                preprocess=preprocess,
                config={'financial_mode': True, 'psm': 6}
            )
            
            processing_time = time.time() - start_time
            
            # Determine status
            if confidence >= self.config.ocr_confidence_threshold and text.strip():
                status = OCRStatus.SUCCESS
                self._stats['ocr_successes'] += 1
            else:
                status = OCRStatus.FAILED
                self._stats['ocr_failures'] += 1
            
            result = OCRResult(
                page_num=page_num,
                text=text,
                confidence=confidence,
                status=status,
                processing_time=processing_time,
                method=self.ocr_engine.get_active_engine()
            )
            
            if self.config.cache_ocr_results:
                self.cache[cache_key] = result
            
            logger.info(
                f"OCR Page {page_num + 1}: {confidence:.1f}% confidence, "
                f"{len(text)} chars ({processing_time:.2f}s)"
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._stats['ocr_errors'] += 1
            
            return OCRResult(
                page_num=page_num,
                text="",
                confidence=0.0,
                status=OCRStatus.FAILED,
                processing_time=processing_time,
                method="none",
                error_message=str(e)
            )
    
    def process_pages(
        self,
        doc,
        page_nums: Optional[List[int]] = None,
        pdf_path: str = "",
        force_ocr: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> List[OCRResult]:
        """
        Process multiple pages with OCR.
        
        Args:
            doc: PyMuPDF document
            page_nums: Specific pages to process (None = all)
            pdf_path: Path to PDF for caching
            force_ocr: Force OCR on all pages
            progress_callback: Optional callback(current, total, result)
            
        Returns:
            List of OCRResult objects
        """
        results = []
        
        if page_nums is None:
            page_nums = list(range(len(doc)))
        
        total = len(page_nums)
        
        for i, page_num in enumerate(page_nums):
            if page_num >= len(doc):
                continue
            
            page = doc[page_num]
            result = self.process_page(page, page_num, pdf_path, force_ocr)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total, result)
        
        return results
    
    def get_combined_text(self, results: List[OCRResult]) -> str:
        """Combine OCR results into single text with page markers."""
        parts = []
        for result in results:
            if result.is_successful and result.text.strip():
                parts.append(f"\n### PAGE {result.page_num + 1} ###\n")
                parts.append(result.text)
        return '\n'.join(parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get OCR processing statistics."""
        return {
            "cache_hits": self._stats['cache_hits'],
            "native_extractions": self._stats['native_extractions'],
            "ocr_successes": self._stats['ocr_successes'],
            "ocr_failures": self._stats['ocr_failures'],
            "ocr_errors": self._stats['ocr_errors'],
            "engine": self.ocr_engine.get_active_engine(),
            "cache_size": len(self.cache)
        }
    
    def clear_cache(self):
        """Clear OCR cache."""
        self.cache.clear()
        logger.info("OCR cache cleared")
