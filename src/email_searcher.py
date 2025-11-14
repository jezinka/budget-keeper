import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional

from email_parser import extract_all_amounts, extract_all_dates, normalize_amount
from const import ME_ID


class EmailSearcher:
    
    def __init__(self, gmail_service, amount_tolerance: Decimal = Decimal('0.01')):
        self.service = gmail_service
        self.amount_tolerance = amount_tolerance
    
    def _get_message_content(self, message_id: str) -> Optional[Dict[str, Any]]:
        try:
            msg = self.service.users().messages().get(
                userId=ME_ID,
                id=message_id,
                format='full'
            ).execute()
            return msg
        except Exception as e:
            logging.error(f'Error fetching message {message_id}: {e}')
            return None
    
    def _matches_amount(self, message: Dict[str, Any], target_amount: Decimal) -> bool:
        # Extract body text from message
        body_text = self._extract_body_text(message)
        if not body_text:
            return False
        
        # Find all amounts in the message
        amounts = extract_all_amounts(body_text)
        
        # Normalize target amount
        normalized_target = normalize_amount(target_amount)
        
        # Check if any amount matches (within tolerance)
        for amount in amounts:
            normalized_amount = normalize_amount(amount)
            diff = abs(normalized_amount - normalized_target)
            if diff <= self.amount_tolerance:
                return True
        
        return False
    
    def _extract_body_text(self, message: Dict[str, Any]) -> str:
        payload = message.get('payload', {})
        
        # Try to get body data directly
        if 'body' in payload and 'data' in payload['body']:
            from base64 import urlsafe_b64decode
            body = urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'replace')
            return body
        
        # Try to get from parts (multipart message)
        if 'parts' in payload:
            return self._extract_from_parts(payload['parts'])
        
        return ''
    
    def _extract_from_parts(self, parts: List[Dict[str, Any]]) -> str:
        from base64 import urlsafe_b64decode
        text = ''
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            
            # Get body from this part
            if 'body' in part and 'data' in part['body']:
                try:
                    decoded = urlsafe_b64decode(part['body']['data']).decode('utf-8', 'replace')
                    text += decoded + '\n'
                except:
                    pass
            
            # Recursively process nested parts
            if 'parts' in part:
                text += self._extract_from_parts(part['parts'])
        
        return text
    
    def search_receipt_emails(
        self,
        target_date: datetime,
        target_amount: Decimal,
        days_range: int = 7
    ) -> List[Dict[str, Any]]:
        start_date = target_date - timedelta(days=days_range)
        end_date = target_date + timedelta(days=days_range)
        
        # Build date range query
        after_str = start_date.strftime('%Y/%m/%d')
        before_str = end_date.strftime('%Y/%m/%d')
        
        query = f'after:{after_str} before:{before_str}'
        
        try:
            result = self.service.users().messages().list(
                userId=ME_ID,
                q=query,
                maxResults=100  # Limit to avoid too many results
            ).execute()
            
            messages = result.get('messages', [])
            
            # Filter by amount
            matching_messages = []
            for msg_ref in messages:
                msg = self._get_message_content(msg_ref['id'])
                if msg and self._matches_amount(msg, target_amount):
                    matching_messages.append(msg)
            
            logging.info(f'Found {len(matching_messages)} receipt emails for amount {target_amount} in range {after_str} to {before_str}')
            return matching_messages
            
        except Exception as e:
            logging.error(f'Error searching receipt emails: {e}')
            return []
