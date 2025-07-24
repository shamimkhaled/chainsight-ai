import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import PyPDF2
import docx
import os
import logging
import signal
import gc
from functools import wraps

logger = logging.getLogger(__name__)

def timeout_decorator(seconds):
    """Decorator to add timeout to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set the timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                signal.alarm(0)  # Disable the alarm
                signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
        return wrapper
    return decorator

class ContractDocumentProcessor:
    """Enhanced processor with OCR capabilities for scanned documents using PIL only"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.docx', '.jpg', '.jpeg', '.png']
        
        # Configure pytesseract
        try:
            pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
            # Test tesseract
            pytesseract.get_tesseract_version()
            logger.info("Tesseract initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tesseract: {str(e)}")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            return f"Error extracting PDF: {str(e)}"

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            return f"Error extracting DOCX: {str(e)}"

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting TXT: {str(e)}")
            return f"Error extracting TXT: {str(e)}"

    def is_scanned_pdf(self, file_path: str) -> bool:
        """Detect if PDF contains scanned images vs searchable text"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                # Check first few pages
                pages_to_check = min(3, len(reader.pages))
                for i in range(pages_to_check):
                    text += reader.pages[i].extract_text()
                
                # If very little text extracted, likely scanned
                words = len(text.strip().split())
                is_scanned = words < 20
                logger.info(f"PDF analysis: {words} words extracted. {'Scanned' if is_scanned else 'Searchable'} PDF detected.")
                return is_scanned
        except Exception as e:
            logger.error(f"Error analyzing PDF: {str(e)}")
            return True  # Assume scanned if can't analyze

    def preprocess_image_for_ocr(self, pil_image):
        """Preprocess PIL image for better OCR results with memory optimization"""
        try:
            # Resize if image is too large (save memory)
            max_size = 2000
            if pil_image.width > max_size or pil_image.height > max_size:
                logger.info(f"Resizing large image from {pil_image.width}x{pil_image.height}")
                pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to grayscale if needed
            if pil_image.mode != 'L':
                gray_image = pil_image.convert('L')
            else:
                gray_image = pil_image
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced = enhancer.enhance(1.5)  # Reduced from 2.0 to save memory
            
            # Apply sharpening filter (lighter processing)
            sharpened = enhanced.filter(ImageFilter.SHARPEN)
            
            # Convert to binary (black and white)
            threshold = 128
            binary_image = sharpened.point(lambda x: 0 if x < threshold else 255, '1')
            
            result = binary_image.convert('L')  # Convert back to grayscale mode
            
            # Clean up intermediate images
            del gray_image, enhanced, sharpened, binary_image
            gc.collect()
            
            return result
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return pil_image

    @timeout_decorator(30)  # 30 second timeout
    def extract_text_with_tesseract(self, pil_image) -> str:
        """Extract text using Tesseract OCR with PIL image and timeout"""
        try:
            # Configure Tesseract for better accuracy with faster processing
            custom_config = r'--oem 3 --psm 6 -c tessedit_do_invert=0'
            
            # Use timeout parameter in pytesseract
            text = pytesseract.image_to_string(
                pil_image, 
                config=custom_config,
                timeout=25  # 25 second timeout for pytesseract
            )
            return text
        except (pytesseract.TesseractError, TimeoutError) as e:
            logger.error(f"Tesseract OCR failed or timed out: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            return ""

    def extract_text_with_ocr(self, file_path: str) -> tuple:
        """Extract text from scanned PDFs using Tesseract OCR with PIL and memory optimization"""
        try:
            logger.info("Converting PDF pages to images...")
            
            # Check file size first
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning(f"File too large: {file_size} bytes. Limiting to first 3 pages.")
                max_pages = 3
            else:
                max_pages = 10  # Process max 10 pages to save memory
            
            # Convert PDF pages to images with reduced DPI for memory saving
            images = convert_from_path(
                file_path, 
                dpi=150,  # Reduced from 300 to save memory
                first_page=1,
                last_page=max_pages,
                thread_count=1  # Single thread to avoid memory issues
            )
            
            extracted_text = ""
            ocr_method = "tesseract_pil"
            
            for i, pil_image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)} with OCR...")
                
                try:
                    # Preprocess image with PIL
                    processed_image = self.preprocess_image_for_ocr(pil_image)
                    
                    # Use Tesseract for text extraction with timeout
                    page_text = self.extract_text_with_tesseract(processed_image)
                    
                    # Limit text length per page
                    if len(page_text) > 10000:
                        page_text = page_text[:10000] + "... [Page text truncated]"
                    
                    extracted_text += f"\n=== Page {i+1} ===\n{page_text}\n"
                    logger.info(f"  Extracted {len(page_text)} characters from page {i+1}")
                    
                    # Clean up memory after each page
                    del pil_image, processed_image
                    gc.collect()
                    
                except (TimeoutError, Exception) as e:
                    logger.error(f"Error processing page {i+1}: {str(e)}")
                    extracted_text += f"\n=== Page {i+1} ===\n[Error processing page: {str(e)}]\n"
                    continue
            
            # Final cleanup
            del images
            gc.collect()
            
            logger.info("OCR extraction completed.")
            return extracted_text, ocr_method
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return f"OCR extraction failed: {str(e)}", "failed"

    def extract_text_from_image(self, file_path: str) -> tuple:
        """Extract text from image files (JPG, PNG, etc.) using PIL with optimization"""
        try:
            logger.info("Processing image file with OCR...")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB limit for images
                logger.error(f"Image file too large: {file_size} bytes")
                return "Error: Image file too large (max 10MB)", "failed"
            
            # Load image with PIL
            pil_image = Image.open(file_path)
            
            # Preprocess image
            processed_image = self.preprocess_image_for_ocr(pil_image)
            
            # Use Tesseract for text extraction with timeout
            final_text = self.extract_text_with_tesseract(processed_image)
            ocr_method = "tesseract_pil"
            
            # Clean up
            del pil_image, processed_image
            gc.collect()
            
            logger.info("Image OCR extraction completed.")
            return final_text, ocr_method
            
        except Exception as e:
            logger.error(f"Image text extraction failed: {str(e)}")
            return f"Image text extraction failed: {str(e)}", "failed"

    def process_document(self, file_path: str) -> dict:
        """Enhanced document processing with automatic OCR detection using PIL only"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        logger.info(f"Processing file: {file_path}")
        logger.info(f"File extension: {file_extension}")
        
        # Check file size limits
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB total limit
        
        if file_size > max_size:
            logger.error(f"File too large: {file_size} bytes (max: {max_size})")
            return {
                'text': '',
                'is_scanned': False,
                'ocr_method': 'failed',
                'error': f'File too large: {file_size/1024/1024:.1f}MB (max: {max_size/1024/1024}MB)'
            }
        
        result = {
            'text': '',
            'is_scanned': False,
            'ocr_method': 'standard',
            'error': None
        }
        
        try:
            if file_extension == '.pdf':
                # First check if PDF is scanned or searchable
                if self.is_scanned_pdf(file_path):
                    logger.info("   Scanned PDF detected - Using OCR extraction...")
                    text, ocr_method = self.extract_text_with_ocr(file_path)
                    result.update({
                        'text': text,
                        'is_scanned': True,
                        'ocr_method': ocr_method
                    })
                else:
                    logger.info("   Searchable PDF detected - Using standard extraction...")
                    result['text'] = self.extract_text_from_pdf(file_path)
                    
            elif file_extension in ['.jpg', '.jpeg', '.png']:
                logger.info("   Image file detected - Using OCR extraction...")
                text, ocr_method = self.extract_text_from_image(file_path)
                result.update({
                    'text': text,
                    'is_scanned': True,
                    'ocr_method': ocr_method
                })
                
            elif file_extension == '.docx':
                logger.info("   Word document detected - Using standard extraction...")
                result['text'] = self.extract_text_from_docx(file_path)
                
            elif file_extension == '.txt':
                logger.info("   Text file detected - Using standard extraction...")
                result['text'] = self.extract_text_from_txt(file_path)
                
            else:
                result['error'] = f"   Unsupported file format: {file_extension}"
                
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            result['error'] = f"Document processing failed: {str(e)}"
        
        # Limit final text length
        if result['text'] and len(result['text']) > 100000:  # 100k character limit
            result['text'] = result['text'][:100000] + "... [Text truncated for processing]"
            logger.info("Text truncated to 100k characters for processing")
        
        return result