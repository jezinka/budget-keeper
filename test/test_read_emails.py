import unittest

from read_emails import prepare_message_dict


class TestReadMails(unittest.TestCase):

    def test_prepare_message_dict_empty(self):
        with self.assertRaises(AttributeError):
            prepare_message_dict('', True)

    def test_prepare_message_dict_card_expense(self):
        body = 'W związku z transakcją ZAKUPY na Twojej karcie debetowej zostało zablokowane -19,22 PLN. Szczegóły:Karta:Dopasowana Visa 1234 Ile:-19,22 PLN Kiedy:05-01-2023 Gdzie:JMP S.A. BIEDRONKA 1244 WROCLAWTel'
        self.assertDictEqual(prepare_message_dict(body, False),
                             {'kwota': '19,22', 'kiedy': '05-01-2023', 'tytul': 'JMP S.A. BIEDRONKA 1244 WROCLAW'})

    def test_prepare_message_dict_income(self):
        body = 'Na Twoje konto wpłynęło 9 999,98 PLN od PAULINA KACZMAREK.Szczegóły przelewu:Tytuł:Przelew własnyNadawca:PAULINA KACZMAREKKwota:9 999,98 PLNNa konto:11 2222 3333 4444 5555 6666 7777 Stan konta po przelewie:Saldo:9 999,99 PLN Tel'
        self.assertDictEqual(prepare_message_dict(body, True),
                             {'tytul': 'Przelew własny', 'kto': 'PAULINA KACZMAREK', 'kwota': '9 999,98'})

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


if __name__ == '__main__':
    unittest.main()
