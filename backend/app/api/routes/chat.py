from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import StreamingResponse
from app.api.deps import AIDep, SessionDep, SSEDep
from app.models import DialogueMessage, DialogueMessageCreate, DialogueSession, XHSHistory
from sqlmodel import select

router = APIRouter(prefix="/chat", tags=["chat"])


# @router.post("/create_message/", )
# def create_message(message: DialogueMessageCreate, ai: AIDep, session: SessionDep):
#     db_message = DialogueMessage.model_validate(message)
#     session.add(db_message)
#     session.commit()
#     session.refresh(db_message)
#     ai_content = ai.chat(message.content)
#     ai_message = DialogueMessageCreate(
#         id=uuid.uuid4().__str__(),
#         session_id=message.session_id,
#         content=ai_content,
#     )
#     ai_message = DialogueMessage.model_validate(ai_message)
#     session.add(ai_message)
#     session.commit()
#     session.refresh(ai_message)
#     return ai_content


@router.get('/broadcast/', summary="广播消息")
async def broadcast(request: Request, sse: SSEDep,):
    return StreamingResponse(
        sse.add_connection('broadcast', request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/chat_stream/", summary="创建新会话")
async def chat_stream(request: Request, sse: SSEDep, session_id: str, keywordStringId: str, session: SessionDep):
    dialog_session_db = DialogueSession.model_validate(DialogueSession(
        id = session_id,
        keyword_id = keywordStringId
    ))
    session.add(dialog_session_db)
    session.commit()
    session.refresh(dialog_session_db)
    return StreamingResponse(
        sse.add_connection(session_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/chat_stream/", summary="流式对话")
async def chat_stream(request: Request, sse: SSEDep, ai: AIDep, session: SessionDep, message: DialogueMessageCreate):
    if message.content.strip() == '':
        return "OK"
    db_message = DialogueMessage.model_validate(message)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    dialogue_session = session.get(DialogueSession, message.session_id)
    spider_history: list[XHSHistory] = session.exec(select(XHSHistory).where(XHSHistory.keyword_id == dialogue_session.keyword_id))
    await ai.chat_reply(db_message, spider_history, sse, request)
    # TODO 保存ai生成的回答入库, 保存上下文
    return db_message
