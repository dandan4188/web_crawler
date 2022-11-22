import requests
import re
import parsel
import os, time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from requests_html import UserAgent
import queue


# 章节优先级队列
priQue = queue.PriorityQueue()
pool = ThreadPoolExecutor(max_workers=20)

# 发生请求
def get_response(html_url):
    ua = UserAgent().random
    response = requests.get(url=html_url, headers={'user-agent' : ua})
    response.encoding = response.apparent_encoding
    return response

# 获得小说每个章节的url地址
def get_novel_url(html_url):
    Priority_num = 1
    response = get_response(html_url)
    seltector = parsel.Selector(response.text)
    # 前9章是推荐章节，我们不需要
    herf = seltector.css('#list dd a::attr(href)').getall()[9:]
    for url in herf:
        novel_url = 'http://www.biqugse.com' + url
        priQue.put((Priority_num, novel_url))
        Priority_num += 1


# 找到小说文章并保存
def get_chapter_content(novel_url, index, path):  
    response = get_response(novel_url)
    selector = parsel.Selector(response.text)
    title = re.findall('<h1>(.*?)</h1>',response.text)[0]
    content_list = selector.css('#content::text').getall()
    content = '\n'.join(content_list)
    content += '\n'
    print(f'{title} 已完成！')
    with open(path + '//' + '缓存' + '//' + f'{index}.txt', 'w', encoding='utf-8') as f:
        f.write(title)
        f.write('\n')
        f.writelines(content)
        f.write('\n\n')




def get_novel_content():
    print(priQue.empty())
    path = os.path.dirname(__file__)
    while not priQue.empty():
            urlData = priQue.get()
            # 章节地址
            firstUrl = urlData[1]
            # 章节数字
            index = urlData[0]
            # print(index)
            get_chapter_content(firstUrl, index, path) 
            
            
    

# 保存
def save(book_name, path):
    with open(path + '\\' +f'{book_name}.txt', 'a', encoding='utf-8') as f:
        for num in range(1,len(os.listdir(os.path.join(path, '缓存')))+1):
            path_1 = path + '\\' + '缓存' + '\\' + f'{num}.txt'
            content = open(path_1, 'r', encoding='utf-8').read()
            f.write(content)
            os.remove(path_1)
        print(f'{book_name} 下载完成')
    

# 搜索功能
def serch(book_name):
    lis = []
    ua = UserAgent().random
    data = {'key': book_name}
    # 获取Cookies
    r_cookie = get_response(html_url='http://www.biqugse.com/')
    pass_id =  r_cookie.cookies.get_dict()['PHPSESSID']
    pass_id2 = r_cookie.cookies.get_dict()['b28ea585bfe8eadf981fa538e26beed2']
    Cookies = f'obj=1; 796ab53acf966fbacf8f078ecd10a9ce=a%3A3%3A%7Bi%3A28801%3Bs%3A24%3A%2251387311%7C%2A%7C%E7%AC%AC1%E7%AB%A0%E7%A7%9F%E6%88%BF%22%3Bi%3A22510%3Bs%3A25%3A%2237975040%7C%2A%7C%E7%AC%AC95%E7%AB%A0%E5%B0%8F%E5%BA%99%22%3Bi%3A44947%3Bs%3A24%3A%2265939281%7C%2A%7C%E7%AC%AC1%E7%AB%A0%E6%B5%B4%E8%A1%80%22%3B%7D; PHPSESSID={pass_id}; b28ea585bfe8eadf981fa538e26beed2={pass_id2}; Hm_lvt_7a41ef5a4df2b47849f9945ac428a3df=1668769884,1668935895,1669038696,1669091578; Hm_lpvt_7a41ef5a4df2b47849f9945ac428a3df=1669091578'
    header = {
        'user-agent' : ua,
        'Cookie':  Cookies
    }
    # 开始搜索
    response = requests.post(url='http://www.biqugse.com/case.php?m=search', headers=header,data=data)
    response.encoding = response.apparent_encoding
    seltector = parsel.Selector(response.text) #转换为Selector对象进行css搜索
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
        num = input('请输入你要下载小说的序号:\n')      
        num_id = lis[int(num)]['书ID']
        book_url = 'http://www.biqugse.com/' + num_id + '/'
        return book_url
    else:
        print('未查找到书籍！\n')

def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):#如果是文件夹那么递归调用一下
            del_file(c_path)
        else:                    #如果是一个文件那么直接删除
            os.remove(c_path)


def main():
    while True:
        print("输入'0'退出程序\n")
        book_name = input('请输入书名:\n')
        if book_name == '0':
            break
        book_url = serch(book_name)
        #程序开始时间
        start_time = time.time()
        response = get_response(book_url)
        book_name = re.findall('<h1>(.*?)</h1>',response.text)[0]
        get_novel_url(book_url)
        #判断小说文件是否重复，若重复，删除
        pth = os.path.dirname(__file__)
        if os.path.exists(pth + '\\' + book_name + '.txt'):
            os.remove(pth + '\\' + book_name + '.txt')
        if os.path.exists(os.path.join(pth, '缓存')) == False:
            os.mkdir(os.path.join(pth, '缓存'))
        del_file(os.path.join(pth, '缓存'))
        # 提交多线程任务
        for i in range(20):
            All_task = pool.submit(get_novel_content)
        # 保存书籍
        pool.shutdown(wait=True)
        print('缓存成功！！\n')
        time.sleep(3)
        save(book_name,pth)
        end_time = time.time()
        print((end_time-start_time))

if __name__ =='__main__':
    main()