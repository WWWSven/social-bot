import React, { useState, useEffect } from 'react';
import { useKeywordContext } from '@/context/KeywordContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Timer as TimerIcon } from "lucide-react"
import { toast } from 'sonner';
import {useSettingContext} from "@/context/SettingContext.tsx";
import {Skeleton} from "@/components/ui/skeleton.tsx";
import {getIntervalMinutesApi, startRedBookJobApi, stopRedBookJobApi} from "@/lib/api.ts";

const Timer: React.FC = () => {
  const { redBookStatus, fetchRedBookStatus, timerSettings, updateTimerSettings } = useSettingContext()
  const { keywordStrings, toggleKeywordStringActive } = useKeywordContext();
  const [intervalMinutes, setIntervalMinutes] = useState<number>(timerSettings.intervalMinutes);

  useEffect(() => {
    getIntervalMinutesApi()
      .then(value => {
        updateTimerSettings(value.data)
      })
    fetchRedBookStatus();
    const interval = setInterval(fetchRedBookStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setIntervalMinutes(timerSettings.intervalMinutes);
  }, [timerSettings.intervalMinutes]);

  const handleStartTimer = () => {
    if (!redBookStatus.setup_browser){
      toast.warning('请先在平台管理中启动')
      return;
    }
    if (keywordStrings.filter(ks => ks.isActive).length === 0) {
      toast.error('请先激活至少一个关键词字符串');
      return;
    }
    startRedBookJobApi()
      .then(() => {
        toast.success('定时器启动成功')
      }).catch(() => {
        toast.error('定时器启动失败')
      }).finally(()=>{
        setTimeout(()=>{
          fetchRedBookStatus()
        }, 1000)
      })
  };

  const handleStopTimer = () => {
    stopRedBookJobApi()
      .then(() => toast.success('定时器停止成功'))
      .catch(() => toast.error('定时器停止失败'))
  };

  const handleIntervalChange = (value: number[]) => {
    const newInterval = value[0];
    setIntervalMinutes(newInterval);
  };

  const handleIntervalCommit = () => {
    updateTimerSettings({ intervalMinutes: intervalMinutes });
    toast.info(`定时器间隔已更新为 ${intervalMinutes} 秒`);
  };

  const activeKeywordStrings = keywordStrings.filter(ks => ks.isActive);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>定时器设置</CardTitle>
        <CardDescription>设置内容抓取定时器</CardDescription>
      </CardHeader>
      <CardContent>
        {
          intervalMinutes < 0
            ?
            <div className="space-y-3">
              <Skeleton className="w-full h-10" />
              <Skeleton className="w-[550px] h-10" />
              <Skeleton className="w-[550px] h-10" />
            </div>
            :
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <TimerIcon className="h-4 w-4"/>
                <Label htmlFor="interval">内容抓取间隔</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Slider
                  id="interval"
                  defaultValue={[intervalMinutes]}
                  max={60}
                  min={5}
                  step={5}
                  onValueChange={handleIntervalChange}
                  onValueCommit={handleIntervalCommit}
                  className="w-3/4"
                />
                <span className="w-1/4 text-right">{intervalMinutes} 秒</span>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">
                  定时器将每 {intervalMinutes} 秒 (大约, 加入了随机秒数) 抓取一次
                </p>
              </div>
              <div>
                <h3 className="text-md font-semibold">激活的关键词字符串</h3>
                {keywordStrings.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    您还没有创建任何关键词字符串。
                  </p>
                ) : (
                  <ul className="list-none pl-0 space-y-2">
                    {keywordStrings.map(keywordString => (
                      <li key={keywordString.id} className="flex items-center justify-between">
                        <Label htmlFor={`keyword-${keywordString.id}`}>{keywordString.name}</Label>
                        <Switch
                          id={`keyword-${keywordString.id}`}
                          checked={keywordString.isActive}
                          onCheckedChange={(checked) => {
                            if (redBookStatus.job_running) {
                              toast.warning('需要先停止计时器')
                              return
                            }
                            toggleKeywordStringActive(keywordString.id);
                            toast.info(`关键词字符串 "${keywordString.name}" 已${checked ? '激活' : '禁用'}`);
                          }}
                        />
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="flex justify-end space-x-2">
                {redBookStatus.job_running ? (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">停止定时器</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>确定停止定时器？</AlertDialogTitle>
                        <AlertDialogDescription>
                          停止定时器后，将不再自动抓取内容。
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>取消</AlertDialogCancel>
                        <AlertDialogAction onClick={handleStopTimer}>停止</AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                ) : (
                  <Button
                    onClick={handleStartTimer}
                    variant="default"
                    className="bg-green-500 hover:bg-green-600 text-white"
                    disabled={activeKeywordStrings.length === 0}
                  >
                    启动定时器
                  </Button>
                )}
              </div>
              <div className="p-4 bg-amber-50 text-amber-800 rounded-md">
                1. 点击启动后需等待数秒 <br/>
                2. 不是严格按照设置的秒数延迟的, 这个控制基础的延迟时间
              </div>
              {activeKeywordStrings.length === 0 && (
                <div className="p-4 bg-amber-50 text-red-700 rounded-md">
                  暂只支持同时激活一个, 激活一个关闭其余的
                </div>
              )}
            </div>
        }
      </CardContent>
    </Card>
  );
};

export default Timer;