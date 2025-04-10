from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, Integer, Text


# 基础设置
class SettingsBase(SQLModel):
    value: str = Field(sa_column=Column(Text))


class Settings(SettingsBase, table=True):
    id: str = Field(index=True, primary_key=True)


class SettingsUpdate(SettingsBase):
    value: str = Field(sa_column=Column(Text))



# 关键词
class KeywordBase(SQLModel):
    id: str = Field(index=True, primary_key=True)
    name: str = Field(index=True, max_length=100)
    keywords: str
    prompts: str = Field(sa_column=Column(Text))


class Keyword(KeywordBase, table=True):
    is_active: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True)),
    )
    last_collected_at: datetime | None = None


class KeywordCreate(KeywordBase):
    id: str
    name: str
    keywords: str
    prompts: str

class KeywordUpdate(KeywordBase):
    id: str
    name: str
    keywords: str
    prompts: str

class KeywordPublic(KeywordBase):
    id: str
    name: str
    keywords: str
    is_active: bool
    created_at: datetime
    last_collected_at: datetime | None
    prompts: str

# 对话
class DialogueSession(SQLModel, table=True):
    id: str = Field(index=True, primary_key=True)
    keyword_id: str = Field(index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=datetime.now
    )


# 对话消息
class DialogueMessageBase(SQLModel):
    session_id: str = Field(index=True)
    content: str
    sender: str


class DialogueMessage(DialogueMessageBase, table=True):
    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, autoincrement=True, primary_key=True)
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True)),
    )


class DialogueMessageCreate(DialogueMessageBase):
    sender: str = 'user'

# 爬取记录
class XHSHistory(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, autoincrement=True, primary_key=True)
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True)),
    )
    keyword_id: str
    detail: str = Field(sa_column=Column(Text))
