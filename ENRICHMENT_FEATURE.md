# Email Enrichment Feature

## Overview

This feature enhances the budget-keeper application by automatically enriching transaction emails with detailed receipt information. When a transaction email is processed (e.g., a BLIK payment), the system searches for matching receipt emails that contain item-level details.

## How It Works

### 1. Transaction Processing
When a bank transaction email is fetched from Gmail:
- The system extracts the **amount** (e.g., "82,87 zł") and **date** (e.g., "11.11.2025") from the transaction email
- These values are normalized for accurate matching

### 2. Receipt Search
The system searches Gmail for receipt emails that:
- Were sent within ±7 days of the transaction date
- Contain the same amount as the transaction
- Uses Gmail API search with date range filtering, then validates amount match

### 3. Item Extraction
For matching receipt emails, the system extracts:
- Product names and descriptions
- Uses HTML parsing (BeautifulSoup) as the primary method
- Falls back to text parsing for plain-text emails
- Example extracted item: "Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski"

### 4. Data Enrichment
The enriched data is sent to RabbitMQ with the expense message:
```json
{
  "title": "Zakup BLIK",
  "payee": "",
  "amount": -82.87,
  "transactionDate": "2025-11-11 00:00:00",
  "sendDate": "2025-11-14 16:45:00",
  "items": [
    "Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski"
  ],
  "receiptIds": ["receipt_gmail_id_123"]
}
```

## New Modules

### `src/email_parser.py`
Extracts amounts and dates from email content:
- `extract_amount(text)` - Parses Polish currency format (handles spaces, commas, "zł", "PLN")
- `extract_date(text)` - Parses dates in dd.mm.yyyy or dd-mm-yyyy format
- `normalize_amount(amount)` - Normalizes amounts for comparison

### `src/email_searcher.py`
Searches for emails by date and amount:
- `EmailSearcher.search_by_date_and_amount()` - Exact date + amount search
- `EmailSearcher.search_receipt_emails()` - Search with date range (±7 days)
- Configurable amount tolerance (default: ±0.01)

### `src/receipt_extractor.py`
Extracts item details from receipt emails:
- `ReceiptExtractor.extract_items_from_message()` - Main extraction method
- Supports HTML parsing (tables, lists, paragraphs)
- Fallback to plain text parsing
- Filters out numeric-only data (prices, dates)

### Updated Modules

#### `src/main.py`
- Added `enrich_message_with_receipts()` function
- Integrated enrichment into `process_messages()` flow
- Logs enrichment success with item count

#### `src/rabbitMQ_communication.py`
- Updated `send_expense_to_rabbitmq()` to accept optional `enriched_data` parameter
- Includes `items` and `receiptIds` fields in message when available

## Configuration

### Amount Tolerance
By default, amounts must match within ±0.01. This can be adjusted when creating `EmailSearcher`:
```python
searcher = EmailSearcher(gmail_service, amount_tolerance=Decimal('0.50'))
```

### Date Range
Receipt search looks ±7 days from transaction date by default. This can be adjusted:
```python
receipt_messages = searcher.search_receipt_emails(date, amount, days_range=14)
```

## Testing

The feature includes comprehensive test coverage:
- **16 tests** for email parser (amount/date extraction)
- **6 tests** for receipt extractor (HTML/text parsing)
- **3 integration tests** (end-to-end enrichment flow)

Run tests:
```bash
PYTHONPATH=/home/runner/work/budget-keeper/budget-keeper/src python -m unittest test.test_email_parser test.test_receipt_extractor test.test_integration -v
```

## Example Use Case

### Scenario: BLIK Transaction
1. **Transaction Email Received:**
   - Subject: "Zakup BLIK"
   - Body: "Stan Twojego konta zmniejszył się o 82,87 PLN. Ile: 82,87 PLN Kiedy: 11.11.2025"

2. **System Processing:**
   - Extracts amount: 82.87 PLN
   - Extracts date: 11.11.2025
   - Searches Gmail for emails with matching amount between 04.11.2025 and 18.11.2025

3. **Receipt Found:**
   - From: shop@example.com
   - Contains HTML table with product: "Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski"
   - Amount: 82,87 zł

4. **Enriched Message Sent:**
   - Original transaction data + item description + receipt ID
   - Spring/React app can now display detailed expense information

## Benefits

1. **Automatic Detail Capture**: No manual entry of purchase details
2. **Better Expense Tracking**: Know exactly what was purchased, not just "BLIK payment"
3. **Receipt Linking**: Track which receipts correspond to which transactions
4. **Historical Analysis**: Detailed item-level spending patterns

## Error Handling

The enrichment process is non-blocking:
- If amount/date extraction fails → transaction still processed without enrichment
- If no receipts found → transaction processed without items
- If receipt parsing fails → transaction processed without items
- All errors logged for debugging

## Logging

The feature adds logging at key points:
- Amount/date extraction results
- Receipt search results (count of matches)
- Item extraction results (count per receipt)
- Enrichment success/failure with item count

Example log:
```
INFO: Extracted amount 82.87 and date 2025-11-11 from message msg_123
INFO: Found 1 receipt emails for amount 82.87 in range 2025-11-04 to 2025-11-18
INFO: Extracted 1 items from receipt receipt_456
INFO: message msg_123: Zakup BLIK: 82,87: saved successfully (enriched with 1 items)
```
