import re
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


def extract_amount(text: str) -> Optional[Decimal]:
    # Pattern for Polish currency format with spaces as thousands separator
    # Handles: "82,87 zł", "1 234,56 PLN", "100,00 zł"
    pattern = r'(\d{1,3}(?:[\s\u00A0]\d{3})*(?:[.,]\d{2})?)[\s\u00A0]*(zł|PLN)?'
    
    matches = re.findall(pattern, text)
    if not matches:
        return None
    
    # Take the first match, process the amount part
    amount_str = matches[0][0] if isinstance(matches[0], tuple) else matches[0]
    
    # Remove spaces and non-breaking spaces
    amount_str = amount_str.replace(' ', '').replace('\u00A0', '')
    # Replace comma with dot for Decimal
    amount_str = amount_str.replace(',', '.')
    
    try:
        return Decimal(amount_str)
    except:
        return None


def extract_all_amounts(text: str) -> List[Decimal]:
    # Pattern for Polish currency format
    pattern = r'(\d{1,3}(?:[\s\u00A0]\d{3})*(?:[.,]\d{2})?)[\s\u00A0]*(zł|PLN)?'
    
    matches = re.findall(pattern, text)
    amounts = []
    
    for match in matches:
        amount_str = match[0] if isinstance(match, tuple) else match
        # Remove spaces and non-breaking spaces
        amount_str = amount_str.replace(' ', '').replace('\u00A0', '')
        # Replace comma with dot for Decimal
        amount_str = amount_str.replace(',', '.')
        
        try:
            amounts.append(Decimal(amount_str))
        except:
            continue
    
    return amounts


def extract_date(text: str) -> Optional[datetime]:
    # Pattern for dd.mm.yyyy format
    pattern_dot = r'(\d{1,2})\.(\d{1,2})\.(\d{4})'
    match = re.search(pattern_dot, text)
    
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass
    
    # Pattern for dd-mm-yyyy format (alternative)
    pattern_dash = r'(\d{1,2})-(\d{1,2})-(\d{4})'
    match = re.search(pattern_dash, text)
    
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass
    
    return None


def extract_all_dates(text: str) -> List[datetime]:
    dates = []
    
    # Pattern for dd.mm.yyyy format
    pattern_dot = r'(\d{1,2})\.(\d{1,2})\.(\d{4})'
    for match in re.finditer(pattern_dot, text):
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            dates.append(datetime(year, month, day))
        except ValueError:
            continue
    
    # Pattern for dd-mm-yyyy format
    pattern_dash = r'(\d{1,2})-(\d{1,2})-(\d{4})'
    for match in re.finditer(pattern_dash, text):
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            dates.append(datetime(year, month, day))
        except ValueError:
            continue
    
    return dates


def normalize_amount(amount: Decimal, tolerance: Decimal = Decimal('0.01')) -> Decimal:
    return amount.quantize(Decimal('0.01'))
