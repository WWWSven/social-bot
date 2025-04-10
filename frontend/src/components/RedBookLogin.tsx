import { useEffect, useState } from "react";
import {Card, CardContent, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import { Button } from "@/components/ui/button.tsx";
import { toast } from "sonner";
import {useSettingContext} from "@/context/SettingContext.tsx";
import {shutdownRedBookApi, startRedBookApi, reallyDoToggleApi} from "@/lib/api.ts";
import {Switch} from "@/components/ui/switch.tsx";
import {TooltipProvider, TooltipContent, TooltipTrigger, Tooltip} from "@/components/ui/tooltip.tsx";

const RedBookLogin = () => {
  const {redBookStatus, fetchRedBookStatus} = useSettingContext()
  const [loading, setLoading] = useState(false);

  const toggleBrowser = async () => {
    if (redBookStatus.job_running){
      toast.warning('先关闭定时器')
      return
    }
    setLoading(true);
    if (redBookStatus?.setup_browser){
      shutdownRedBookApi()
        .then(() => {
          toast.success("操作成功");
          fetchRedBookStatus(); // 操作后刷新状态
        }).catch(() => {
          console.error("操作失败");
          toast.error("操作失败");
        }).finally(()=>{
          setLoading(false);
        })
    }else {
      startRedBookApi()
        .then(() => {
          toast.success("操作成功");
          fetchRedBookStatus(); // 操作后刷新状态
        }).catch(() => {
          console.error("操作失败");
          toast.error("操作失败");
        }).finally(()=>{
          setLoading(false);
        })
    }
  };

  useEffect(() => {
    fetchRedBookStatus();
    const interval = setInterval(fetchRedBookStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>小红书</CardTitle>
          {redBookStatus && (
            <div className="text-sm text-muted-foreground space-y-1 mt-2">
              <div>浏览器: {redBookStatus.setup_browser ? "启动" : "未启动"}</div>
              <div>定时任务: {redBookStatus.job_running ? "启动" : "未启动"}</div>
              <div className="flex gap-2">
                <div>智能三连: {redBookStatus.really_do ? "启动": "未启动"}</div>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div>
                        <Switch
                          checked={redBookStatus.really_do}
                          onCheckedChange={()=>{reallyDoToggleApi()}}
                        />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>点击切换</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {redBookStatus && (
            <>
              <Button onClick={toggleBrowser} disabled={loading} variant={redBookStatus.setup_browser?"destructive":"default"}>
                {redBookStatus.setup_browser ? "关闭小红书" : "启动小红书"}
              </Button>
            </>
          )}
        </CardContent>
        <CardFooter>
          <div className="p-4 bg-amber-50 text-amber-800 rounded-md">
            1. 点击后等待浏览器启动 <br/>
            2. 智能三连是: 点赞, 评论(ai), 收藏 <br/>
            3. 当你登录过后(会在本地保存cookie), 再次启动小红书, 等待几秒, 让他自动登录
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};

export default RedBookLogin;
