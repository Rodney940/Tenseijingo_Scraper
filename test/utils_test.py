import unittest
import tenseijingoscraper.utils as utils
from tenseijingoscraper.utils import DateHandling


class TestUtils(unittest.TestCase):
    def test_create_file(self):
        # file should be created at designated path
        # return False if file already exists
        self.assertFalse(utils.create_file())
        # return True if file created successfully
        self.assertTrue(utils.create_file())

    def test_making_file_name(self):
        # file name should be combination of path and filename(date) with .html
        self.assertEqual('./testdirectory/20200217.html', utils.making_file_name('./testdirectory', '20200217'))


class TestDateHandling(unittest.TestCase):
    def test_get_str_date_n_days_ago(self):
        self.assertEqual(DateHandling.get_str_date_n_days_ago('20191003', 2), '20191001')

    def test_rearrange_date_arguments(self):
        date_from, date_to = DateHandling.rearrange_date_arguments('20190101', '20181231')
        self.assertTrue(date_from < date_to)

    def test_get_substantive_start_date(self):
        dl = ['20191001', '20191002', '20191003']
        self.assertEqual(DateHandling.get_substantive_start_date('20190311', dl), '20191001')

    def test_get_substantive_end_date(self):
        dl = ['20191001', '20191002', '20191003']
        self.assertEqual(DateHandling.get_substantive_end_date('20190311', dl), '20191003')

    def test_convert_to_date_object(self):
        from datetime import datetime
        self.assertIsInstance(DateHandling.convert_to_date_object('2019-10-03T03:11+09:00'), datetime)


if __name__ == '__main__':
    unittest.main()
