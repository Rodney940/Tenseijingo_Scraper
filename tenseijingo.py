# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs
import re
import os
import userinfo


class TenseijingoModule:
    __LOGIN_INFO = {
        'jumpUrl': 'https://www.asahi.com/?',
        'ref': None,
        'login_id': None,
        'login_password': None
    }

    __URL_LogIn = 'https://digital.asahi.com/login/login.html'
    __URL_BacknumberList = 'https://www.asahi.com/news/tenseijingo.html'

    @property
    def id(self):
        return self.__LOGIN_INFO['login_id']

    @property
    def password(self):
        return self.__LOGIN_INFO['login_password']

    def __init__(self, id, password):
        if id is None or password is None:
            raise ValueError("ID or Password shouldn't be None")
        self.__LOGIN_INFO['login_id'] = id
        self.__LOGIN_INFO['login_password'] = password

    def open_session(self):
        with requests.Session() as s:
            login_req = s.post(self.__URL_LogIn, data=self.__LOGIN_INFO)
            if login_req.status_code != 200:
                raise ConnectionError('Connection Failed')
            login_req.encoding = login_req.apparent_encoding
            soup = bs(login_req.text, 'html.parser')
            login_result = soup.findAll('ul', attrs={'class', 'Error'})
            if len(login_result) > 0:
                raise ConnectionError(str.strip(login_result[0].text))
            else:
                return s

    def get_contents_from_url(self, url: str):
        """
        URLから天声人語コンテンツを取得する
        :param url: str
            コンテンツ取得対象のURL
        :return: BeautifulSoup
            コンテンツ
        """
        if url:
            with self.open_session() as s:
                res = s.get(url)
                if res.status_code != 200:
                    raise ConnectionError
                res.encoding = res.apparent_encoding
                return bs(res.text, 'html.parser')
        else:
            raise ValueError

    def get_contents_from_urls(self, urls: list):
        """
        (deprecated) URLのリストから天声人語コンテンツを取得する
        :param urls: list
            コンテンツ取得対象のURL
        :return: list[BeautifulSoup]
            コンテンツ
        """
        if urls:
            with self.open_session() as s:
                results = list()
                for url in urls:
                    res = s.get(url)
                    if res.status_code != 200:
                        raise ConnectionError
                    res.encoding = res.apparent_encoding
                    results.append(bs(res.text, 'html.parser'))
                return results
        else:
            raise ValueError

    def convert_content_bs_to_dict(self, url):
        from datetime import datetime
        soup = self.get_contents_from_url(url)
        dic_result = {
                  'title': soup.findAll('h1')[0].text,
                  'content': soup.findAll('div', attrs={'class', 'ArticleText'})[0].text,
                  'datetime': datetime.strptime(soup.findAll('time', attrs={'class', 'LastUpdated'})[0].attrs['datetime'], "%Y-%m-%dT%H:%M")
                  }
        return dic_result

    def get_backnumber_list(self):
        soup = self.get_contents_from_url(self.__URL_BacknumberList)
        panels = soup.findAll('div', attrs={'class', 'TabPanel'})
        dic_article = dict()
        for panel in panels:
            list_items = panel.findAll('li')
            for item in list_items:
                _date = item['data-date']
                _title = item.findAll('em')[0].text
                _url = TenseijingoModule.get_individual_url_from_backnumber_url(item.findAll('a')[0]['href'])

                dic_article[_date] = {'title': _title, 'url': _url}
        return dic_article if len(dic_article) > 0 else None

    @staticmethod
    def get_individual_url_from_backnumber_url(url: str):
        pattern = r'^/articles/(\d|\D)+\.html\?iref\=tenseijingo_backnumber$'
        if re.compile(pattern).search(url):
            return 'https://digital.asahi.com' + url.split('?')[0]
        else:
            raise ValueError('Invalid URL')

    @staticmethod
    def making_html(content: dict):
        html = '<!DOCTYPE html> \
                    <html>\
                        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> \
                        <head>\
                            <h1>{0}</h1> \
                            <h3 align="right">{1}</h3>\
                        </head>\
                        <body> \
                            <p>{2}</p> \
                        </body>\
                    </html>'.format(content['title'], str(content['datetime']), content['content'])
        return html


def get_html_with_date(date_from: str, date_to: str):
    # Todo : Convert this method to module and make available query by date from to
    download_path = r'./html'
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # https://digital.asahi.com User Id and Password
    user_id = userinfo.id
    user_password = userinfo.password

    s = TenseijingoModule(user_id, user_password)
    try:
        s.open_session()

        # Get list of content
        article_list = s.get_backnumber_list()

        list_of_dates = [dt for dt in article_list.keys()]
        list_of_dates.sort()
        idx_from = list_of_dates.index(date_from)
        idx_to = list_of_dates.index(date_to) + 1

        # Todo:
        #   if there no from date or to date
        #       how to handle does dates which are inside range
        #       ex) dateFrom = '20191001', dateTo = '20191010'
        #           list_of_dates = ['20191005', '20191006', '20191007']

        for content_date in list_of_dates[idx_from:idx_to]:
            print(content_date, end=': ')
            html_name = download_path + '/' + content_date + '.html'
            if not os.path.exists(html_name):
                content_dic = article_list[content_date]
                content = s.convert_content_bs_to_dict(content_dic['url'])

                print('Downloading.. ' + html_name.split('/')[-1])
                html = TenseijingoModule.making_html(content)
                with open(html_name, 'w') as f:
                    f.write(html)
                    f.close()
            else:
                print('skip')
    except ConnectionError as e:
        print(e)


if __name__ == '__main__':
    from datetime import date
    get_html_with_date('20191001', date.today().strftime('%Y%m%d'))
