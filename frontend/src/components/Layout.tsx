import React, {useEffect, useState} from 'react';
import { Link, useLocation } from 'react-router';
import { Button } from '@/components/ui/button';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  const [message, setMessage] = useState<string | null>("欢迎━(*｀∀´*)ノ亻!");

  useEffect(() => {
    const eventSource = new EventSource(
      `http://127.0.0.1:8000/chat/broadcast`
    );
    eventSource.addEventListener('message', (event) => {
      console.log(message)
      setMessage(event.data || '未知消息');
    });
    return ()=>eventSource.close()
  }, []);


  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b py-4 px-6 bg-white shadow-sm">
        <div className="container mx-auto flex justify-between items-center">
          <h2 className="text-2xl font-bold text-blue-600">
            {message && (
              <div className="animate-marquee whitespace-nowrap overflow-hidden px-5 text-ellipsis">
                {message}
              </div>
            )}
          </h2>
          <nav className="flex gap-4">
            <Link to="/platform">
              <Button variant={location.pathname === '/platform' ? 'default' : 'outline'}>
                平台管理
              </Button>
            </Link>
            <Link to="/">
              <Button variant={location.pathname === '/' ? 'default' : 'outline'}>
                关键词管理
              </Button>
            </Link>
            <Link to="/analysis">
              <Button variant={location.pathname.startsWith('/analysis') ? 'default' : 'outline'}>
                AI 对话分析
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 container mx-auto py-8 px-4">
        {children}
      </main>

      <footer className="border-t py-4 px-6 bg-white text-center text-sm text-gray-500">
        <div className="container mx-auto">
          Test Demo &copy; {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  );
};

export default Layout;
