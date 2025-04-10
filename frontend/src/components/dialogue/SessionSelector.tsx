import React from 'react';
import { KeywordString } from '@/types';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface SessionSelectorProps {
  keywordStrings: KeywordString[];
  selectedKeywordStringId: string;
  onKeywordStringChange: (value: string) => void;
  onStartNewSession: () => void;
}

const SessionSelector: React.FC<SessionSelectorProps> = ({
   keywordStrings,
   selectedKeywordStringId,
   onKeywordStringChange,
   onStartNewSession
}) => {
  // const availableKeywordStrings = keywordStrings.filter(ks => ks.collectedContent?.length > 0);
  const availableKeywordStrings = keywordStrings
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <label className="text-sm font-medium">选择关键词字符串</label>
        <Select value={selectedKeywordStringId} onValueChange={onKeywordStringChange}>
          <SelectTrigger>
            <SelectValue placeholder="选择要分析的关键词字符串" />
          </SelectTrigger>
          <SelectContent>
            {availableKeywordStrings.map(ks => (
              <SelectItem key={ks.id} value={ks.id}>
                {ks.name} ({ks.collectedContent?.length}条内容)
              </SelectItem>
            ))}
            {availableKeywordStrings.length === 0 && (
              <SelectItem value="empty" disabled>
                暂无可用的关键词字符串
              </SelectItem>
            )}
          </SelectContent>
        </Select>
      </div>

      <Button onClick={onStartNewSession} disabled={!selectedKeywordStringId}>
        开始新的对话
      </Button>

      {keywordStrings.length === 0 && (
        <div className="p-4 bg-amber-50 text-amber-800 rounded-md">
          请先在关键词管理页面创建关键词字符串并收集内容
        </div>
      )}

      {keywordStrings.length > 0 && keywordStrings.every(ks => ks.collectedContent?.length === 0) && (
        <div className="p-4 bg-amber-50 text-amber-800 rounded-md">
          您已创建关键词字符串，但还未收集任何内容。请在关键词管理页面激活关键词字符串并启动定时器收集内容。
        </div>
      )}
    </div>
  );
};

export default SessionSelector;
