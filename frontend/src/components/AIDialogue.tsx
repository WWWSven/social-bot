import React, { useState, useEffect } from 'react';
import { useKeywordContext } from '@/context/KeywordContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { toast } from 'sonner';
import { useNavigate, useParams } from 'react-router';
import { KeywordString} from '@/types';

import SessionSelector from './dialogue/SessionSelector';
import MessageList from './dialogue/MessageList';
import InputArea from './dialogue/InputArea';
import SessionHeader from './dialogue/SessionHeader';

const AIDialogue: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();

  const {
    keywordStrings,
    dialogueSessions,
    addDialogueSession,
    addDialogueMessage,
    getCurrentDialogueSession
  } = useKeywordContext();

  const [selectedKeywordStringId, setSelectedKeywordStringId] = useState<string>('');
  const [currentSession, setCurrentSession] = useState(sessionId ? getCurrentDialogueSession(sessionId) : undefined);

  useEffect(() => {
    if (sessionId) {
      const session = getCurrentDialogueSession(sessionId);
      setCurrentSession(session);

      if (session) {
        const keywordString = keywordStrings.find(ks => ks.id === session.keywordStringId);
        if (keywordString) {
          setSelectedKeywordStringId(keywordString.id);
        }
      }
    }
  }, [sessionId, dialogueSessions, keywordStrings, getCurrentDialogueSession]);

  useEffect(() => {
    if (!currentSession) return
    navigate(`/analysis/${currentSession.id}`);
  }, [currentSession?.id]);

  useEffect(() => {
    setCurrentSession((prev) => {
      return prev ? getCurrentDialogueSession(prev.id) : undefined
    })
  }, [dialogueSessions]);

  const getSelectedKeywordString = (): KeywordString | undefined => {
    return keywordStrings.find(ks => ks.id === selectedKeywordStringId);
  };

  const handleKeywordStringChange = (value: string) => {
    setSelectedKeywordStringId(value);
  };

  const handleStartNewSession = () => {
    if (!selectedKeywordStringId) {
      toast.error('请先选择一个关键词字符串');
      return;
    }

    const keywordString = getSelectedKeywordString();
    if (!keywordString) {
      toast.error('无效的关键词字符串');
      return;
    }

    if (keywordString.collectedContent?.length === 0) {
      toast.warning('该关键词字符串还未收集任何内容');
      return;
    }

    const newSession = addDialogueSession(selectedKeywordStringId);

    // addDialogueMessage(newSession.id, {
    //   sender: 'ai',
    //   content: `您好！我已经准备好分析关于 "${keywordString.name}" 的收集内容，该内容包含关键词：${keywordString.keywords.join('、')}。目前已收集 ${keywordString.collectedContent.length} 条内容。请问您想了解什么？`
    // });
    setCurrentSession(newSession);
  };

  const handleSendMessage = (message: string) => {
    if (!currentSession) {
      toast.error('请先创建会话');
      return;
    }

    addDialogueMessage(currentSession.id, {
      sender: 'user',
      content: message
    });
  };

  return (
    <div className="h-full flex flex-col">
      <Card className="flex flex-col h-full gap-1">
        <CardHeader>
          {!currentSession ? <>
            <CardTitle>AI 对话分析</CardTitle>
            <CardDescription>
              选择关键词字符串，开始与 AI 进行对话分析
            </CardDescription>
          </>
          :
          <SessionHeader
            sessionName={keywordStrings.find(ks => ks.id === currentSession.keywordStringId)?.name || '对话'}
            createdAt={currentSession.createdAt}
            onNewSession={() => setCurrentSession(undefined)}
          />
          }

        </CardHeader>

        <CardContent className="flex-1 overflow-hidden flex flex-col">
          {!currentSession ? (
            <SessionSelector
              keywordStrings={keywordStrings}
              selectedKeywordStringId={selectedKeywordStringId}
              onKeywordStringChange={handleKeywordStringChange}
              onStartNewSession={handleStartNewSession}
            />
          ) : (
              <MessageList messages={currentSession.messages} />
          )}
        </CardContent>

        {currentSession && (
          <CardFooter className="pt-4">
            <InputArea
              onSendMessage={handleSendMessage}
              isProcessing={false}
            />
          </CardFooter>
        )}
      </Card>
    </div>
  );
};

export default AIDialogue;