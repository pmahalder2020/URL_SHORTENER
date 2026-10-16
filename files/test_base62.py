import unittest

import base62


class TestBase62Encode(unittest.TestCase):
    def test_zero_encodes_to_first_character(self):
        self.assertEqual(base62.encode(0), "0")

    def test_single_digit_values(self):
        self.assertEqual(base62.encode(9), "9")
        self.assertEqual(base62.encode(10), "a")
        self.assertEqual(base62.encode(35), "z")
        self.assertEqual(base62.encode(36), "A")
        self.assertEqual(base62.encode(61), "Z")

    def test_first_two_character_value(self):
        # 62 is the first number that needs two digits: "10" in base62
        self.assertEqual(base62.encode(62), "10")

    def test_known_large_value(self):
        # 1,000,000 = 4*62^3 + 12*62^2 + 9*62 + 2 -> "4c92"
        self.assertEqual(base62.encode(1_000_000), "4c92")

    def test_output_only_uses_alphabet_characters(self):
        for n in (1, 61, 62, 3843, 3844, 123456789):
            self.assertTrue(set(base62.encode(n)) <= set(base62.ALPHABET))


class TestBase62Decode(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(base62.decode("0"), 0)
        self.assertEqual(base62.decode("10"), 62)
        self.assertEqual(base62.decode("4c92"), 1_000_000)

    def test_invalid_character_raises_value_error(self):
        for bad in ("abc!", "a-b", "hello world", "é"):
            with self.subTest(code=bad):
                with self.assertRaises(ValueError):
                    base62.decode(bad)


class TestBase62RoundTrip(unittest.TestCase):
    def test_round_trip_small_range(self):
        for n in range(0, 5000):
            self.assertEqual(base62.decode(base62.encode(n)), n)

    def test_round_trip_large_values(self):
        for n in (10**6, 10**9, 2**40, 2**63):
            self.assertEqual(base62.decode(base62.encode(n)), n)

    def test_different_ids_give_different_codes(self):
        codes = {base62.encode(n) for n in range(1, 10000)}
        self.assertEqual(len(codes), 9999)  # no collisions


if __name__ == "__main__":
    unittest.main()
