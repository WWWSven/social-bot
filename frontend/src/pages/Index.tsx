import React from 'react';
import KeywordManagement from "@/components/KeywordManagement.tsx";
import Layout from "@/components/Layout.tsx";
import Timer from '@/components/Timer';

const Index = () => {
  return (
    <Layout>
      <div className="space-y-8">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold">关键词管理</h2>
          <p className="text-muted-foreground">
            创建并管理关键词字符串，配置定时收集设置
          </p>
        </div>

        <div className="grid gap-8">
          <Timer />
          <KeywordManagement />
        </div>
      </div>
    </Layout>
  );
};

export default Index;
