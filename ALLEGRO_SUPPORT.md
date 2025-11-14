# Allegro Receipt Support

## Overview

The receipt extractor has been optimized for Allegro emails, which use JSON-LD structured data embedded in their HTML. This provides the most reliable method for extracting product information.

## How It Works

### 1. JSON-LD Structure

Allegro emails contain structured data in JSON-LD format (schema.org):

```json
{
  "@context": "http://schema.org",
  "@type": "Order",
  "seller": {...},
  "orderedItem": [
    {
      "@type": "OrderItem",
      "orderedItem": {
        "@type": "Product",
        "name": "Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski",
        "url": "https://allegro.pl/oferta/...",
        "image": "..."
      },
      "price": "82.87",
      "priceCurrency": "PLN"
    }
  ],
  "orderDate": "11.11.2025, 20:00"
}
```

### 2. Extraction Process

The `_extract_from_allegro_jsonld()` method:
1. Finds all `<script type="application/ld+json">` tags
2. Parses JSON content
3. Looks for `Order` objects
4. Extracts product names from `orderedItem.orderedItem.name`
5. Returns list of product names

### 3. Advantages

**Reliability**: JSON-LD provides structured, machine-readable data
- No need for HTML parsing heuristics
- No dependency on page layout changes
- Consistent field names and structure

**Accuracy**: Direct access to product information
- Full product name exactly as stored
- No text extraction errors
- No false positives from other page elements

**Performance**: Fast parsing
- Single JSON parse operation
- No DOM traversal needed
- Minimal processing overhead

## Example Usage

### Input: Allegro Receipt Email
```
From: powiadomienia@allegro.pl
Subject: Kupiłaś i zapłaciłaś: Prześcieradło z gumką...
Date: 11.11.2025
```

### Extracted Data
```python
items = extractor.extract_items_from_message(allegro_message)
# Returns: ["Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski"]
```

### Enriched Transaction
```json
{
  "title": "Zakup BLIK",
  "amount": -82.87,
  "transactionDate": "2025-11-11 00:00:00",
  "items": ["Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski"],
  "receiptIds": ["msg_allegro_id"]
}
```

## Multiple Products

The extractor handles orders with multiple products:

```python
# Order with 2 products
items = [
  "Prześcieradło z gumką 220x200 gruba satyna",
  "Poduszka puchowa 50x70 antyalergiczna"
]
```

## Fallback Strategy

If Allegro JSON-LD is not found (e.g., for non-Allegro receipts), the system falls back to:
1. HTML table parsing
2. HTML paragraph/list parsing
3. Plain text extraction

This ensures compatibility with other receipt formats while prioritizing Allegro's reliable structured data.

## Testing

See `test/test_allegro_extractor.py` for test cases:
- JSON-LD parsing validation
- Multiple product handling
- Real Allegro email verification

Run tests:
```bash
python -m unittest test.test_allegro_extractor -v
```

## Email Format Requirements

The extractor expects:
- Email contains `<script type="application/ld+json">` tag
- JSON-LD contains `@type: "Order"`
- Order has `orderedItem` array
- Each item has `orderedItem.orderedItem.name` with product name

These are standard in Allegro transaction notification emails.
