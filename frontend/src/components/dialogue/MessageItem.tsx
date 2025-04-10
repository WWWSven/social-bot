import React from 'react';
import { Avatar } from '@/components/ui/avatar';
import { Bot, User } from 'lucide-react';
import { DialogueMessage } from '@/types';
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MessageItemProps {
  message: DialogueMessage;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  return (
    <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start gap-2 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
        <Avatar className={message.sender === 'user' ? 'bg-blue-100' : 'bg-gray-100'}>
          {message.sender === 'user' ? (
            <User className="h-5 w-5 text-blue-500" />
          ) : (
            <Bot className="h-5 w-5 text-gray-500" />
          )}
        </Avatar>

        <div className={`rounded-lg p-3 ${message.sender === 'user' ? 'bg-blue-100 text-blue-900' : 'bg-gray-100'}`}>
          <div className="whitespace-pre-wrap text-sm">
            <Markdown  remarkPlugins={[remarkGfm]}>
              {message.content}
            </Markdown>
          </div>
          <div className="mt-1 text-[10px] text-muted-foreground text-right">
            {new Date(message.timestamp).toLocaleTimeString('zh-CN', { timeZone: 'Asia/Shanghai'})}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageItem;
