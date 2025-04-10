import json

from sqlmodel import Session
from app.api.deps import engine, create_db_and_tables
from app.models import Settings, Keyword


def create_settings():
    with Session(engine) as session:
        global_setting = Settings(
            id="global_interval",
            value="5"
        )
        session.add(global_setting)
        session.commit()
        session.refresh(global_setting)

        print("导入: settings")

def create_keyword():
    default_prompts = """
        你是一个社交媒体机器人，但是你需要思考怎么伪装才能让别人发现不了你是机器人。
        你的人设是"成年男性，年轻运动乐观积极，高素养高情商，擅长赞美年轻成年女性，发言需要简单成熟"。
        你只对女生艺术照或女生自拍照的帖子进行操作，请根据用户提供的图片、内容进行综合判断，考虑标准优先于图片，软色情擦边也允许操作，请主要甄别出AI照片，孕妇照，可能含广告以及其他不符合要求的帖子并不操作；
        你将收到用户提供的关于帖子首张图和帖子信息，可能只有标题没有内容，也可能图片不是本人，请根据所提供的信息思考作者的身份和立场和发表的该帖子的用意再做出回应。
        基于人设做出你的操作，你可以点赞，收藏，评论。
        符合要求条件的内容可以点赞。
        符合软色情内容的可以收藏。
        动画内容不允许点赞，收藏，评论。
        评论只能在有内容的帖子才能评论(标签不算内容)，评论内容需要是赞美，但不要过于夸张，如果有和内容相关的合适互动的问题可以在最后提出问题与作者互动（如果没合适可以不提问），纯文字，不能携带emoji，不需要标点符号结尾，不能超过50个字。
        评论示例：
        - 真好看，太漂亮啦
        - 看起来太有气质了，这衣服哪买的
        - 哇，好可爱，好漂亮，求发夹链接
        - 穿搭的真好，发型也很适合你，求衣服链接
    """
    with Session(engine) as session:
        default_keyword = Keyword(
            id = "0f904720-1765-4ff9-ffff-f9360b08781a",
            name = "美女",
            keywords = json.dumps(["清凉", "ootd", "纯欲"], ensure_ascii=False),
            prompts = default_prompts,
            is_active = True
        )
        session.add(default_keyword)
        session.commit()
        session.refresh(default_keyword)

        print("导入: keyword")

def main():
    create_db_and_tables()
    create_settings()
    create_keyword()


if __name__ == "__main__":
    main()