import React from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

interface SessionHeaderProps {
  sessionName: string;
  createdAt: Date;
  onNewSession: () => void;
}

const SessionHeader: React.FC<SessionHeaderProps> = ({ sessionName, createdAt, onNewSession }) => {
  return (
    <div className="flex justify-between items-center">
      <div>
        <h3 className="text-lg font-medium">{sessionName}</h3>
        <p className="text-sm text-muted-foreground">
          创建于: {new Date(createdAt).toLocaleString()}
        </p>
      </div>
      <Button variant="outline" size="sm" onClick={onNewSession}>
        <RefreshCw size={16} className="mr-1" /> 新对话
      </Button>
    </div>
  );
};

export default SessionHeader;