import asyncio
import json
from typing import Literal
from openai import OpenAI
import os
import time
from fastapi import Request, HTTPException
from pydantic import BaseModel
from app.core.SSE import SSEManager
from app.models import DialogueMessage, XHSHistory, Keyword


class AiStructuredOutput(BaseModel):
    status: Literal["success", "fail"]
    is_like: bool
    is_fav: bool
    is_comment: bool
    comment: str
    reason: str

class AI:

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("AI_BASE_URL"),
            api_key=os.getenv("AI_API_KEY"),
        )

    def chat(self, detail, keyword: Keyword, retry=True) -> AiStructuredOutput | None:
        # 自定义人设
        system_prompt = f'''
        {keyword.prompts if keyword.prompts else ''}
        
        我关心的{keyword.name}是: {keyword.keywords} 这样的, 根据笔记的标题, 内容等信息给出是否符合给出是否进行点赞/收藏/评论的建议

        用户提供的笔记信息格式如下：
        {{
            "title": "<帖子标题>",
            "post": "<帖子内容，可能无内容,如果是一段文本前有 # 说明是话题标签>",
            "author": "<作者昵称>",
            "like_count": <点赞数>,
            "comment_count": <评论数>,
            "fav_count": <收藏数>,
            "channel": "<频道名>"
        }}
        '''

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": detail}
        ]

        try:
            completion = self.client.beta.chat.completions.parse(
                model=os.getenv("AI_MODEL"),
                messages=messages,
                temperature=0.3,
                response_format=AiStructuredOutput,
            )
        except Exception as e:
            if retry:
                print(e)
                print("请求失败，等待10 秒后重试中...")
                time.sleep(10)  # 等待 10 秒
                print("重试中...")
                return self.chat(detail, keyword, retry=False)
            else:
                return  AiStructuredOutput(
                    status="fail",
                    reason="请求超时",
                    is_like=False,
                    is_fav=False,
                    is_comment=False,
                    comment="",
                )
        result = completion.choices[0].message.parsed
        return result

    @staticmethod
    def _format_sse(id: int, data: str, event: str = "message") -> str:
        return f"id: {id}\nevent: {event}\ndata: {data}\n\n"

    async def chat_reply(self, dialogue_msg: DialogueMessage, spider_history: list[XHSHistory], sse: SSEManager, request: Request, retry=True):
        session_id = dialogue_msg.session_id
        system_prompt = '''
            根据下面的文章信息直接给出结论, 不要说一些含糊不定的话, 当你觉得文章的内容需要注意的时候不要提醒我
            文章的信息格式如下：
            {
                "title": "<帖子标题>",
                "post": "<帖子内容，可能无内容,如果是一段文本前有 # 说明是话题标签>",
                "author": "<作者昵称>",
                "like_count": <点赞数>,
                "comment_count": <评论数>,
                "fav_count": <收藏数>,
                "channel": "<频道名>"
            }
            '''

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        for history_item in spider_history:
            detail = history_item.detail
            for item in json.loads(detail):
                if item.get("type") == "text":
                    text_json_str = item.get("text", "")
                    try:
                        messages.append({"role": "user", "content": text_json_str})
                    except json.JSONDecodeError:
                        print("JSON 解码失败")

        messages.append({"role": "user", "content": dialogue_msg.content})

        # print(f'给ai发的消息: {jsonable_encoder(messages)}')

        try:
            stream = self.client.chat.completions.create(
                model=os.getenv("AI_MODEL"),
                messages=messages,
                temperature=0.1,
                response_format={"type": "text"},
                stream=True
            )
            for chunk in stream:
                if await request.is_disconnected():
                    break
                chunk_content = chunk.choices[0].delta.content
                if chunk_content:
                    sse_data = self._format_sse(dialogue_msg.id, json.dumps(
                        {
                            "id": dialogue_msg.id,
                            "content": chunk_content,
                            "timestamp": dialogue_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "session_id": dialogue_msg.session_id,
                            "sender": 'ai'
                        }
                    ))
                    await sse.send_message(sse_data, session_id)
                    reason = chunk.choices[0].finish_reason
                    if reason == 'stop':
                        await sse.send_message(
                            self._format_sse(event='stop', data='', id=dialogue_msg.id),
                            session_id
                        )
        except Exception as e:
            if retry:
                print(f"请求失败，重试中... 错误: {str(e)}")
                await asyncio.sleep(10)
                await self.chat_reply(dialogue_msg, session_id, spider_history, sse, request, retry=False)
            else:
                error_msg = self._format_sse(
                    dialogue_msg.id,
                    json.dumps({"error": str(e)}),
                    event="error"
                )
                await sse.send_message(error_msg, session_id)
                raise HTTPException(500, detail="AI 服务异常")


    def chat_stream(self, detail, retry=True):
        # 自定义人设
        system_prompt = '''
            请用中文详尽总结以下对话内容，按照以下步骤，每一步分别打印结果：
            1. 尽可能列出他们讨论的所有话题，不要遗漏
            2. 检查第一步列出的话题，补充缺失的重要话题
            3. 基于每个话题用bullet points列出要点
            4. 严格的以话题为章节，不要遗漏，基于每个话题和下面的要点，用1-3个自然段落总结每个话题的内容，总结每个话题时不要用bullet points，整体效果像是一篇科普文章
            以下是要总结的内容：
            过去的美好一直在，溪溪有十几万ee的爱守护着，快乐，温暖，幸福，会永远包围着她，到她上幼儿园，上小学，上大学，到她10岁，18岁，28岁……一辈子
            时间变得好快，大二开始关注溪溪，到现在居然三年了，我也顺利毕业参加工作了。溪溪要健康快乐成长哦，ee会一直关注你的
            '''

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": detail}
        ]

        try:
            completion = self.client.chat.completions.create(
                model=os.getenv("AI_MODEL"),
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            if retry:
                print(e)
                print("请求失败，等待10 秒后重试中...")
                time.sleep(10)  # 等待 10 秒
                print("重试中...")
                return self.chat_stream(detail, retry=False)
            else:
                return '{"status": "fail", "message": "请求超时"}'
        result = completion.choices[0].message.content
        return result
