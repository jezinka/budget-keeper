import unittest
from decimal import Decimal
from datetime import datetime

from src.email_parser import (
    extract_amount,
    extract_all_amounts,
    extract_date,
    extract_all_dates,
    normalize_amount
)


class TestEmailParser(unittest.TestCase):
    
    def test_extract_amount_simple(self):
        """Test extracting simple amount with zł currency"""
        text = "Kwota: 82,87 zł"
        result = extract_amount(text)
        self.assertEqual(result, Decimal("82.87"))
    
    def test_extract_amount_with_pln(self):
        """Test extracting amount with PLN currency"""
        text = "Ile: 100,00 PLN"
        result = extract_amount(text)
        self.assertEqual(result, Decimal("100.00"))
    
    def test_extract_amount_with_spaces(self):
        """Test extracting amount with thousand separators"""
        text = "Kwota: 1 234,56 PLN"
        result = extract_amount(text)
        self.assertEqual(result, Decimal("1234.56"))
    
    def test_extract_amount_large(self):
        """Test extracting large amount"""
        text = "Na Twoje konto wpłynęło 9 999,98 PLN"
        result = extract_amount(text)
        self.assertEqual(result, Decimal("9999.98"))
    
    def test_extract_amount_not_found(self):
        """Test when no amount is found"""
        text = "No amount here"
        result = extract_amount(text)
        self.assertIsNone(result)
    
    def test_extract_all_amounts(self):
        """Test extracting multiple amounts from text"""
        text = "Wpłata: 100,00 zł. Saldo: 1 234,56 PLN"
        results = extract_all_amounts(text)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], Decimal("100.00"))
        self.assertEqual(results[1], Decimal("1234.56"))
    
    def test_extract_date_dot_format(self):
        """Test extracting date in dd.mm.yyyy format"""
        text = "Data: 11.11.2025"
        result = extract_date(text)
        self.assertEqual(result, datetime(2025, 11, 11))
    
    def test_extract_date_dash_format(self):
        """Test extracting date in dd-mm-yyyy format"""
        text = "Kiedy: 05-01-2023"
        result = extract_date(text)
        self.assertEqual(result, datetime(2023, 1, 5))
    
    def test_extract_date_single_digit(self):
        """Test extracting date with single digit day/month"""
        text = "Data: 5.1.2023"
        result = extract_date(text)
        self.assertEqual(result, datetime(2023, 1, 5))
    
    def test_extract_date_not_found(self):
        """Test when no date is found"""
        text = "No date here"
        result = extract_date(text)
        self.assertIsNone(result)
    
    def test_extract_date_invalid(self):
        """Test invalid date (e.g., 32.13.2023)"""
        text = "Data: 32.13.2023"
        result = extract_date(text)
        self.assertIsNone(result)
    
    def test_extract_all_dates(self):
        """Test extracting multiple dates from text"""
        text = "Kiedy: 11.11.2025 i 05-01-2023"
        results = extract_all_dates(text)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], datetime(2025, 11, 11))
        self.assertEqual(results[1], datetime(2023, 1, 5))
    
    def test_normalize_amount(self):
        """Test amount normalization"""
        amount = Decimal("82.8765")
        result = normalize_amount(amount)
        self.assertEqual(result, Decimal("82.88"))
    
    def test_extract_amount_from_real_email_blik(self):
        """Test extracting amount from real BLIK transaction email"""
        body = 'Stan Twojego konta zmniejszył się o 0,01 PLN. Szczegóły:Z konta:11 2222 3333 4444 5555 6666 7777 Ile:0,01 PLN Tytuł:Zakup BLIK Kiedy:03-01-2023'
        result = extract_amount(body)
        self.assertEqual(result, Decimal("0.01"))
    
    def test_extract_date_from_real_email_blik(self):
        """Test extracting date from real BLIK transaction email"""
        body = 'Stan Twojego konta zmniejszył się o 0,01 PLN. Szczegóły:Z konta:11 2222 3333 4444 5555 6666 7777 Ile:0,01 PLN Tytuł:Zakup BLIK Kiedy:03-01-2023'
        result = extract_date(body)
        self.assertEqual(result, datetime(2023, 1, 3))
    
    def test_extract_from_card_transaction(self):
        """Test extracting from card transaction email"""
        body = 'W związku z transakcją ZAKUPY na Twojej karcie debetowej zostało zablokowane -19,22 PLN. Szczegóły:Karta:Dopasowana Visa 1234 Ile:-19,22 PLN Kiedy:05-01-2023'
        amount = extract_amount(body)
        date = extract_date(body)
        self.assertEqual(amount, Decimal("19.22"))
        self.assertEqual(date, datetime(2023, 1, 5))


if __name__ == '__main__':
    unittest.main()
