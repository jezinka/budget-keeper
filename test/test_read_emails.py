import unittest

from src.read_emails import prepare_message_dict, parse_purchase_info, parse_donation


class TestReadMails(unittest.TestCase):

    def test_prepare_message_dict_empty(self):
        with self.assertRaises(AttributeError):
            prepare_message_dict('', True)

    def test_prepare_message_dict_card_expense(self):
        body = 'W związku z transakcją ZAKUPY na Twojej karcie debetowej zostało zablokowane -19,22 PLN. Szczegóły:Karta:Dopasowana Visa 1234 Ile:-19,22 PLN Kiedy:05-01-2023 Gdzie:JMP S.A. BIEDRONKA 1244 WROCLAWTel'
        self.assertDictEqual(prepare_message_dict(body, False),
                             {'kwota': '19,22', 'kiedy': '05-01-2023', 'tytul': 'JMP S.A. BIEDRONKA 1244 WROCLAW'})

    def test_prepare_message_dict_income(self):
        body = 'Na Twoje konto wpłynęło 9 999,98 PLN od PAULINA P.Szczegóły przelewu:Tytuł:Przelew własnyNadawca:PAULINA PKwota:9 999,98 PLNNa konto:11 2222 3333 4444 5555 6666 7777 Stan konta po przelewie:Saldo:9 999,99 PLN Tel'
        self.assertDictEqual(prepare_message_dict(body, True),
                             {'tytul': 'Przelew własny', 'kto': 'PAULINA P', 'kwota': '9 999,98'})

    def test_prepare_message_dict_atm_income(self):
        body = "Wpłata we wpłatomacie 100,00 PLN. Na Twoje konto wpłynęło 100,00 PLN.Szczegóły:Ile:100,00 PLN Kiedy:17-10-2022 Karta:Dopasowana Visa 1234 Gdzie:ATMTel"

        self.assertDictEqual(prepare_message_dict(body, True),
                             {'kwota': '100,00', 'kiedy': '17-10-2022', 'tytul': 'ATM'})

    def test_prepare_message_dict_expense(self):
        body = 'Stan Twojego konta zmniejszył się o 0,01 PLN. Szczegóły:Z konta:11 2222 3333 4444 5555 6666 7777 Ile:0,01 PLN Tytuł:Zakup BLIK Kiedy:03-01-2023 Data księgowania:03-01-2023Saldo po operacji: Saldo:0,02 PLN Tel'
        self.assertDictEqual(prepare_message_dict(body, False),
                             {'kto': None, 'kwota': '0,01',
                              'tytul': 'Zakup BLIK',
                              'kiedy': '03-01-2023'})

    def test_prepare_message_dict_atm_expense(self):
        body = 'Stan Twojego konta zmniejszył się o -50,00 PLN. Szczegóły:Ile:-0,01 PLN Kiedy:19-09-2022 Karta:Dopasowana Visa 1234 Gdzie:ATMTel'
        self.assertDictEqual(prepare_message_dict(body, False),
                             {'kwota': '0,01', 'kiedy': '19-09-2022', 'tytul': 'ATM'})


class TestParsePurchaseInfo(unittest.TestCase):
    SAMPLE_JSONLD = [[{
        '@context': 'http://schema.org',
        '@type': 'Order',
        'price': '82.87',
        'priceCurrency': 'PLN',
        'acceptedOffer': [
            {
                '@type': 'Offer',
                'itemOffered': {
                    '@type': 'Product',
                    'name': 'Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski'
                },
                'price': '82.87'
            }
        ],
        'orderDate': '11.11.2025, 20:00'
    }]]

    def test_parse_purchase_info_single_item(self):
        result = parse_purchase_info(self.SAMPLE_JSONLD)
        self.assertEqual(result['price'], '82.87')
        self.assertEqual(result['name'], 'Prześcieradło z gumką 220x200 gruba satyna, bawełna 100% granat niebieski')
        self.assertEqual(result['orderDate'], '11.11.2025, 20:00')

    def test_parse_purchase_info_blik_overrides_order_price(self):
        """When BLIK payment (after discount) differs from order total, BLIK amount is used."""
        html_body = '<html><body>Gravitrax 228,99 zł ... Płatność 128,99 zł przekazana Metoda płatności BLIK</body></html>'
        result = parse_purchase_info(self.SAMPLE_JSONLD, html_body)
        self.assertEqual(result['price'], '128.99')

    def test_parse_purchase_info_fallback_to_jsonld_price(self):
        """When no BLIK payment text found, falls back to ld+json price."""
        result = parse_purchase_info(self.SAMPLE_JSONLD, '<html><body>no payment text</body></html>')
        self.assertEqual(result['price'], '82.87')

    def test_parse_purchase_info_multiple_items(self):
        jsonld = [[{
            '@type': 'Order',
            'price': '50.00',
            'acceptedOffer': [
                {'itemOffered': {'name': 'Produkt A'}},
                {'itemOffered': {'name': 'Produkt B'}},
            ],
            'orderDate': '01.01.2025, 10:00'
        }]]
        result = parse_purchase_info(jsonld)
        self.assertEqual(result['name'], 'Produkt A, Produkt B')

    def test_parse_purchase_info_no_order_raises(self):
        with self.assertRaises(ValueError):
            parse_purchase_info([[{'@type': 'Person', 'name': 'Jan'}]])


class TestParseSiepomaga(unittest.TestCase):
    HEADERS_FDDS = [
        {'name': 'Subject',
         'value': 'Twoja comiesięczna darowizna 100 zł została przekazana - Fundacja Dajemy Dzieciom Siłę'},
        {'name': 'Date', 'value': 'Thu, 26 Mar 2026 07:00:46 +0100'},
    ]

    HEADERS_WOSP = [
        {'name': 'Subject',
         'value': 'Twoja comiesięczna darowizna 100 zł została przekazana - Wielka Orkiestra Świątecznej Pomocy'},
        {'name': 'Date', 'value': 'Thu, 26 Mar 2026 07:00:45 +0100'},
    ]

    def test_parse_fdds_amount(self):
        result = parse_donation(self.HEADERS_FDDS)
        self.assertEqual(result['price'], '100')

    def test_parse_fdds_name(self):
        result = parse_donation(self.HEADERS_FDDS)
        self.assertEqual(result['name'], 'Fundacja Dajemy Dzieciom Siłę')

    def test_parse_fdds_date(self):
        result = parse_donation(self.HEADERS_FDDS)
        self.assertEqual(result['orderDate'], '26.03.2026, 07:00')

    def test_parse_wosp_name(self):
        result = parse_donation(self.HEADERS_WOSP)
        self.assertEqual(result['name'], 'Wielka Orkiestra Świątecznej Pomocy')

    def test_no_amount_raises(self):
        headers = [
            {'name': 'Subject', 'value': 'Inny email bez kwoty'},
            {'name': 'Date', 'value': 'Thu, 26 Mar 2026 07:00:46 +0100'},
        ]
        with self.assertRaises(ValueError):
            parse_donation(headers)


if __name__ == '__main__':
    unittest.main()
