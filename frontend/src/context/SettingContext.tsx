import React, {createContext, useContext, useState} from "react";
import {toast} from "sonner";
import {getRedBookStatusApi, updateIntervalMinutesApi} from "@/lib/api.ts";

type RedBookStatus = {
  setup_browser: boolean;
  job_running: boolean;
  really_do: boolean
};


export interface TimerSettings {
  intervalMinutes: number;
}

interface SettingContextType {
  redBookStatus: RedBookStatus;
  fetchRedBookStatus: () => void;
  timerSettings: TimerSettings ;
  updateTimerSettings: (settings: Partial<TimerSettings>) => void;
}

const SettingContext = createContext<SettingContextType | undefined>(undefined);

export const SettingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [redBookStatus, setRedBookStatus] = useState<RedBookStatus>({
    setup_browser: false,
    job_running: false,
    really_do: false
  })

  const [timerSettings, setTimerSettings] = useState<TimerSettings>({
    intervalMinutes: -1
  });

  const updateTimerSettings = (settings: Partial<TimerSettings>) => {
    updateIntervalMinutesApi(settings)
      .then(value => {
        setTimerSettings(prev=>{
          return { ...prev, ...value.data } as TimerSettings
        });
      })
      .catch(() => {
        toast.error('设置失败')
      });
  };

  const fetchRedBookStatus = async () => {
    getRedBookStatusApi()
      .then(value => {
        setRedBookStatus(value.data);
      }).catch(reason => {
        console.log(reason)
        toast.error("获取状态失败");
      })
  }

  return (
    <SettingContext.Provider value={{
      redBookStatus,
      fetchRedBookStatus,
      timerSettings,
      updateTimerSettings
    }}>
      {children}
    </SettingContext.Provider>
  )
}

export const useSettingContext = () => {
  const context = useContext(SettingContext);
  if (context === undefined) {
    throw new Error('useSettingContext must be used within a SettingProvider');
  }
  return context;
};
