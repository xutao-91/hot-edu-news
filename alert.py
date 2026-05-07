#!/usr/bin/env python3
import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import List, Dict

class AlertManager:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.alert_config = self.config.get('alert', {})
        self.enabled = self.alert_config.get('enabled', False)
        self.alert_interval = self.alert_config.get('alert_interval', 300) # 默认5分钟内相同告警不重复发送
        self.last_alerts = {} # 记录最近发送的告警，key是告警内容hash，value是发送时间
    
    def _should_alert(self, alert_key: str) -> bool:
        """判断是否应该发送告警（去重逻辑）"""
        if not self.enabled:
            return False
        now = datetime.now()
        if alert_key in self.last_alerts:
            last_time = self.last_alerts[alert_key]
            if now - last_time < timedelta(seconds=self.alert_interval):
                return False
        self.last_alerts[alert_key] = now
        return True
    
    def _send_wecom_alert(self, title: str, content: str) -> bool:
        """发送企业微信告警"""
        wecom_config = self.alert_config.get('wecom', {})
        if not wecom_config.get('webhook_url'):
            return False
        
        try:
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"## {title}\n\n{content}\n\n**告警时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            response = requests.post(wecom_config['webhook_url'], json=message, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 发送企业微信告警失败: {str(e)}")
            return False
    
    def _send_email_alert(self, title: str, content: str) -> bool:
        """发送邮件告警"""
        email_config = self.alert_config.get('email', {})
        required_fields = ['smtp_server', 'smtp_port', 'smtp_user', 'smtp_password', 'to_email']
        if not all(email_config.get(field) for field in required_fields):
            return False
        
        try:
            msg = MIMEText(f"{content}\n\n告警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'plain', 'utf-8')
            msg['Subject'] = f"[教育新闻爬虫告警] {title}"
            msg['From'] = email_config['smtp_user']
            msg['To'] = email_config['to_email']
            
            with smtplib.SMTP_SSL(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.login(email_config['smtp_user'], email_config['smtp_password'])
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"❌ 发送邮件告警失败: {str(e)}")
            return False
    
    def send_alert(self, title: str, content: str, alert_key: str = None) -> bool:
        """发送告警，自动尝试所有配置的渠道"""
        if not self.enabled:
            return False
        
        if alert_key is None:
            alert_key = hash(title + content)
        
        if not self._should_alert(str(alert_key)):
            print(f"ℹ️  告警 {title} 已在最近 {self.alert_interval} 秒内发送过，跳过重复发送")
            return False
        
        print(f"🚨 发送告警: {title}")
        success = False
        
        # 尝试企业微信
        if self._send_wecom_alert(title, content):
            success = True
        
        # 尝试邮件
        if self._send_email_alert(title, content):
            success = True
        
        return success
    
    def process_pending_alerts(self, db) -> int:
        """处理数据库中未发送的告警"""
        if not self.enabled:
            return 0
        
        errors = db.get_unalerted_errors()
        if not errors:
            return 0
        
        sent_count = 0
        error_ids_to_mark = []
        
        for error in errors:
            title = f"{error['source']} 发生错误"
            content = f"错误信息: {error['message']}\n错误详情: {error['error_detail'] or '无'}\n发生时间: {error['happened_at']}"
            alert_key = f"error_{error['id']}"
            
            if self.send_alert(title, content, alert_key):
                error_ids_to_mark.append(error['id'])
                sent_count += 1
        
        if error_ids_to_mark:
            db.mark_errors_alerted(error_ids_to_mark)
        
        return sent_count

if __name__ == "__main__":
    # 测试告警
    alert_manager = AlertManager()
    if alert_manager.enabled:
        alert_manager.send_alert("测试告警", "这是一条测试告警信息，用于验证告警功能是否正常工作。")
