# web_crawler
版本 1.0 是单线程版本
Version  1.0 is a single-threaded version
1.5版本采用自定义多线程加优先级序列，旨在提高下载速度，效果较差，提高速度几乎为0
Version 1.5 adopts custom multi-threaded plus priority sequence, which is aimed at improving download speed and has poor results
2.0版本采用线程池下载，最大线程数为20，下载速度可提升10~15倍
Version 2.0 adopts thread pool download, the maximum number of threads is 20, and the download speed can be increased by 10~15 times
test.py文件是测试文件，获取网站每天自动更新的cookie
test.py file is a test file that captures cookies that are automatically updated daily by the website
