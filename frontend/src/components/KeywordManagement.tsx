import React, { useState } from 'react';
import { useKeywordContext } from '@/context/KeywordContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
// import { Switch } from '@/components/ui/switch';
import { X, Plus, Trash2 } from 'lucide-react';
import {Textarea} from "@/components/ui/textarea.tsx";

const KeywordManagement: React.FC = () => {

  const {
    keywordStrings,
    addKeywordString,
    updateKeywordString,
    removeKeywordString,
    // toggleKeywordStringActive
  } = useKeywordContext();

  const [name, setName] = useState('');
  const [keywordInput, setKeywordInput] = useState('');
  const [prompts, setPrompts] = useState('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [editMode, setEditMode] = useState<string | null>(null);

  const handleAddKeyword = () => {
    if (keywordInput.trim()) {
      setKeywords([...keywords, keywordInput.trim()]);
      setKeywordInput('');
    }
  };

  const handleRemoveKeyword = (indexToRemove: number) => {
    setKeywords(keywords.filter((_, index) => index !== indexToRemove));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (name.trim() && keywords.length > 0) {
      if (editMode) {
        updateKeywordString(editMode, { name, 'keywords': keywords, prompts});
        setEditMode(null);
      } else {
        addKeywordString(name, keywords, prompts);
      }
      setName('');
      setKeywords([]);
      setPrompts('')
    }
  };

  const handleEdit = (keywordString: typeof keywordStrings[0]) => {
    setEditMode(keywordString.id);
    setName(keywordString.name);
    setKeywords(keywordString.keywords);
    setPrompts(keywordString.prompts)
  };

  const handleCancelEdit = () => {
    setEditMode(null);
    setName('');
    setKeywords([]);
    setPrompts('')
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{editMode ? '编辑关键词字符串' : '添加关键词字符串'}</CardTitle>
          <CardDescription>
            关键词用于搜索指定内容, prompts用于自定义喜好
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">名称</Label>
              <Input
                id="name"
                placeholder="输入关键词字符串名称"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="keywords">关键词</Label>
              <div className="flex space-x-2">
                <Input
                  id="keywords"
                  placeholder="输入关键词"
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                />
                <Button type="button" size="icon" onClick={handleAddKeyword}>
                  <Plus size={18} />
                </Button>
              </div>
            </div>

            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {keywords.map((keyword, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1 px-2 py-1">
                    {keyword}
                    <button
                      type="button"
                      onClick={() => handleRemoveKeyword(index)}
                      className="ml-1 text-gray-500 hover:text-gray-700"
                    >
                      <X size={12} />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="keywords">prompts</Label>
              <div className="flex space-x-2 h-[200px]">
                <Textarea
                  id="prompts"
                  placeholder="输入提示词"
                  value={prompts}
                  onChange={(e) => setPrompts(e.target.value)}
                />
              </div>
            </div>
          </CardContent>
          <div className="h-4"></div>
          <CardFooter className="flex justify-between">
            {editMode && (
              <Button type="button" variant="outline" onClick={handleCancelEdit}>
                取消
              </Button>
            )}
            <Button type="submit">
              {editMode ? '保存修改' : '添加'}
            </Button>
          </CardFooter>
        </form>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {keywordStrings.map((keywordString) => (
          <Card key={keywordString.id}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle>{keywordString.name}</CardTitle>
                {/*<div className="flex items-center space-x-2">*/}
                {/*  <span className="text-sm text-muted-foreground">*/}
                {/*    {keywordString.isActive ? '已激活' : '未激活'}*/}
                {/*  </span>*/}
                {/*  <Switch*/}
                {/*    checked={keywordString.isActive}*/}
                {/*    onCheckedChange={() => toggleKeywordStringActive(keywordString.id)}*/}
                {/*  />*/}
                {/*</div>*/}
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2 mb-4">
                {keywordString.keywords.map((keyword, index) => (
                  <Badge key={index} variant="outline">{keyword}</Badge>
                ))}
              </div>

              <div className="text-sm text-muted-foreground">
                已收集内容: {keywordString.collectedContent?.length} 条
              </div>

              {keywordString.lastCollectedAt && (
                <div className="text-sm text-muted-foreground mt-1">
                  最近收集时间: {new Date(keywordString.lastCollectedAt).toLocaleString()}
                </div>
              )}
            </CardContent>
            <CardFooter className="pt-0">
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEdit(keywordString)}
                >
                  编辑
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => removeKeywordString(keywordString.id)}
                >
                  <Trash2 size={16} className="mr-1" /> 删除
                </Button>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default KeywordManagement;