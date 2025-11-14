import json
import logging
import re
from base64 import urlsafe_b64decode
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup


class ReceiptExtractor:
    
    def extract_items_from_message(self, message: Dict[str, Any]) -> List[str]:
        payload = message.get('payload', {})
        
        # Try HTML parsing first (more structured)
        html_body = self._get_html_body(payload)
        if html_body:
            items = self._extract_from_html(html_body)
            if items:
                logging.info(f'Extracted {len(items)} items from HTML')
                return items
        
        # Fallback to plain text parsing
        text_body = self._get_text_body(payload)
        if text_body:
            items = self._extract_from_text(text_body)
            logging.info(f'Extracted {len(items)} items from text')
            return items
        
        return []
    
    def _get_html_body(self, payload: Dict[str, Any]) -> Optional[str]:
        # Check if body is directly in payload
        if 'body' in payload and 'data' in payload['body']:
            mime_type = payload.get('mimeType', '')
            if 'html' in mime_type.lower():
                return urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'replace')
        
        # Check parts for HTML content
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if 'html' in mime_type.lower() and 'body' in part and 'data' in part['body']:
                    return urlsafe_b64decode(part['body']['data']).decode('utf-8', 'replace')
                
                # Recursively check nested parts
                if 'parts' in part:
                    html = self._get_html_body(part)
                    if html:
                        return html
        
        return None
    
    def _get_text_body(self, payload: Dict[str, Any]) -> Optional[str]:
        # Check if body is directly in payload
        if 'body' in payload and 'data' in payload['body']:
            mime_type = payload.get('mimeType', '')
            if 'text/plain' in mime_type.lower() or 'text' in mime_type.lower():
                return urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'replace')
        
        # Check parts for text content
        if 'parts' in payload:
            text_parts = []
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if 'text/plain' in mime_type.lower() and 'body' in part and 'data' in part['body']:
                    text_parts.append(urlsafe_b64decode(part['body']['data']).decode('utf-8', 'replace'))
                
                # Recursively check nested parts
                if 'parts' in part:
                    text = self._get_text_body(part)
                    if text:
                        text_parts.append(text)
            
            if text_parts:
                return '\n'.join(text_parts)
        
        return None
    
    def _extract_from_html(self, html_body: str) -> List[str]:
        items = []
        
        try:
            soup = BeautifulSoup(html_body, 'html.parser')
            
            # Strategy 1: Extract from Allegro JSON-LD structured data (most reliable)
            allegro_items = self._extract_from_allegro_jsonld(soup)
            if allegro_items:
                logging.info(f'Extracted {len(allegro_items)} items from Allegro JSON-LD')
                return allegro_items
            
            # Strategy 2: Look for table rows with product information
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        # Look for product-like descriptions (longer text, not just numbers)
                        if len(text) > 15 and not self._is_just_numbers(text):
                            items.append(text)
            
            # Strategy 3: Look for paragraphs with product-like content
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Look for text that mentions product or contains descriptive content
                if len(text) > 15 and not self._is_just_numbers(text):
                    # Check if contains product keywords or looks descriptive
                    if any(kw in text.lower() for kw in ['produkt', 'nazwa', 'towar', 'artykuł']):
                        items.append(text)
                    elif re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}.*[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}', text):
                        # Has multiple words (descriptive)
                        items.append(text)
            
            # Strategy 4: Look for list items
            list_items = soup.find_all('li')
            for li in list_items:
                text = li.get_text(strip=True)
                if len(text) > 15 and not self._is_just_numbers(text):
                    items.append(text)
            
        except Exception as e:
            logging.error(f'Error parsing HTML: {e}')
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(items))
    
    def _extract_from_allegro_jsonld(self, soup: BeautifulSoup) -> List[str]:
        items = []
        
        try:
            # Find all script tags with type="application/ld+json"
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_ld_scripts:
                if not script.string:
                    continue
                
                try:
                    # Parse the JSON-LD content
                    data = json.loads(script.string)
                    
                    # Handle both single object and array
                    items_to_check = data if isinstance(data, list) else [data]
                    
                    for item in items_to_check:
                        # Look for Order objects with orderedItem
                        if item.get('@type') == 'Order' and 'orderedItem' in item:
                            ordered_items = item['orderedItem']
                            if not isinstance(ordered_items, list):
                                ordered_items = [ordered_items]
                            
                            for ordered_item in ordered_items:
                                # Extract product name from orderedItem
                                if 'orderedItem' in ordered_item:
                                    product = ordered_item['orderedItem']
                                    if isinstance(product, dict) and 'name' in product:
                                        product_name = product['name']
                                        if product_name and len(product_name) > 10:
                                            items.append(product_name)
                                            logging.debug(f'Found Allegro product: {product_name}')
                
                except json.JSONDecodeError as e:
                    logging.debug(f'Failed to parse JSON-LD: {e}')
                    continue
        
        except Exception as e:
            logging.error(f'Error extracting Allegro JSON-LD: {e}')
        
        return items
    
    def _extract_from_text(self, text_body: str) -> List[str]:
        items = []
        
        # Split into lines
        lines = text_body.split('\n')
        
        # Look for lines that appear to be product descriptions
        product_keywords = ['produkt', 'nazwa', 'towar', 'artykuł', 'szczegóły', 'opis']
        
        found_product_section = False
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're in a product section
            if any(keyword in line_lower for keyword in product_keywords):
                found_product_section = True
                # Look at the next few lines for actual product info
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if len(next_line) > 20 and not self._is_just_numbers(next_line):
                        items.append(next_line)
                        break
            
            # Also look for long descriptive lines (likely product names)
            elif len(line.strip()) > 30 and not self._is_just_numbers(line):
                # Check if it looks like a product description
                # (contains letters and possibly numbers, not just metadata)
                if re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}', line):
                    items.append(line.strip())
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(items))
    
    def _is_just_numbers(self, text: str) -> bool:
        # Remove common numeric patterns
        cleaned = re.sub(r'[\d.,\s€$£¥zł\-:/]+', '', text)
        # If very little remains, it's probably just numbers
        return len(cleaned) < 5
    

