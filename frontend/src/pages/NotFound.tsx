import { useEffect } from "react";
import {useLocation} from "react-router";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: 用户访问了一个不存在的路由",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-4">不存在的页面</p>
        <a href="/" className="text-blue-500 hover:text-blue-700 underline">
          回到主页
        </a>
      </div>
    </div>
  );
};

export default NotFound;
