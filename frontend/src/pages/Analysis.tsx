import React from 'react';
import Layout from '@/components/Layout';
import AIDialogue from '@/components/AIDialogue';

const Analysis: React.FC = () => {
  return (
    <Layout>
      <div className="space-y-8">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold">AI 对话分析</h2>
          <p className="text-muted-foreground">
            基于收集的关键词内容与 AI 进行交互式对话
          </p>
        </div>

        <div className="h-[calc(100vh-300px)]">
          <AIDialogue />
        </div>
      </div>
    </Layout>
  );
};

export default Analysis;