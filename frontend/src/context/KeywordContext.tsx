import React, { createContext, useState, useContext, useEffect } from 'react';
import { KeywordString, DialogueSession, DialogueMessage } from '@/types';
import {toast} from "sonner";
import {
  activeKeywordStringApi,
  addChatMessageApi,
  addKeywordStringsApi,
  deleteKeywordStringsApi,
  getKeywordStringsApi,
  updateKeywordStringsApi
} from "@/lib/api.ts";

interface KeywordContextType {
  keywordStrings: KeywordString[];
  dialogueSessions: DialogueSession[];
  addKeywordString: (name: string, keywords: string[], prompts: string) => void;
  updateKeywordString: (id: string, data: Partial<KeywordString>) => void;
  removeKeywordString: (id: string) => void;
  toggleKeywordStringActive: (id: string) => void;
  addCollectedContent: (keywordStringId: string, content: string) => void;
  addDialogueSession: (keywordStringId: string) => DialogueSession;
  addDialogueMessage: (sessionId: string, message: Omit<DialogueMessage, 'id' | 'timestamp'>) => void;
  getCurrentDialogueSession: (sessionId: string) => DialogueSession | undefined;
}

const KeywordContext = createContext<KeywordContextType | undefined>(undefined);

export const KeywordProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [keywordStrings, setKeywordStrings] = useState<KeywordString[]>([]);

  const [dialogueSessions, setDialogueSessions] = useState<DialogueSession[]>(() => {
    const saved = localStorage.getItem('dialogueSessions');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    getKeywordStringsApi()
      .then(value => {
        setKeywordStrings(value.data as KeywordString[]);
      }).catch(reason => {
        console.log('获取关键字集合失败', reason)
      })
  }, []);


  useEffect(() => {
    localStorage.setItem('dialogueSessions', JSON.stringify(dialogueSessions));
  }, [dialogueSessions]);

  const addKeywordString = (name: string, keywords: string[], prompts: string) => {
    addKeywordStringsApi(name, keywords, prompts)
      .then(value => {
        setKeywordStrings([...keywordStrings, value.data]);
      }).catch(reason => {
        console.log('添加关键字失败', reason)
      })
  };

  const updateKeywordString = (id: string, data: Partial<KeywordString>) => {
    updateKeywordStringsApi(id, data)
      .then(value => {
        setKeywordStrings(keywordStrings.map(ks =>
          ks.id === id ? { ...ks, ...value.data } : ks
        ));
      }).catch(reason => {
      console.log('更新失败', reason)
    })
  };

  const removeKeywordString = (id: string) => {
    deleteKeywordStringsApi(id)
      .then(value => {
        console.log('删除成功', value)
        setKeywordStrings(keywordStrings.filter(ks => ks.id !== id));
      }).catch(reason => {
        console.log('删除失败', reason)
      })
  };

  const toggleKeywordStringActive = (id: string) => {
    activeKeywordStringApi(id)
      .then(value => {
        setKeywordStrings(value.data);
      }).catch(console.log)
  };

  const addCollectedContent = (keywordStringId: string, content: string) => {
    setKeywordStrings(keywordStrings.map(ks =>
      ks.id === keywordStringId
        ? {
          ...ks,
          collectedContent: [...(ks.collectedContent || []), content],
          lastCollectedAt: new Date()
        }
        : ks
    ));
  };

  const addDialogueSession = (keywordStringId: string) => {
    const newSession: DialogueSession = {
      id: crypto.randomUUID(),
      keywordStringId,
      messages: [],
      createdAt: new Date()
    };
    const eventSource = new EventSource(
      `http://127.0.0.1:8000/chat/chat_stream/?session_id=${newSession.id}&keywordStringId=${keywordStringId}`
    );
    eventSource.addEventListener('message', (message) => {
      setDialogueSessions(prev => {
        return prev.map(session => {
          if (session.id === newSession.id) {
            const data = JSON.parse(message.data)
            const exists = session.messages.find(v=>v.id == data.id)
            let newMessages: DialogueMessage[]
            if (exists){
              newMessages = session.messages.map(v=>{
                if (v.id == data.id){
                  return {...v, content: v.content + data.content}
                }else {
                  return v;
                }
              })
            }else {
              newMessages = session.messages ? [...session.messages, data] : [data]
            }
            const newDialogueSession: DialogueSession = {
              ...session,
              messages: newMessages
            }
            return newDialogueSession
          }
          return session;
        });
      });
    });
    eventSource.addEventListener('open', () => {
      toast.success(`连接成功`)
    })
    eventSource.addEventListener('error', () => {
      toast.warning(`连接中断，正在尝试重新连接...`);
    });


    setDialogueSessions([...dialogueSessions, newSession]);
    return newSession;
  };

  const addDialogueMessage = (sessionId: string, message: Omit<DialogueMessage, 'id' | 'timestamp'>) => {
    setDialogueSessions(prev => {
      return prev.map(session => {
        if (session.id === sessionId) {
          return {
            ...session,
            messages: [
              ...session.messages,
              {
                'id': crypto.randomUUID(),
                'sender': 'user',
                'content': message.content,
                'timestamp': new Date(),
              }
            ]
          };
        }
        return session;
      });
    });
    addChatMessageApi(sessionId, {content: message.content, sender: message.sender})
  };

  const getCurrentDialogueSession = (sessionId: string) => {
    return dialogueSessions.find(session => session.id === sessionId);
  };

  return (
    <KeywordContext.Provider value={{
      keywordStrings,
      dialogueSessions,
      addKeywordString,
      updateKeywordString,
      removeKeywordString,
      toggleKeywordStringActive,
      addCollectedContent,
      addDialogueSession,
      addDialogueMessage,
      getCurrentDialogueSession
    }}>
      {children}
    </KeywordContext.Provider>
  );
};

export const useKeywordContext = () => {
  const context = useContext(KeywordContext);
  if (context === undefined) {
    throw new Error('useKeywordContext must be used within a KeywordProvider');
  }
  return context;
};
