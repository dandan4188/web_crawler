import requests
import parsel
from requests_html import UserAgent
import pandas as pd

url = 'http://www.biqugse.com/'
ua = UserAgent().random


def get_response(html_url):
    response = requests.get(url=html_url, headers={'user-agent' : ua})
    response.encoding = response.apparent_encoding
    return response

r = get_response(url)
pass_id =  r.cookies.get_dict()['PHPSESSID']
pass_id2 = r.cookies.get_dict()['b28ea585bfe8eadf981fa538e26beed2']
cookies = f'obj=1; 796ab53acf966fbacf8f078ecd10a9ce=a%3A3%3A%7Bi%3A28801%3Bs%3A24%3A%2251387311%7C%2A%7C%E7%AC%AC1%E7%AB%A0%E7%A7%9F%E6%88%BF%22%3Bi%3A22510%3Bs%3A25%3A%2237975040%7C%2A%7C%E7%AC%AC95%E7%AB%A0%E5%B0%8F%E5%BA%99%22%3Bi%3A44947%3Bs%3A24%3A%2265939281%7C%2A%7C%E7%AC%AC1%E7%AB%A0%E6%B5%B4%E8%A1%80%22%3B%7D; PHPSESSID={pass_id}; b28ea585bfe8eadf981fa538e26beed2={pass_id2}; Hm_lvt_7a41ef5a4df2b47849f9945ac428a3df=1668769884,1668935895,1669038696,1669091578; Hm_lpvt_7a41ef5a4df2b47849f9945ac428a3df=1669091578'

url_search = 'http://www.biqugse.com/case.php?m=search'
book_name = input('请输入书籍:\n')
header = {
    'User-Agent' : ua,
    'Cookie' : cookies
}
data = {'key': book_name}

lis =[]

r2 = requests.post(url=url_search, headers=header, data=data)
r2.encoding = r2.apparent_encoding
seltector = parsel.Selector(r2.text) #转换为Selector对象进行css搜索
books_allinformation = seltector.css('#newscontent div.l ul li').getall() # 搜索书籍信息
    # 遍历书籍信息进行保存
if books_allinformation:
    for book_information in books_allinformation:
        # 将字符串转化为Selector对象
        book_information = parsel.Selector(book_information) 
        novel_name = book_information.css('span.s2 a::text').get()
        novel_id = book_information.css('span.s2 a::attr(href)').get().replace('/', '')
        author = book_information.css('span.s4::text').get()
        dit = {
            '书名':novel_name,
            '作者':author,
            '书ID':novel_id
        }   
        lis.append(dit)   
    print(f'共搜索到{len(lis)}书籍')
    search_result = pd.DataFrame(lis)
    print(search_result) 