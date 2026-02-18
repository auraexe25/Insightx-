"""
OCR using EasyOCR - No external installation required
"""

import easyocr
import cv2
import numpy as np
from PIL import Image
import argparse
import os


class EasyOCRModel:
    """OCR Model using EasyOCR."""
    
    def __init__(self, languages: list = ['en'], gpu: bool = False):
        """
        Initialize EasyOCR reader.
        
        Args:
            languages: List of language codes (e.g., ['en'], ['en', 'hi'])
            gpu: Whether to use GPU acceleration
        """
        print("Loading OCR model (first run downloads models)...")
        self.reader = easyocr.Reader(languages, gpu=gpu)
        print("Model loaded!")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR - handles rotation and enhances contrast.
        """
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Auto-rotate based on text orientation detection
        img_rotated = self._auto_rotate(gray)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img_rotated)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        return denoised
    
    def _auto_rotate(self, image: np.ndarray) -> np.ndarray:
        """Auto-rotate image to correct text orientation."""
        # Try multiple rotation angles and pick best
        best_angle = 0
        best_conf = 0
        
        for angle in [0, 90, 180, 270, -45, 45, -90]:
            rotated = self._rotate_image(image, angle)
            # Quick test with reader
            try:
                results = self.reader.readtext(rotated, detail=1)
                if results:
                    avg_conf = np.mean([r[2] for r in results])
                    if avg_conf > best_conf:
                        best_conf = avg_conf
                        best_angle = angle
            except:
                pass
        
        return self._rotate_image(image, best_angle)
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle."""
        if angle == 0:
            return image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new bounding box
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        return cv2.warpAffine(image, M, (new_w, new_h), 
                              borderMode=cv2.BORDER_REPLICATE)
    
    def extract_text(self, image_path: str, detail: int = 0, preprocess: bool = False) -> str:
        """
        Extract text from an image.
        
        Args:
            image_path: Path to image file
            detail: 0 for text only, 1 for detailed results
            preprocess: Apply preprocessing (rotation, contrast enhancement)
            
        Returns:
            Extracted text
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if preprocess:
            image = self.preprocess_image(image_path)
            results = self.reader.readtext(image, detail=detail)
        else:
            results = self.reader.readtext(image_path, detail=detail)
        
        if detail == 0:
            return '\n'.join(results)
        return results
    
    def extract_text_with_details(self, image_path: str, preprocess: bool = False) -> dict:
        """
        Extract text with bounding boxes and confidence.
        
        Returns:
            Dictionary with text, boxes, and confidence scores
        """
        if preprocess:
            image = self.preprocess_image(image_path)
            results = self.reader.readtext(image)
        else:
            results = self.reader.readtext(image_path)
        
        output = {
            'text': [],
            'boxes': [],
            'confidence': []
        }
        
        for (bbox, text, conf) in results:
            output['text'].append(text)
            output['boxes'].append(bbox)
            output['confidence'].append(conf)
        
        output['full_text'] = ' '.join(output['text'])
        return output


def main():
    parser = argparse.ArgumentParser(description='OCR using EasyOCR')
    parser.add_argument('image_path', help='Path to image file')
    parser.add_argument('--lang', nargs='+', default=['en'], 
                        help='Languages (e.g., --lang en hi)')
    parser.add_argument('--detailed', action='store_true',
                        help='Show detailed output')
    parser.add_argument('--gpu', action='store_true', help='Use GPU')
    parser.add_argument('--preprocess', action='store_true',
                        help='Apply preprocessing (rotation fix, contrast enhancement)')
    
    args = parser.parse_args()
    
    ocr = EasyOCRModel(languages=args.lang, gpu=args.gpu)
    
    if args.detailed:
        results = ocr.extract_text_with_details(args.image_path, preprocess=args.preprocess)
        print("\n=== OCR Results ===")
        print(f"Full Text: {results['full_text']}")
        print(f"\nWord count: {len(results['text'])}")
        if results['confidence']:
            print(f"Average confidence: {np.mean(results['confidence']):.2%}")
        print("\n--- Details ---")
        for text, conf in zip(results['text'], results['confidence']):
            print(f"  [{conf:.2%}] {text}")
    else:
        text = ocr.extract_text(args.image_path, preprocess=args.preprocess)
        print("\n=== Extracted Text ===")
        print(text)


if __name__ == '__main__':
    main()
