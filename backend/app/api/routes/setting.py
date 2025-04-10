import json
import threading
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from selenium.common import WebDriverException
from sqlmodel import select
from app.api.deps import SessionDep, RedBookDep, AIDep, SSEDep
from app.models import Settings, Keyword, SettingsUpdate, KeywordCreate, KeywordBase, KeywordUpdate, KeywordPublic, \
    XHSHistory

router = APIRouter(prefix="/setting", tags=["setting"])


@router.get("/intervalMinutes/", summary='获取任务间隔时间')
def intervalMinutes(session: SessionDep):
    setting = session.get(Settings, 'global_interval')
    return {"intervalMinutes": setting.value}


@router.patch("/update_intervalMinutes/", summary='修改任务间隔时间')
def update_intervalMinutes(setting: SettingsUpdate, session: SessionDep):
    setting_db = session.get(Settings, 'global_interval')
    if not setting_db:
        raise HTTPException(status_code=404, detail="setting not found")
    setting_data = setting.model_dump(exclude_unset=True)
    setting_db.sqlmodel_update(setting_data)
    session.add(setting_db)
    session.commit()
    session.refresh(setting_db)
    return {"intervalMinutes": setting_db.value}


@router.get("/keywordStrings/", summary='获取所有关键字')
def keywordStrings(session: SessionDep):
    def getHistoryListByKeyWordId(id: str):
        re = []
        his: list[XHSHistory] = session.exec(select(XHSHistory).where(XHSHistory.keyword_id==id))
        for item_his in his:
            re.append(item_his.id)
        return re
    data = session.exec(select(Keyword)).all()
    processed_data = []
    for item in data:
        processed_item = {
            "id": item.id,
            "name": item.name,
            "keywords": json.loads(item.keywords),  # 将 keywords 字符串转换为列表
            "isActive": item.is_active,  # 将 is_active 映射为 isActive
            "collectedContent": getHistoryListByKeyWordId(item.id),
            "prompts": item.prompts
        }
        processed_data.append(processed_item)

    return processed_data


@router.post("/add_keywordStrings/", summary='添加关键字')
def add_keywordStrings(keyword: KeywordCreate, session: SessionDep):
    keyword_db = Keyword.model_validate(keyword)
    session.add(keyword_db)
    session.commit()
    session.refresh(keyword_db)
    processed_item = {
        "id": keyword_db.id,
        "name": keyword_db.name,
        "keywords": json.loads(keyword_db.keywords),  # 将 keywords 字符串转换为列表
        "isActive": keyword_db.is_active,  # 将 is_active 映射为 isActive
        "prompts": keyword_db.prompts
    }
    return processed_item

@router.patch("/update_keywordStrings/", summary='修改关键字')
def update_keywordStrings(keyword: KeywordUpdate, session: SessionDep):
    keyword_db = session.get(Keyword, keyword.id)
    if not keyword_db:
        raise HTTPException(status_code=404, detail="keyword not found")
    keyword_data = keyword.model_dump(exclude_unset=True)
    keyword_db.sqlmodel_update(keyword_data)
    session.add(keyword_db)
    session.commit()
    session.refresh(keyword_db)
    processed_item = {
        "id": keyword_db.id,
        "name": keyword_db.name,
        "keywords": json.loads(keyword_db.keywords),  # 将 keywords 字符串转换为列表
        "isActive": keyword_db.is_active,  # 将 is_active 映射为 isActive
        "prompts": keyword_db.prompts
    }
    return processed_item


@router.delete("/delete_keywordStrings/", summary='删除关键字')
def delete_keywordStrings(keyword_id: str, session: SessionDep):
    keyword = session.get(Keyword, keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="not found")
    session.delete(keyword)
    session.commit()
    return {"ok": True}

@router.get('/active_keywordStrings', summary='激活关键字')
def active_keywordStrings(keyword_id: str, session: SessionDep):
    keyword = session.get(Keyword, keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="not found")
    # 获取所有关键词
    keywords_db = session.exec(select(Keyword)).all()
    # 批量设置状态
    for k in keywords_db:
        k.is_active = (k.id == keyword_id)
        session.add(k)
    session.commit()
    keywords_db = session.exec(select(Keyword)).all()
    processed_data = []
    for item in keywords_db:
        processed_item = {
            "id": item.id,
            "name": item.name,
            "keywords": json.loads(item.keywords),  # 将 keywords 字符串转换为列表
            "isActive": item.is_active  # 将 is_active 映射为 isActive
        }
        processed_data.append(processed_item)
    return processed_data


@router.get("/red_book/status", summary="获取当前状态")
def red_book_status(red_book_dep: RedBookDep):
    setup_browser = red_book_dep.driver is not None
    try:
        if setup_browser:
            red_book_dep.driver.title
    except WebDriverException:
        setup_browser = False
    job_running = red_book_dep.is_running is not False
    really_do = red_book_dep.reallyDo
    return {
        "setup_browser": setup_browser,
        "job_running": job_running,
        "really_do": really_do
    }


@router.get("/red_book/", summary="管理小红书任务")
def read_book_login(session: SessionDep, red_book_dep: RedBookDep, action: str):
    if action == "start":
        red_book_dep.active_job = True
    elif action == "stop":
        red_book_dep.active_job = False
    return "ok"


@router.get("/red_book/login/", summary="登录小红书")
def read_book_login(session: SessionDep, red_book_dep: RedBookDep, ai: AIDep, sse: SSEDep):
    red_book_dep.start_browser(session)

    def run_in_background():
        red_book_dep.run(ai, session, sse)
        session.close()
    thread = threading.Thread(target=run_in_background)
    thread.start()
    return "ok"


@router.get("/red_book/shutdown/", summary="关闭小红书")
def read_book_login(session: SessionDep, red_book_dep: RedBookDep):
    red_book_dep.stop_browser()
    return "ok"

@router.patch("/red_book/really_do_toggle", summary="切换是否进行点赞, 收藏, ai评论")
def really_do_toggle(red_book_dep: RedBookDep):
    red_book_dep.reallyDo =  not red_book_dep.reallyDo
    return red_book_dep.reallyDo