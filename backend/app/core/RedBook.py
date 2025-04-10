import base64
import json
import logging
import os
import random
from sqlmodel import select
import requests
from PIL import Image
from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service as ChromeService

from app.core.AI import AiStructuredOutput
from app.core.local import LocalStorage
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from app.models import XHSHistory, Keyword, Settings


class RedBook:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.currentPosts = []
            cls._instance.currentPost = None
            cls._instance.reallyDo = False  # False测试, 不真点赞收藏评论
            cls._instance.doVideoNote = True  # 视频笔记是否操作

            # self.mainPage = 'https://www.xiaohongshu.com/explore'
            cls._instance.explorePage = 'https://www.xiaohongshu.com/explore?channel_id=homefeed.cosmetics_v3'
            cls._instance.keyword = Keyword(keywords= '["openai", "gemini"]')
            keywords_str = ' '.join(json.loads(cls._instance.keyword.keywords))
            cls._instance.mainPage = f'https://www.xiaohongshu.com/search_result?keyword={keywords_str}&source=web_search_result_notes'
            cls._instance.session = requests.session()
            cls._instance.driver = None
            cls._instance.is_running = False
            cls._instance.active_job = False
        return cls._instance


    def run(self, ai, session_dep, sse):
        time.sleep(2)
        while True:
            time.sleep(1)
            if self.active_job is False:
                self.is_running = False
                if self.driver is None:
                    return
                print(f'定时任务未启动{self.active_job}')
                sse.broadcast_message(f"定时任务{'启动' if self.active_job else '未启动'}")
                time.sleep(1)
                continue
            self.is_running = True

            active_Keyword = self._get_active_keyword(session_dep)
            print(f'激活的关键字: {active_Keyword.name}')
            sse.broadcast_message(f"当前关键字{active_Keyword.name}")
            new_search_page_url = self._get_new_main_page(active_Keyword.keywords)
            if self.mainPage != new_search_page_url:
                self.driver.get(new_search_page_url)
            self.mainPage = new_search_page_url

            global_interval: Settings = session_dep.execute(select(Settings).where(Settings.id == 'global_interval')).first()[0]

            try:
                time.sleep(random.randint(3, 10))
                posts = self._find_post_list()
                sse.broadcast_message(f"找到了{len(posts)}篇笔记")
                for post in posts:
                    if self.active_job is False:
                        continue
                    note_id = self._get_current_note_id(post)
                    if note_id and self._is_history_note(note_id):
                        print("本篇笔记已操作过，跳过")
                        continue
                    post_el = self._click_post_detail(post)
                    if post_el:
                        print("开始操作内容")
                        if not post_el.is_displayed():
                            print("元素丢失")
                            continue

                        print("获取内容详情")
                        post_detail = self._get_current_post_detail(post_el, active_Keyword.name, sse)
                        self._save_post_in_db(post_detail, active_Keyword.id, session_dep)
                        try:
                            ai_result: AiStructuredOutput = ai.chat(post_detail, active_Keyword)
                        except Exception as e:
                            print("AI请求异常: %s" % e)
                            time.sleep(10)
                            continue
                        print(f"AI返回结果: {ai_result}")
                        sse.broadcast_message(ai_result.reason)
                        self._save_history_note({"id": note_id, "ai_result": ai_result.model_dump()})
                        if ai_result.status == 'success':
                            if self.reallyDo and ai_result.is_like:
                                self._like(post_el)
                                sse.broadcast_message("为本篇笔记点赞")
                                time.sleep(2)
                            if self.reallyDo and ai_result.is_fav:
                                self._fav(post_el)
                                sse.broadcast_message("为本篇笔记收藏")
                                time.sleep(2)
                            if self.reallyDo and ai_result.is_comment:
                                comment = ai_result.comment
                                if comment:
                                    print(f"评论内容: {comment}")
                                    self._comment(post_el, comment)
                                    sse.broadcast_message(f"为本篇笔记评论: {comment}")
                                    time.sleep(2)
                            print("本篇笔记已操作完成")
                            sse.broadcast_message(f"本篇笔记操作完成")
                            self.driver.back()
                            sleep_time = int(global_interval.value) + random.randint(1, 5)
                            print(f'休息{sleep_time}秒')
                            sse.broadcast_message(f'休息{sleep_time}秒')
                            time.sleep(sleep_time)
                        else:
                            if self.driver.current_url != self.mainPage:
                                self.driver.back()
                            sse.broadcast_message(f'本篇笔记已跳过')
                            print("本篇笔记已跳过")

                    else:
                        print("没有展开笔记详情，稍后重试")

                    time.sleep(1)

            except Exception as e:
                logging.exception(e)

            finally:
                print("本轮任务结束，等待5秒后刷新")
                sse.broadcast_message(f'本轮任务结束，等待5秒后刷新')
                time.sleep(5)
                print("当前页面url: %s" % self.driver.current_url)
                if self.mainPage == self.explorePage and self.driver.current_url.find(self.mainPage) == -1:
                    self.driver.get(self.mainPage)
                else:
                    if self.driver.current_url.find("search_result") != -1:
                        # 往下拉到底部加载更多
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        print("至底部等待5秒加载完毕")
                        time.sleep(5)  # 等5秒加载完毕
                    else:
                        reload_el = self.driver.find_elements(By.CLASS_NAME, "reload")
                        if reload_el:
                            reload_el = reload_el[0]
                            reload_el.click()
                        else:
                            self.driver.refresh()

    def start_browser(self, session_dep, debug=True):
        active_keyword = self._get_active_keyword(session_dep)
        self.mainPage = self._get_new_main_page(active_keyword.keywords)

        dir_name = os.path.dirname(os.path.abspath(__file__))
        stealth_path = os.path.join(dir_name, "stealth.min.js")
        with open(stealth_path) as f:
            js = f.read()

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("lang=zh-CN,zh")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 去webdriver痕迹

        self.driver = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
        # 设置窗口尺寸（单位：像素）
        self.driver.set_window_size(1200, 800)  # width, height
        # 设置窗口位置（屏幕坐标）
        self.driver.set_window_position(100, 200)  # x, y
        self.driver.get(self.mainPage)
        self.storage = LocalStorage(self.driver)
        time.sleep(1)
        if not self._get_session():
            print("已调用完毕自动登录，如果长时间没动静，请手动刷新页面，还没有登录状态则手动登录或重新运行程序...")
            self._login()
            self._save_session()

    def stop_browser(self):
        self.active_job = False
        self.driver.close()
        self.driver = None

    def _login(self) -> str:
        while True:
            users = self.driver.find_elements(By.CLASS_NAME, "user")
            if users:
                user = users[0]
                profile_url = user.find_element(By.TAG_NAME, "a")
                print("登录成功，用户主页:", profile_url.get_attribute("href"))
                break
            else:
                print("未完成登录")
            time.sleep(3)
        return profile_url.get_attribute("href")

    def _find_post_list(self):
        post_container = None
        if self.driver.current_url.find("explore") != -1:
            print("发现页面的列表")
            post_container = self.driver.find_elements(By.ID, "exploreFeeds")
        if self.driver.current_url.find("search_result") != -1:
            print("搜索页面的列表")
            post_container = self.driver.find_elements(By.CLASS_NAME, "feeds-container")
        if not post_container:
            print("未找到帖子列表")
            return []
        posts = post_container[0].find_elements(By.CLASS_NAME, "note-item")
        print("找到帖子列表, 数量: %d" % len(posts))
        self.currentPosts = posts
        new_posts = []
        for post in posts:
            current_note_id = self._get_current_note_id(post)
            if current_note_id and not self._is_history_note(current_note_id):
                new_posts.append(post)
        return new_posts

    def _click_post_detail(self, post):
        is_video = post.find_elements(By.CLASS_NAME, "play-icon")
        if self.doVideoNote is False and is_video:
            print("下一个操作笔记是视频，即将跳过")
            time.sleep(1)
            return None
        post.click()
        time.sleep(3)
        current_url = self.driver.current_url
        print("点击帖子, url: %s" % current_url)
        self.currentPost = post
        parent_el = self.driver.find_elements(By.CLASS_NAME, "note-detail-mask")
        if parent_el:
            print("找到帖子详情")
            return parent_el[0]
        else:
            print("未找到帖子详情")
        return None

    def _get_current_post_detail(self, parent_el, channel, sse):
        title_el = parent_el.find_elements(By.ID, "detail-title")
        title = ""
        if title_el:
            title = title_el[0].text
            print("找到帖子标题, title: %s" % title)

        author_el = self.driver.find_elements(By.CLASS_NAME, "username")
        author = ""
        if author_el:
            author = author_el[1].text
            print("找到作者昵称, title: %s" % author)

        content_el = parent_el.find_elements(By.ID, "detail-desc")
        content = ""
        if content_el:
            inner_text = self.driver.execute_script("return arguments[0].innerText;", content_el[0])
            content = inner_text
            print("找到帖子内容")

        media_el = parent_el.find_elements(By.CLASS_NAME, "note-slider-img")
        media = []
        if media_el:
            print("找到帖子媒体, 数量: %d" % len(media_el))
            try:
                for mediaItemEl in media_el:
                    if mediaItemEl.is_displayed():
                        print("找到媒体, url: %s" % mediaItemEl.get_attribute("src"))
                        media.append(mediaItemEl.get_attribute("src"))
            except Exception as e:
                print("媒体获取发生异常: %s" % e)

        if not media:
            og_meta_el = self.driver.find_elements(By.XPATH, "//meta[@name='og:image']")
            if og_meta_el:
                print("找到帖子媒体, url: %s" % og_meta_el[0].get_attribute("content"))
                media.append(og_meta_el[0].get_attribute("content"))

        data_el = parent_el.find_elements(By.CLASS_NAME, "interact-container")
        if not data_el:
            print("未找到帖子互动数据")
            return {
                "title": title,
                "content": content,
                "media": media
            }
        data_el = data_el[0]

        like_total_text = ''
        like_total_el = data_el.find_elements(By.CLASS_NAME, "like-active")
        if like_total_el:
            like_total = like_total_el[0].find_elements(By.CLASS_NAME, "count")
            if like_total:
                like_total_text = like_total[0].text
                print("找到点赞总数, total: %s" % like_total_text)

        fav_total_text = ''
        fav_total_el = data_el.find_elements(By.CLASS_NAME, "collect-wrapper")
        if fav_total_el:
            fav_total = fav_total_el[0].find_elements(By.CLASS_NAME, "count")
            if fav_total:
                fav_total_text = fav_total[0].text
                print("找到收藏总数, total: %s" % fav_total_text)

        com_total_text = ''
        com_total_el = data_el.find_elements(By.CLASS_NAME, "chat-wrapper")
        if com_total_el:
            com_total = com_total_el[0].find_elements(By.CLASS_NAME, "count")
            if com_total:
                com_total_text = com_total[0].text
                print("找到评论总数, total: %s" % com_total_text)

        if media:
            media_path = self._download_media(media[0])
            with open(media_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        sse_msg = f'找到{author}的<<{title}>>文章, 点赞:{like_total_text}个, 收藏:{fav_total_text}个, 评论:{com_total_text}个'
        sse.broadcast_message(sse_msg)
        return [
            {
                'type': "image_url",
                "image_url": {
                    "url": f"data:image/webp;base64,{base64_image}"
                }
            },
            {
                "type": "text",
                "text": json.dumps({
                    "title": title,
                    "author": author,
                    "content": content,
                    "like_count": like_total_text,
                    "fav_count": fav_total_text,
                    "comment_count": com_total_text,
                    "channel": channel
                }, ensure_ascii=False)
            }
        ]

    def _like(self, post_div_el):
        data_el = post_div_el.find_elements(By.CLASS_NAME, "interact-container")
        if not data_el:
            print("未找到帖子互动数据")
            return False
        data_el = data_el[0]
        like_el = data_el.find_elements(By.CLASS_NAME, "like-active")
        if like_el:
            if self.reallyDo:
                like_el[0].click()
            print("点赞完成")
            return True
        else:
            print("没有找到点赞按钮")
        return False

    def _fav(self, post_div_el):
        data_el = post_div_el.find_elements(By.CLASS_NAME, "interact-container")
        if not data_el:
            print("未找到帖子互动数据")
            return False
        data_el = data_el[0]
        fav_el = data_el.find_elements(By.CLASS_NAME, "collect-wrapper")
        if fav_el:
            if self.reallyDo:
                fav_el[0].click()
            print("收藏完成")
            return True
        else:
            print("没有找到收藏按钮")
        return False

    def _comment(self, post_div_el, comment):
        data_el = post_div_el.find_elements(By.CLASS_NAME, "interact-container")
        if not data_el:
            print("未找到帖子互动数据")
            return False
        data_el = data_el[0]
        com_el = data_el.find_elements(By.CLASS_NAME, "chat-wrapper")
        if com_el:
            com_el[0].click()
            time.sleep(1)
            print("展开评论")
            try:
                input_el = post_div_el.find_element(By.ID, "content-textarea")
                self.driver.execute_script("arguments[0].click();", input_el)
                input_el.send_keys(comment)
                time.sleep(3)
                send_el = post_div_el.find_element(By.CLASS_NAME, "submit")
                if self.reallyDo:
                    send_el.click()
                print("发送评论,评论完成")
                return True
            except Exception as e:
                print("评论发生异常: %s" % e)
                return False
        else:
            print("没有找到评论按钮")
        return False

    @staticmethod
    def _get_current_note_id(post):
        id_element = post.find_elements(By.TAG_NAME, "a")
        if id_element:
            id_element = id_element[0].get_attribute("href")
            return id_element.split("/")[-1]
        else:
            print("未找到帖子id")
            return None

    @staticmethod
    def _is_history_note(note_id):
        file_name = 'history.json'
        if not os.path.exists(file_name):
            with open(file_name, 'w') as f:
                f.write(json.dumps({'notes': []}, ensure_ascii=False))
        with open(file_name, 'r') as f:
            data = json.loads(f.read())
            for note in data['notes']:
                if note['id'] == note_id:
                    return True
        return False

    @staticmethod
    def _save_history_note(info_data, file_path='history.json'):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)  # 使用json.load更安全
        except (FileNotFoundError, json.JSONDecodeError):
            data = {'notes': []}  # 如果文件不存在或格式错误，创建新的字典
        data['notes'].append(info_data)
        with open(file_path, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False))

    def _download_media(self, media_url, resize=True) -> str | None:
        if not os.path.isdir('media'):
            os.mkdir('media')
        file_name = "%s.webp" % media_url.split('/')[-1]
        media_path = os.path.join('media', file_name)
        if os.path.isfile(media_path):
            print("媒体已存在, 跳过下载")
        else:
            print("开始下载媒体, url: %s" % media_url)
            response = self.session.get(media_url)
            with open(media_path, 'wb') as f:
                f.write(response.content)
            print("媒体下载完成, 保存路径: %s" % media_path)

        if not os.path.isfile(media_path):
            print("媒体下载失败")
            return None
        if resize:
            image = Image.open(media_path)
            image.save("%s.new.webp" % media_path)
            resize_path = "%s.new.webp" % media_path
            if resize_path:
                return resize_path
            else:
                print("媒体缩放失败，用原图")
        return media_path

    def _get_session(self):
        if os.path.isfile("cookie"):
            with open("cookie", "r") as f:
                cookies = f.read()
                if cookies:
                    json_cookies = json.loads(cookies)
                    for cookie_item in json_cookies:
                        self.driver.add_cookie(cookie_item)

        if os.path.isfile("localstorage"):
            with open("localstorage", "r") as f:
                localstorage = f.read()
                if localstorage:
                    json_storage = json.loads(localstorage)
                    for k in json_storage:
                        self.driver.execute_script("localStorage.setItem('%s', '%s')" % (k, json_storage[k]))
        self.driver.refresh()
        return False

    def _save_session(self):
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            self.session.cookies[cookie['name']] = cookie['value']
        self.session.headers['User-Agent'] = self.driver.execute_script("return navigator.userAgent")

        with open("cookie", "w") as f:
            f.write(json.dumps(cookies))

        local_storage = self.storage.items()
        with open("localstorage", "w") as f:
            f.write(json.dumps(local_storage))

        return True

    def _save_post_in_db(self, post_detail, keyword_id, session_dep):
        post_detail_str = json.dumps(post_detail, ensure_ascii=False)
        new_history = XHSHistory(
            keyword_id=keyword_id,
            detail=post_detail_str
        )
        session_dep.add(new_history)
        session_dep.commit()

    def _get_active_keyword(self, session_dep) -> Keyword:
        active_Keyword_db = select(Keyword).where(Keyword.is_active == True)
        result = session_dep.execute(active_Keyword_db).scalars().all()
        active_keyword: Keyword = result[0]
        return active_keyword

    def _get_new_main_page(self, keywords: str) -> str:
        keywords_str = ' '.join(json.loads(keywords))
        new_page = f'https://www.xiaohongshu.com/search_result?keyword={keywords_str}&source=web_search_result_notes'
        return new_page


