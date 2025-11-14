import unittest
from base64 import urlsafe_b64encode

from src.receipt_extractor import ReceiptExtractor


class TestReceiptExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = ReceiptExtractor()
    
    def test_extract_from_html_table(self):
        """Test extracting items from HTML table"""
        html = """
        <html>
        <body>
            <table>
                <tr><th>Nazwa produktu</th><th>Cena</th></tr>
                <tr><td>Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski</td><td>82,87 zł</td></tr>
            </table>
        </body>
        </html>
        """
        
        message = {
            'id': 'test123',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(html.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        items = self.extractor.extract_items_from_message(message)
        self.assertTrue(len(items) > 0)
        # Check if the product name is in any of the extracted items
        found = any('Prześcieradło' in item for item in items)
        self.assertTrue(found, f"Expected to find product name in items: {items}")
    
    def test_extract_from_text(self):
        """Test extracting items from plain text"""
        text = """
        Szczegóły zamówienia:
        
        Produkt: Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski
        Cena: 82,87 zł
        Data: 11.11.2025
        """
        
        message = {
            'id': 'test456',
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': urlsafe_b64encode(text.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        items = self.extractor.extract_items_from_message(message)
        self.assertTrue(len(items) > 0)
        # Check if the product name is in the extracted items
        found = any('Prześcieradło' in item for item in items)
        self.assertTrue(found, f"Expected to find product name in items: {items}")
    
    def test_extract_multiple_items(self):
        """Test extracting multiple items from one message"""
        html = """
        <html>
        <body>
            <ul>
                <li>Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski - 82,87 zł</li>
                <li>Poduszka puchowa 50x70 antyalergiczna biała - 45,99 zł</li>
                <li>Kołdra zimowa 200x220 puch naturalny - 199,00 zł</li>
            </ul>
        </body>
        </html>
        """
        
        message = {
            'id': 'test789',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(html.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        items = self.extractor.extract_items_from_message(message)
        self.assertTrue(len(items) >= 3)
    
    def test_is_just_numbers(self):
        """Test number detection helper"""
        self.assertTrue(self.extractor._is_just_numbers("123.45"))
        self.assertTrue(self.extractor._is_just_numbers("11.11.2025"))
        self.assertTrue(self.extractor._is_just_numbers("82,87 zł"))
        self.assertFalse(self.extractor._is_just_numbers("Prześcieradło z gumką 220x200"))
        self.assertFalse(self.extractor._is_just_numbers("Product name with 123 numbers"))
    
    def test_extract_from_multipart_message(self):
        """Test extracting from multipart message with both HTML and text"""
        html = "<html><body><p>Produkt: Testowy produkt z długą nazwą opisową</p></body></html>"
        
        message = {
            'id': 'test_multi',
            'payload': {
                'mimeType': 'multipart/alternative',
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': urlsafe_b64encode(b'Plain text version').decode('utf-8')
                        }
                    },
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': urlsafe_b64encode(html.encode('utf-8')).decode('utf-8')
                        }
                    }
                ]
            }
        }
        
        items = self.extractor.extract_items_from_message(message)
        # Should extract from HTML (preferred)
        self.assertTrue(len(items) > 0)
    
    def test_extract_from_multiple_messages(self):
        """Test extracting from multiple messages"""
        html1 = "<html><body><p>Produkt pierwszy z długą nazwą opisową</p></body></html>"
        html2 = "<html><body><p>Produkt drugi z inną długą nazwą</p></body></html>"
        
        message1 = {
            'id': 'msg1',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(html1.encode('utf-8')).decode('utf-8')
                }
            }
        }
        message2 = {
            'id': 'msg2',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(html2.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        items1 = self.extractor.extract_items_from_message(message1)
        items2 = self.extractor.extract_items_from_message(message2)
        
        self.assertTrue(len(items1) > 0)
        self.assertTrue(len(items2) > 0)


if __name__ == '__main__':
    unittest.main()
