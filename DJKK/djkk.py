import requests, os, re, time, webbrowser
import tkinter as tk
import threading
from fake_useragent import UserAgent

session = requests.Session()

ua = UserAgent().random
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': ua,
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.djkk.com',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.baidu.com/s?wd=djkk&rsv_spt=1&rsv_iqid=0xa6abe1b300055a5b&issp=1&f=8&rsv_bp=0&rsv_idx=2&ie=utf-8&rqlang=&tn=baiduhome_pg&ch=',
    'Connection': 'Keep-Alive'
}
headers2 = {
    'User-Agent': ua,
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Connection': 'Keep-Alive'
}


def loginCookie(url):
    global session
    session.get(url, headers=headers)
    return session.cookies.get_dict()


def mk_dir():
    """在本地创建文件存储目录"""
    path = os.path.join(os.getcwd(), "download")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


# GUI开始
# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('DJKK下载器 V 1.0')

# 第3步，设置窗口的居中显示
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
width = 700
height = 150
size = "%dx%d+%d+%d" % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
# 第4步，设定窗口的大小(长 * 宽)
window.geometry(size)

# 第5步，用户信息
tk.Label(window, text='下载地址:', font=('Arial', 14)).place(x=20, y=30)

# 第6步，下载地址输入框entry
var_url_input = tk.Entry(window, font=('Arial', 14), width='40')
var_url_input.place(x=120, y=30)


# 设置下载进度条
# tk.Label(window, text='进度:').place(x=40, y=80)
canvas = tk.Canvas(window, width=600, height=16, bg="white")
canvas.place(x=20, y=90)
label = tk.Label(window, text="")
label.place(x=630, y=90)
link = tk.Label(window, text='点击购买高级版本:  www.baidu.com', font=('Arial', 10))
link.place(x=20, y=130)


def open_url(event):
    webbrowser.open("http://www.baidu.com", new=0)


link.bind("<Button-1>", open_url)


def download(url):
    """正则匹配媒体文件地址"""
    label["text"] = "正在下载..."
    try:
        cookies_xxx = loginCookie('http://www.djkk.com/')
        rep = session.get(url, headers=headers, cookies=cookies_xxx, verify=False)
        title_pattern = "<title>(.*?)</title>"
        url_pattern = "http://mx.djkk.com/mix/([0-9/-]+).m4a"
        url_str = re.search(url_pattern, rep.text).group(0)
        title = re.search(title_pattern, rep.text).group(0).replace("title", "").replace("<", "").replace(">",
                                                                                                          "").replace(
            "/", "")
        m4a = session.get(url_str, headers=headers2, cookies=cookies_xxx, verify=False, stream=True)  # stream=True表示请求成功后并不会立即开始下载，而是在调用iter_content方法之后才会开始下载
        chunk_size = 40960  # 每次块大小为1024
        content_size = int(m4a.headers['content-length'])  # 返回的response的headers中获取文件大小信息
        # 填充进度条
        fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
        raise_data = 600 / (content_size/chunk_size)

        with open(mk_dir() + "\\" + title + '.m4a', 'wb') as f:
            n = 0
            for data in m4a.iter_content(chunk_size=chunk_size):    
                f.write(data)
                n = n + raise_data
                canvas.coords(fill_line, (0, 0, n, 60))
                window.update()
    except IOError:
        label["text"] = "下载异常"
    finally:
        if label["text"] == "正在下载...":
            label["text"] = "下载完成"


# 清空进度条
def clean_progressbar():
    # 清空进度条
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
    x = 500  # 未知变量，可更改
    n = 600 / x  # 465是矩形填充满的次数

    for t in range(x):
        n = n + 600 / x
        # 以矩形的长度作为变量值更新
        canvas.coords(fill_line, (0, 0, n, 60))
        window.update()
        time.sleep(0)  # 时间为0，即飞速清空进度条


# 第8步，定义用户下载功能
def usr_download():
    # 进度条如果是100%，则执行清空
    if label["text"] == "下载完成":
        clean_progressbar()
    url = var_url_input.get()
    t = threading.Thread(target=download, args=[url])
    t.setDaemon(True)
    t.start()


# 第7步，下载按钮
btn_download = tk.Button(window, text='开始下载', command=usr_download)
btn_download.place(x=600, y=28)

# 第10步，主窗口循环显示
window.mainloop()

