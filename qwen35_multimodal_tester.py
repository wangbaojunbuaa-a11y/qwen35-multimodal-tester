#!/usr/bin/env python3
"""
Qwen3.5-397B 多模态功能验证工具 (GUI版)
支持：文本、图片、文档、视频理解测试
"""

import base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import requests
import json
import urllib3
from pathlib import Path
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Qwen35Tester:
    def __init__(self, root):
        self.root = root
        self.root.title("Qwen3.5-397B 多模态测试工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 配置变量
        self.api_base = tk.StringVar(value="http://localhost:8000/v1")
        self.api_key = tk.StringVar(value="")
        self.model_name = tk.StringVar(value="qwen3.5-397b")
        self.ignore_ssl = tk.BooleanVar(value=True)
        
        # 文件路径变量
        self.image_path = tk.StringVar()
        self.document_path = tk.StringVar()
        self.video_path = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        # 配置区域
        config_frame = ttk.LabelFrame(self.root, text="API 配置", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(config_frame, text="API地址:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(config_frame, textvariable=self.api_base, width=60).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="API密钥:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(config_frame, textvariable=self.api_key, width=60, show="*").grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="模型名称:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(config_frame, textvariable=self.model_name, width=60).grid(row=2, column=1, padx=5, pady=2)

        ttk.Checkbutton(
            config_frame,
            text="忽略 SSL 证书校验（适用于公司内网自签名证书）",
            variable=self.ignore_ssl
        ).grid(row=3, column=1, sticky="w", padx=5, pady=4)
        
        # 测试区域 - 使用Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 测试1: 文本对话
        text_frame = ttk.Frame(notebook, padding=10)
        notebook.add(text_frame, text="📝 文本对话")
        self.setup_text_test(text_frame)
        
        # 测试2: 图片理解
        image_frame = ttk.Frame(notebook, padding=10)
        notebook.add(image_frame, text="🖼️ 图片理解")
        self.setup_image_test(image_frame)
        
        # 测试3: 文档解析
        doc_frame = ttk.Frame(notebook, padding=10)
        notebook.add(doc_frame, text="📄 文档解析")
        self.setup_document_test(doc_frame)
        
        # 测试4: 视频理解
        video_frame = ttk.Frame(notebook, padding=10)
        notebook.add(video_frame, text="🎬 视频理解")
        self.setup_video_test(video_frame)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.root, text="测试结果", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=12, wrap="word")
        self.result_text.pack(fill="both", expand=True)
        
    def setup_text_test(self, parent):
        """设置文本测试界面"""
        ttk.Label(parent, text="输入问题:").pack(anchor="w")
        
        self.text_input = tk.Text(parent, height=5, wrap="word")
        self.text_input.pack(fill="x", pady=5)
        self.text_input.insert("1.0", "请用一句话介绍你自己，并说明你是什么类型的模型。")
        
        ttk.Button(parent, text="🚀 发送测试", command=self.test_text).pack(pady=10)
        
    def setup_image_test(self, parent):
        """设置图片测试界面"""
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill="x", pady=5)
        
        ttk.Label(file_frame, text="选择图片:").pack(side="left")
        ttk.Entry(file_frame, textvariable=self.image_path, width=50).pack(side="left", padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.browse_image).pack(side="left")
        
        ttk.Label(parent, text="问题:").pack(anchor="w", pady=(10, 0))
        
        self.image_question = tk.Text(parent, height=3, wrap="word")
        self.image_question.pack(fill="x", pady=5)
        self.image_question.insert("1.0", "请详细描述这张图片的内容。")
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🚀 发送测试", command=self.test_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🌐 使用网络测试图", command=self.test_image_url).pack(side="left", padx=5)
        
    def setup_document_test(self, parent):
        """设置文档测试界面"""
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill="x", pady=5)
        
        ttk.Label(file_frame, text="选择文档:").pack(side="left")
        ttk.Entry(file_frame, textvariable=self.document_path, width=50).pack(side="left", padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.browse_document).pack(side="left")
        
        ttk.Label(parent, text="问题:").pack(anchor="w", pady=(10, 0))
        
        self.doc_question = tk.Text(parent, height=3, wrap="word")
        self.doc_question.pack(fill="x", pady=5)
        self.doc_question.insert("1.0", "请总结这个文档的主要内容。")
        
        ttk.Button(parent, text="🚀 发送测试", command=self.test_document).pack(pady=10)
        
    def setup_video_test(self, parent):
        """设置视频测试界面"""
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill="x", pady=5)
        
        ttk.Label(file_frame, text="选择视频:").pack(side="left")
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).pack(side="left", padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.browse_video).pack(side="left")
        
        ttk.Label(parent, text="问题:").pack(anchor="w", pady=(10, 0))
        
        self.video_question = tk.Text(parent, height=3, wrap="word")
        self.video_question.pack(fill="x", pady=5)
        self.video_question.insert("1.0", "请描述这个视频的内容，包括主要场景和动作。")
        
        ttk.Button(parent, text="🚀 发送测试", command=self.test_video).pack(pady=10)
        
    def browse_image(self):
        path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.webp"), ("所有文件", "*.*")]
        )
        if path:
            self.image_path.set(path)
            
    def browse_document(self):
        path = filedialog.askopenfilename(
            title="选择文档",
            filetypes=[("PDF文件", "*.pdf"), ("图片文件", "*.jpg *.png"), ("所有文件", "*.*")]
        )
        if path:
            self.document_path.set(path)
            
    def browse_video(self):
        path = filedialog.askopenfilename(
            title="选择视频",
            filetypes=[("视频文件", "*.mp4 *.webm *.mov *.avi"), ("所有文件", "*.*")]
        )
        if path:
            self.video_path.set(path)
            
    def get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key.get():
            headers["Authorization"] = f"Bearer {self.api_key.get()}"
        return headers
    
    def encode_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def get_mime_type(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".gif": "image/gif", ".webp": "image/webp", ".pdf": "application/pdf",
            ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
        }
        return mime_map.get(suffix, "application/octet-stream")
    
    def run_request(self, payload: dict, test_name: str):
        """在后台线程运行请求"""
        def _run():
            try:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("end", f"[{test_name}] 请求中...\n\n")
                self.root.update()
                
                base_url = self.api_base.get().rstrip("/")
                response = requests.post(
                    f"{base_url}/chat/completions",
                    headers=self.get_headers(),
                    json=payload,
                    timeout=60,
                    verify=not self.ignore_ssl.get()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("end", f"✅ {test_name} 成功\n")
                    self.result_text.insert("end", "-" * 50 + "\n")
                    self.result_text.insert("end", content)
                else:
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("end", f"❌ 错误: {response.status_code}\n")
                    self.result_text.insert("end", response.text)
                    
            except Exception as e:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("end", f"❌ 异常: {str(e)}")
                
        threading.Thread(target=_run, daemon=True).start()
    
    def test_text(self):
        question = self.text_input.get("1.0", "end").strip()
        if not question:
            messagebox.showwarning("提示", "请输入问题")
            return
            
        payload = {
            "model": self.model_name.get(),
            "messages": [{"role": "user", "content": question}]
        }
        self.run_request(payload, "文本对话测试")
        
    def test_image(self):
        image_path = self.image_path.get()
        if not image_path or not Path(image_path).exists():
            messagebox.showwarning("提示", "请选择有效的图片文件")
            return
            
        question = self.image_question.get("1.0", "end").strip()
        image_base64 = self.encode_file(image_path)
        mime_type = self.get_mime_type(image_path)
        image_url = f"data:{mime_type};base64,{image_base64}"
        
        payload = {
            "model": self.model_name.get(),
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }]
        }
        self.run_request(payload, "图片理解测试")
        
    def test_image_url(self):
        """使用网络测试图片"""
        question = self.image_question.get("1.0", "end").strip()
        test_image_url = "https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/0033279361/p405166.png"
        
        payload = {
            "model": self.model_name.get(),
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": test_image_url}}
                ]
            }]
        }
        self.run_request(payload, "图片理解测试(网络)")
        
    def test_document(self):
        doc_path = self.document_path.get()
        if not doc_path or not Path(doc_path).exists():
            messagebox.showwarning("提示", "请选择有效的文档文件")
            return
            
        question = self.doc_question.get("1.0", "end").strip()
        doc_base64 = self.encode_file(doc_path)
        mime_type = self.get_mime_type(doc_path)
        doc_url = f"data:{mime_type};base64,{doc_base64}"
        
        payload = {
            "model": self.model_name.get(),
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": doc_url}}
                ]
            }]
        }
        self.run_request(payload, "文档解析测试")
        
    def test_video(self):
        video_path = self.video_path.get()
        if not video_path or not Path(video_path).exists():
            messagebox.showwarning("提示", "请选择有效的视频文件")
            return
            
        question = self.video_question.get("1.0", "end").strip()
        video_base64 = self.encode_file(video_path)
        mime_type = self.get_mime_type(video_path)
        video_url = f"data:{mime_type};base64,{video_base64}"
        
        payload = {
            "model": self.model_name.get(),
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "video_url", "video_url": {"url": video_url}}
                ]
            }]
        }
        self.run_request(payload, "视频理解测试")


def main():
    root = tk.Tk()
    app = Qwen35Tester(root)
    root.mainloop()


if __name__ == "__main__":
    main()