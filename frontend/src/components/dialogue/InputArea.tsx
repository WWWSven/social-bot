import React, { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Send } from 'lucide-react';

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  isProcessing: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, isProcessing }) => {
  const [userInput, setUserInput] = useState('分析这些文章, 给出500字输出');

  const handleSendMessage = () => {
    if (!userInput.trim()) return;
    onSendMessage(userInput);
    setUserInput('');
  };

  return (
    <div className="flex w-full space-x-2">
      <Textarea
        placeholder="输入您的问题..."
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
          }
        }}
        className="flex-1"
      />
      <Button onClick={handleSendMessage} disabled={!userInput.trim() || isProcessing}>
        <Send size={18} />
      </Button>
    </div>
  );
};

export default InputArea;
