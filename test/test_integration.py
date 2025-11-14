import unittest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime
from base64 import urlsafe_b64encode

import sys
sys.path.insert(0, '/home/runner/work/budget-keeper/budget-keeper/src')

from main import enrich_message_with_receipts
from message import Message


class TestIntegration(unittest.TestCase):
    """Integration tests for the enrichment flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.gmail_service = Mock()
    
    def test_enrich_message_with_receipts_success(self):
        """Test successful enrichment with receipt details"""
        # Mock the transaction message
        transaction_body = "Zakup BLIK. Ile: 82,87 PLN Kiedy: 11.11.2025"
        transaction_msg_data = {
            'id': 'trans123',
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': urlsafe_b64encode(transaction_body.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        # Mock the receipt message
        receipt_html = """
        <html>
        <body>
            <table>
                <tr><td>Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski</td><td>82,87 zł</td></tr>
            </table>
            <p>Data: 11.11.2025</p>
        </body>
        </html>
        """
        receipt_msg_data = {
            'id': 'receipt456',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': urlsafe_b64encode(receipt_html.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        # Set up Gmail service mock
        gmail_users = self.gmail_service.users.return_value
        gmail_messages = gmail_users.messages.return_value
        
        # Mock get() for transaction message
        gmail_messages.get.return_value.execute.return_value = transaction_msg_data
        
        # Mock list() to return receipt message
        gmail_messages.list.return_value.execute.return_value = {
            'messages': [{'id': 'receipt456'}]
        }
        
        # Set up side effect for get() to return different messages
        def get_side_effect(*args, **kwargs):
            msg_id = kwargs.get('id')
            mock_result = Mock()
            if msg_id == 'trans123':
                mock_result.execute.return_value = transaction_msg_data
            elif msg_id == 'receipt456':
                mock_result.execute.return_value = receipt_msg_data
            return mock_result
        
        gmail_messages.get.side_effect = get_side_effect
        
        # Create a mock message object
        mock_message = Mock()
        mock_message.get_title.return_value = "Zakup BLIK"
        
        # Call the enrichment function
        msg_ref = {'id': 'trans123'}
        enriched_data = enrich_message_with_receipts(
            self.gmail_service,
            msg_ref,
            mock_message
        )
        
        # Verify enrichment
        self.assertIsNotNone(enriched_data)
        self.assertIn('items', enriched_data)
        self.assertIn('receipt_ids', enriched_data)
        self.assertTrue(len(enriched_data['items']) > 0)
        self.assertIn('receipt456', enriched_data['receipt_ids'])
        
        # Check if product name is in items
        found_product = any('Prześcieradło' in item for item in enriched_data['items'])
        self.assertTrue(found_product, f"Expected product name in items: {enriched_data['items']}")
    
    def test_enrich_message_no_amount_or_date(self):
        """Test enrichment when amount or date cannot be extracted"""
        # Mock message without clear amount/date
        transaction_body = "Some text without proper amount or date"
        transaction_msg_data = {
            'id': 'trans999',
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': urlsafe_b64encode(transaction_body.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        # Set up Gmail service mock
        gmail_users = self.gmail_service.users.return_value
        gmail_messages = gmail_users.messages.return_value
        gmail_messages.get.return_value.execute.return_value = transaction_msg_data
        
        mock_message = Mock()
        msg_ref = {'id': 'trans999'}
        
        enriched_data = enrich_message_with_receipts(
            self.gmail_service,
            msg_ref,
            mock_message
        )
        
        # Should return None when amount/date cannot be extracted
        self.assertIsNone(enriched_data)
    
    def test_enrich_message_no_receipts_found(self):
        """Test enrichment when no matching receipts are found"""
        # Mock transaction message
        transaction_body = "Zakup BLIK. Ile: 999,99 PLN Kiedy: 01.01.2020"
        transaction_msg_data = {
            'id': 'trans888',
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': urlsafe_b64encode(transaction_body.encode('utf-8')).decode('utf-8')
                }
            }
        }
        
        # Set up Gmail service mock
        gmail_users = self.gmail_service.users.return_value
        gmail_messages = gmail_users.messages.return_value
        gmail_messages.get.return_value.execute.return_value = transaction_msg_data
        
        # Mock list() to return no messages
        gmail_messages.list.return_value.execute.return_value = {'messages': []}
        
        mock_message = Mock()
        msg_ref = {'id': 'trans888'}
        
        enriched_data = enrich_message_with_receipts(
            self.gmail_service,
            msg_ref,
            mock_message
        )
        
        # Should return None when no receipts found
        self.assertIsNone(enriched_data)


if __name__ == '__main__':
    unittest.main()
