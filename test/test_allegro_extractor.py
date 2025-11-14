import unittest
from base64 import urlsafe_b64encode
import quopri
import sys
sys.path.insert(0, '/home/runner/work/budget-keeper/budget-keeper/src')

from receipt_extractor import ReceiptExtractor


class TestAllegroExtractor(unittest.TestCase):
    """Test extraction from real Allegro email"""
    
    def setUp(self):
        self.extractor = ReceiptExtractor()
    
    def test_extract_from_allegro_jsonld(self):
        """Test extracting product from Allegro email with JSON-LD"""
        # Simplified Allegro-style JSON-LD structure
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="application/ld+json">
            [
              {
                "@context": "http://schema.org",
                "@type": "Order",
                "seller": {
                  "@type": "Organization",
                  "name": "Seller Name"
                },
                "orderedItem": [
                  {
                    "@type": "OrderItem",
                    "orderedItem": {
                      "@type": "Product",
                      "name": "Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski",
                      "url": "https://allegro.pl/oferta/...",
                      "image": "https://a.allegroimg.com/..."
                    },
                    "price": "82.87",
                    "priceCurrency": "PLN"
                  }
                ],
                "orderDate": "11.11.2025, 20:00"
              }
            ]
            </script>
        </head>
        <body>
            <p>Some other text</p>
        </body>
        </html>
        """
        
        message = {
            'id': 'allegro_test',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(html.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        items = self.extractor.extract_items_from_message(message)
        
        # Should extract the product name from JSON-LD
        self.assertEqual(len(items), 1)
        self.assertIn('Prześcieradło', items[0])
        self.assertIn('granat niebieski', items[0])
    
    def test_extract_from_real_allegro_email(self):
        """Test with actual Allegro email structure"""
        # Read the actual email file if it exists
        try:
            with open('/tmp/INBOX_69071.html', 'rb') as f:
                email_content = f.read()
            
            # Decode quoted-printable
            decoded = quopri.decodestring(email_content).decode('utf-8', errors='replace')
            
            # Extract the HTML body (after headers)
            html_start = decoded.find('<!DOCTYPE')
            if html_start > 0:
                html_body = decoded[html_start:]
            else:
                html_body = decoded
            
            message = {
                'id': 'real_allegro',
                'payload': {
                    'mimeType': 'text/html',
                    'body': {
                        'data': urlsafe_b64encode(html_body.encode('utf-8')).decode('utf-8')
                    }
                }
            }
            
            items = self.extractor.extract_items_from_message(message)
            
            # Should extract the product name
            self.assertTrue(len(items) > 0, "Should extract at least one item")
            
            # Check if product name is in the results
            found_product = False
            for item in items:
                if 'Prześcieradło' in item and 'granat' in item:
                    found_product = True
                    break
            
            self.assertTrue(found_product, f"Should find the bedsheet product. Found items: {items}")
            
        except FileNotFoundError:
            self.skipTest("Real Allegro email file not available")
    
    def test_allegro_multiple_products(self):
        """Test extracting multiple products from Allegro order"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Order",
                "orderedItem": [
                  {
                    "@type": "OrderItem",
                    "orderedItem": {
                      "@type": "Product",
                      "name": "Prześcieradło z gumką 220x200 gruba satyna"
                    },
                    "price": "82.87"
                  },
                  {
                    "@type": "OrderItem",
                    "orderedItem": {
                      "@type": "Product",
                      "name": "Poduszka puchowa 50x70 antyalergiczna"
                    },
                    "price": "45.99"
                  }
                ]
              }
            </script>
        </head>
        <body></body>
        </html>
        """
        
        message = {
            'id': 'multi_test',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(html.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        items = self.extractor.extract_items_from_message(message)
        
        # Should extract both products
        self.assertEqual(len(items), 2)
        self.assertTrue(any('Prześcieradło' in item for item in items))
        self.assertTrue(any('Poduszka' in item for item in items))


if __name__ == '__main__':
    unittest.main()
