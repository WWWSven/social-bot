import json
from tempfile import NamedTemporaryFile
from app.core.AI import AiStructuredOutput, AI
from app.core.RedBook import RedBook
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

from app.models import Keyword


def test_save_history_note():
    temp_file = NamedTemporaryFile(delete=False)
    filepath = temp_file.name
    temp_file.close()
    ai_data = AiStructuredOutput(
        status="success",
        is_like=True,
        is_comment=True,
        is_fav=True,
        comment="good word",
        reason="no reason"
    )
    param = {"id": 'note_id', "ai_result": ai_data.model_dump()}
    RedBook._save_history_note(param, filepath)
    with open(filepath, 'r') as f:
        loaded_data = json.load(f)
        data = {'notes': []}
        data['notes'].append(param)
        assert loaded_data == data
    os.remove(filepath)


def test_web_driver():
    cwd = os.getcwd()
    # 获取绝对路径
    expect_path = os.path.join(cwd, ".wdm")
    os.environ['WDM_LOCAL'] = '1'
    print(f"正在测试Chrome驱动, 第一次会下载驱动到 backend/.wdm/ 下")
    driver_path = ChromeDriverManager().install()
    assert driver_path.startswith(expect_path)
    print(f'🎉 Chrome驱动安装路径:{driver_path}')


def test_gemini_api():
    load_dotenv()
    ai = AI()
    param = [{
                "type": "text",
                "text": json.dumps({
                    "title": "买保险拉",
                    "post": "这是一段买保险的文章 #保险推销>",
                    "author": "保险推销员小王",
                    "like_count": 0,
                    "comment_count": 0,
                    "fav_count": 0,
                    "channel": "推销 保险"
                }, ensure_ascii=False)
            }]
    default_keyword = Keyword(
        id="0f904720-1765-4ff9-ffff-f9360b08781a",
        name="美女",
        keywords=json.dumps(["清凉", "ootd", "纯欲"], ensure_ascii=False),
        prompts= None,
        is_active=True
    )
    ai_result = ai.chat(param, default_keyword, retry=False)
    if ai_result.status != 'success':
        print("检查代理配置")
    print(f"ai: {ai_result}")
    assert ai_result.status == "success"
    print(f"🎉 Gemini API 测试成功！")
