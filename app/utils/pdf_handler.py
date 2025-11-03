"""
PDF processing utilities
"""
import io
import logging
from typing import Optional, List

from PyPDF2 import PdfReader

# Optional OCR dependencies
try:
    import pytesseract
    from PIL import Image
    import pypdfium2 as pdfium
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class PDFHandler:
    """Handles PDF file operations"""
    
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> Optional[str]:
        """
        Extract text content from PDF bytes.
        Falls back to OCR per-page if a page has no embedded text.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            # Create PDF reader from bytes
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages; OCR empty pages if possible
            text_parts: List[str] = []
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""

                if not page_text and OCR_AVAILABLE:
                    try:
                        # Render page to image with pdfium and OCR via Tesseract
                        pdf = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
                        page_handle = pdf.get_page(page_num)
                        bitmap = page_handle.render(scale=2.0, rotation=0)
                        img = Image.frombytes(
                            "RGBA",
                            (bitmap.width, bitmap.height),
                            bitmap.to_bytes(),
                        ).convert("RGB")
                        ocr_text = pytesseract.image_to_string(img)
                        page_text = ocr_text or ""
                    except Exception as ocr_err:
                        logger.warning(f"⚠️  OCR failed on page {page_num + 1}: {ocr_err}")

                if page_text:
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"✅ Extracted {len(full_text)} characters from PDF")
            
            return full_text if full_text.strip() else None
            
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {e}")
            return None
    
    @staticmethod
    def get_pdf_metadata(pdf_bytes: bytes) -> dict:
        """
        Extract metadata from PDF
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            metadata = {
                "num_pages": len(reader.pages),
                "metadata": reader.metadata if reader.metadata else {}
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ PDF metadata extraction error: {e}")
            return {"num_pages": 0, "metadata": {}}