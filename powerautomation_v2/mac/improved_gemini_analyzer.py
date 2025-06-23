#!/usr/bin/env python3
"""
改進版Gemini Vision對話分析工具
針對Manus繁體中文對話優化
"""

import asyncio
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

try:
    from google import genai
except ImportError:
    print("❌ 請安裝: pip3 install google-genai")
    exit(1)

@dataclass
class ConversationMessage:
    content: str
    sender: str  # user, assistant, system
    timestamp: str
    confidence: float = 0.9
    message_type: str = "normal"  # normal, question, answer, system

class ImprovedGeminiAnalyzer:
    def __init__(self, api_key="AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw"):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
    
    async def analyze_screenshot(self, image_path):
        """分析單張截圖"""
        print(f"🔍 分析截圖: {image_path}")
        
        try:
            # 讀取圖片
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # 改進的提示詞
            prompt = """
請仔細分析這張Manus對話截圖，提取所有對話內容。

分析要求：
1. 識別所有繁體中文對話內容
2. 區分用戶問題和AI回覆
3. 保持原始文字，不要修改或翻譯
4. 按對話順序排列

識別規則：
- 用戶問題：通常是提問、請求幫助、描述問題
- AI回覆：通常是回答、建議、解決方案
- 系統消息：如"Manus has completed"等

輸出格式：
[用戶]: 具體問題內容
[AI]: 具體回覆內容
[系統]: 系統消息

請只輸出對話內容，每行一個消息，不要其他說明文字。
"""
            
            # 調用Gemini
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    prompt,
                    {"mime_type": "image/png", "data": image_data}
                ]
            )
            
            # 解析回應
            conversations = self._parse_response(response.text)
            
            print(f"  ✅ 提取到 {len(conversations)} 條對話")
            for conv in conversations:
                print(f"    [{conv.sender}] {conv.content[:50]}...")
            
            return conversations
            
        except Exception as e:
            print(f"❌ 分析失敗: {e}")
            return []
    
    def _parse_response(self, text):
        """解析Gemini回應"""
        conversations = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('```'):
                continue
            
            # 解析不同格式
            if line.startswith('[用戶]') or line.startswith('[USER]'):
                content = line.split(':', 1)[1].strip() if ':' in line else line[4:].strip()
                if content:
                    conversations.append(ConversationMessage(
                        content=content,
                        sender='user',
                        timestamp=datetime.now().isoformat(),
                        message_type='question'
                    ))
            
            elif line.startswith('[AI]') or line.startswith('[助手]') or line.startswith('[ASSISTANT]'):
                content = line.split(':', 1)[1].strip() if ':' in line else line[4:].strip()
                if content:
                    conversations.append(ConversationMessage(
                        content=content,
                        sender='assistant',
                        timestamp=datetime.now().isoformat(),
                        message_type='answer'
                    ))
            
            elif line.startswith('[系統]') or line.startswith('[SYSTEM]'):
                content = line.split(':', 1)[1].strip() if ':' in line else line[4:].strip()
                if content:
                    conversations.append(ConversationMessage(
                        content=content,
                        sender='system',
                        timestamp=datetime.now().isoformat(),
                        message_type='system'
                    ))
            
            # 如果沒有標籤，嘗試智能判斷
            elif len(line) > 10:
                sender, msg_type = self._smart_classify(line)
                conversations.append(ConversationMessage(
                    content=line,
                    sender=sender,
                    timestamp=datetime.now().isoformat(),
                    message_type=msg_type
                ))
        
        return conversations
    
    def _smart_classify(self, text):
        """智能分類消息"""
        text_lower = text.lower()
        
        # 系統消息關鍵詞
        system_keywords = ['completed', 'task', 'manus has', 'system', '系統']
        if any(keyword in text_lower for keyword in system_keywords):
            return 'system', 'system'
        
        # 問題關鍵詞
        question_keywords = ['如何', '怎麼', '什麼', '為什麼', '請問', '請幫', '?', '？', '需要', '想要']
        if any(keyword in text for keyword in question_keywords):
            return 'user', 'question'
        
        # 回答關鍵詞
        answer_keywords = ['您好', '建議', '可以', '應該', '根據', '我們', '這裡', '以下是', '首先']
        if any(keyword in text for keyword in answer_keywords):
            return 'assistant', 'answer'
        
        # 默認為用戶消息
        return 'user', 'normal'
    
    def save_analysis(self, conversations, output_file="analysis_result.json"):
        """保存分析結果"""
        if not conversations:
            print("❌ 沒有對話可保存")
            return None
        
        # 準備數據
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_messages': len(conversations),
            'statistics': {
                'user_messages': sum(1 for c in conversations if c.sender == 'user'),
                'assistant_messages': sum(1 for c in conversations if c.sender == 'assistant'),
                'system_messages': sum(1 for c in conversations if c.sender == 'system')
            },
            'conversations': [{
                'content': conv.content,
                'sender': conv.sender,
                'message_type': conv.message_type,
                'timestamp': conv.timestamp,
                'confidence': conv.confidence
            } for conv in conversations]
        }
        
        # 保存JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 保存可讀格式
        txt_file = output_file.replace('.json', '.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Manus對話分析結果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 統計信息:\n")
            f.write(f"  總消息數: {data['total_messages']}\n")
            f.write(f"  用戶消息: {data['statistics']['user_messages']}\n")
            f.write(f"  AI回覆: {data['statistics']['assistant_messages']}\n")
            f.write(f"  系統消息: {data['statistics']['system_messages']}\n\n")
            
            f.write("📋 對話內容:\n")
            f.write("-" * 40 + "\n\n")
            
            for i, conv in enumerate(conversations, 1):
                f.write(f"[{i:03d}] {conv.sender.upper()} ({conv.message_type}):\n")
                f.write(f"{conv.content}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"💾 分析結果已保存:")
        print(f"  📄 JSON: {output_file}")
        print(f"  📋 文本: {txt_file}")
        
        return output_file, txt_file

async def main():
    """主函數 - 分析單張截圖"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python3 improved_gemini_analyzer.py <截圖路徑>")
        print("例如: python3 improved_gemini_analyzer.py scroll_20250622_193050_000.png")
        return
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ 文件不存在: {image_path}")
        return
    
    analyzer = ImprovedGeminiAnalyzer()
    
    print("🚀 開始分析截圖...")
    conversations = await analyzer.analyze_screenshot(image_path)
    
    if conversations:
        print(f"\n✅ 分析完成！提取到 {len(conversations)} 條對話")
        
        # 顯示統計
        user_count = sum(1 for c in conversations if c.sender == 'user')
        ai_count = sum(1 for c in conversations if c.sender == 'assistant')
        system_count = sum(1 for c in conversations if c.sender == 'system')
        
        print(f"📊 統計: 用戶 {user_count}, AI {ai_count}, 系統 {system_count}")
        
        # 顯示前幾條
        print(f"\n📋 對話預覽:")
        for i, conv in enumerate(conversations[:5]):
            print(f"  {i+1}. [{conv.sender}] {conv.content[:60]}...")
        
        # 保存結果
        output_file = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.save_analysis(conversations, output_file)
        
    else:
        print("❌ 沒有提取到對話內容")
        print("💡 建議檢查:")
        print("  1. 圖片是否清晰")
        print("  2. 是否包含對話內容")
        print("  3. API密鑰是否正確")

if __name__ == "__main__":
    asyncio.run(main())

