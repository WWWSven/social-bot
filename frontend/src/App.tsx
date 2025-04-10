import {BrowserRouter, Route, Routes} from "react-router";
import NotFound from "@/pages/NotFound.tsx";
import Index from "@/pages/Index.tsx"
import Analysis from "@/pages/Analysis.tsx";
import Platform from "@/pages/Platform.tsx";
import {KeywordProvider} from "@/context/KeywordContext.tsx";
import {Toaster} from "@/components/ui/sonner";
import {SettingProvider} from "@/context/SettingContext.tsx";

function App() {
  return (
    <SettingProvider>
      <KeywordProvider>
        <Toaster/>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/platform" element={<Platform />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/analysis/:id" element={<Analysis />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </KeywordProvider>
    </SettingProvider>
  )
}

export default App
