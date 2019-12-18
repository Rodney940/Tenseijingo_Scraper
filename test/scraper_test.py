import unittest
from bs4 import BeautifulSoup as bs
from tenseijingoscraper import userinfo
from tenseijingoscraper.scraper import AsahiShinbunScraper


class TestAsahiShinbunScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user_id = userinfo.id
        cls.user_pw = userinfo.password
        cls.obj = AsahiShinbunScraper(cls.user_id, cls.user_pw)
        cls.test_url = 'https://digital.asahi.com/articles/DA3S14297045.html'

    def test_init(self):
        self.assertEqual(self.obj.id, self.user_id)
        self.assertEqual(self.obj.password, self.user_pw)

    def test_open_session(self):
        import requests
        s = self.obj.open_session()
        self.assertIsInstance(s, requests.Session)

    def test_get_contents_from_url(self):
        self.assertIsInstance(
            self.obj.get_contents_from_url(self.test_url),
            bs
        )

    def test_get_contents_from_urls(self):
        results = self.obj.get_contents_from_urls([self.test_url])
        self.assertIsInstance(results, list)
        for res in results:
            self.assertIsInstance(res, bs)

    def test_convert_content_bs_to_dict(self):
        result_ok = self.obj.convert_content_bs_to_dict(self.test_url)
        # result_should_be_instance_of_dict
        self.assertIsInstance(result_ok, dict)
        # check element's type
        import datetime
        self.assertIsInstance(result_ok['title'], str)
        self.assertIsInstance(result_ok['content'], str)
        self.assertIsInstance(result_ok['datetime'], datetime.datetime)

    def test_get_backnumber_list(self):
        result = self.obj.get_backnumber_list()
        self.assertIsInstance(result, dict)
        # count_of_result
        self.assertTrue(1 <= len(result) <= 122)
        # elements_of_dict_level1
        for item in result:
            # is element string
            self.assertIsInstance(item, str)
            # is element 8digits
            self.assertEqual(len(item), 8)
            # is element date
            self.assertRegex(item, '^20\d\d[0-1]{1}\d[0-3]\d$')
        # elements_of_dict_level2
        for item in result.values():
            for key, value in item.items():
                if key == 'title':
                    self.assertRegex(value, '\w+')
                if key == 'url':
                    self.assertRegex(value, '^http(s)?://digital\.asahi\.com/articles/(\d|\D)+\.html$')


if __name__ == '__main__':
    unittest.main()
