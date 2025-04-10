import axios from "axios";
import {DialogueMessage, KeywordString} from "@/types";
import {TimerSettings} from "@/context/SettingContext.tsx";

const instance = axios.create({
  baseURL: 'http://127.0.0.1:8000/',
});

// 获取关键字集合
function getKeywordStringsApi() {
  return instance.get<KeywordString[]>('/setting/keywordStrings/')
}

// 添加关键字
function addKeywordStringsApi(name: string, keywords: string[], prompts: string) {
  return instance.post('/setting/add_keywordStrings/', {
    id: crypto.randomUUID(),
    name: name,
    keywords: JSON.stringify(keywords),
    prompts: prompts
  })
}

// 删除关键字
function deleteKeywordStringsApi(keywordId: string) {
  return instance.delete(`/setting/delete_keywordStrings/?keyword_id=${keywordId}`)
}

// 更新关键字
function updateKeywordStringsApi(id: string, data: Partial<KeywordString>) {
  return instance.patch<KeywordString>('/setting/update_keywordStrings/', {
      "id": id,
      "name": data.name,
      "keywords": JSON.stringify(data.keywords),
      "prompts": data.prompts
  })
}

// 激活关键字
function activeKeywordStringApi(keyword_id: string) {
  return instance.get(`/setting/active_keywordStrings?keyword_id=${keyword_id}`)
}


// 提交用户聊天消息
function addChatMessageApi(sessionId: string, message: Omit<DialogueMessage, 'id' | 'timestamp'>) {
  return instance.post('/chat/chat_stream/', {
    session_id: sessionId,
    content: message.content,
    sender: message.sender
  })
}

// 关闭小红书
function shutdownRedBookApi() {
  return instance.get('/setting/red_book/shutdown/')
}

// 启动小红书
function startRedBookApi() {
  return instance.get('/setting/red_book/login/')
}

// 任务间隔
function getIntervalMinutesApi() {
  return instance.get('/setting/intervalMinutes/')
}

// 更新任务间隔时间
function updateIntervalMinutesApi(settings: Partial<TimerSettings>) {
  return instance.patch('/setting/update_intervalMinutes/', {
    value: settings.intervalMinutes+""
  })
}

// 启动定时任务
function startRedBookJobApi() {
  return instance.get('/setting/red_book/?action=start')
}

// 停止定时任务
function stopRedBookJobApi() {
  return instance.get('/setting/red_book/?action=stop')
}

// 全局小红书任务状态
function getRedBookStatusApi() {
  return instance.get('/setting/red_book/status')
}

// 切换智能三连
function reallyDoToggleApi() {
  return instance.patch('/setting/red_book/really_do_toggle')
}

export {
  getKeywordStringsApi,
  addKeywordStringsApi,
  deleteKeywordStringsApi,
  updateKeywordStringsApi,
  activeKeywordStringApi,
  addChatMessageApi,
  shutdownRedBookApi,
  startRedBookApi,
  getIntervalMinutesApi,
  updateIntervalMinutesApi,
  startRedBookJobApi,
  stopRedBookJobApi,
  getRedBookStatusApi,
  reallyDoToggleApi
}