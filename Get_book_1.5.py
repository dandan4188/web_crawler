import requests
import re
import parsel
import os, time
import pandas as pd
# import threading
from concurrent.futures import ThreadPoolExecutor, wait ,ALL_COMPLETED, FIRST_COMPLETED 
from requests_html import UserAgent
import queue


# 章节优先级队列
priQue = queue.PriorityQueue()
# 文章主体优先级队列,为无限长
contentQue = queue.PriorityQueue(maxsize=-1)
# 存放线程的列表
ts =[]
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
    # herf.reverse()
    # novel_urls =[]
    for url in herf:
        novel_url = 'http://www.biqugse.com' + url
        priQue.put((Priority_num, novel_url))
        Priority_num += 1
        # novel_urls.append(novel_url)


# 找到小说文章并保存
def get_chapter_content(novel_url, index):  
    response = get_response(novel_url)
    selector = parsel.Selector(response.text)
    title = re.findall('<h1>(.*?)</h1>',response.text)[0]
    # print(title)
    content_list = selector.css('#content::text').getall()
    content = '\n'.join(content_list)
    content += '\n'
    contentQue.put((index, title, content))



def get_novel_content():
    while not priQue.empty():
            urlData = priQue.get()
            # 章节地址
            firstUrl = urlData[1]
            # 章节数字
            index = urlData[0]
            get_chapter_content(firstUrl, index) 
            
            
    


def save(name:str):
    print(contentQue.empty())
    while not contentQue.empty():
        data = contentQue.get()
        title = data[1]
        content = data[2]
        path = os.path.dirname(__file__)
        with open(path + '\\' + name + '.txt', mode='a', encoding='utf-8') as f:
            f.write(title)
            f.write('\n')
            f.writelines(content)
            f.write('\n\n')


# 搜索功能
def serch(book_name):
    lis = []
    ua = UserAgent().random
    data = {'key': book_name}
    # Cookies = input('请输入Cookies')
    header = {
        'user-agent' : ua,
        'Cookie': 'obj=1; 796ab53acf966fbacf8f078ecd10a9ce=a%3A1%3A%7Bi%3A28801%3Bs%3A24%3A%2251387311%7C%2A%7C%E7%AC%AC1%E7%AB%A0%E7%A7%9F%E6%88%BF%22%3B%7D; PHPSESSID=kigrt4hfuvmpvs08iopmjn1er1; eee124c39a6d9bc42108981154c5ab0c=1; Hm_lvt_7a41ef5a4df2b47849f9945ac428a3df=1668612958,1668671534,1668769884,1668935895; Hm_lpvt_7a41ef5a4df2b47849f9945ac428a3df=1668935898'
    }
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
        # print(book_url)
        return book_url
    else:
        print('未查找到书籍！\n')

        

def main():
    while True:
        print("输入'0'退出程序\n")
        book_name = input('请输入书名:\n')
        if book_name == '0':
            break
        book_url = serch(book_name)

        start_time = time.time()

        response = get_response(book_url)
        book_name = re.findall('<h1>(.*?)</h1>',response.text)[0]
        # print(book_name)
        get_novel_url(book_url)
        #判断小说文件是否重复，若重复，删除
        path = os.path.dirname(__file__)
        if os.path.exists(path + '\\' + book_name + '.txt'):
            os.remove(path + '\\' + book_name + '.txt')
        
        All_task = [pool.submit(get_novel_content)]
        # 保存书籍
        wait(All_task, return_when=ALL_COMPLETED)
        save(book_name)
        
        # for i in range(20):
        #     print('')
        #     t = threading.Thread(target=get_novel_content(), name='download')
        #     t.start()
        #     print('yes')
        #     ts.append(t)
        # for t in ts:
        #     t.join()
        

        # while not priQue.empty():
        #     print(priQue.get())

        # for index in tqdm(herf):
        #     get_novel_content_and_save(name=book_name, novel_url=index)
        print(f'{book_name}已经下载完成了:')
        end_time = time.time()
        print((end_time-start_time))

if __name__ =='__main__':
    main()