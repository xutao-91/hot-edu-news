#!/usr/bin/env python3
import os
import shutil
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
import json

class BackupManager:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.backup_config = self.config.get('backup', {})
        self.enabled = self.backup_config.get('enabled', False)
        self.backup_dir = self.backup_config.get('backup_dir', 'data/backups')
        self.retention_days = self.backup_config.get('retention_days', 30)
        self.backup_items = [
            'data/news.db', # 数据库
            'data/raw', # 原始文章
            'data/translated', # 翻译结果
            'data/cache' # 缓存文件
        ]
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self) -> str:
        """创建备份"""
        if not self.enabled:
            print("ℹ️  备份功能未启用")
            return ""
        
        now = datetime.now()
        backup_filename = f"backup_{now.strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        print(f"🚀 开始创建备份: {backup_path}")
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                for item in self.backup_items:
                    item_path = Path(item)
                    if item_path.exists():
                        tar.add(item_path, arcname=item_path.name)
                        print(f"✅ 添加到备份: {item}")
                    else:
                        print(f"⚠️  跳过不存在的文件/目录: {item}")
            
            backup_size = os.path.getsize(backup_path) / (1024 * 1024)
            print(f"🎉 备份创建完成，大小: {backup_size:.2f} MB")
            
            # 清理过期备份
            self._cleanup_old_backups()
            
            return backup_path
        
        except Exception as e:
            print(f"❌ 备份创建失败: {str(e)}")
            return ""
    
    def _cleanup_old_backups(self):
        """清理超过保留天数的备份"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for backup_file in Path(self.backup_dir).glob("backup_*.tar.gz"):
            try:
                # 从文件名提取日期
                filename = backup_file.name
                date_str = filename.split('_')[1]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date < cutoff_date:
                    os.remove(backup_file)
                    deleted_count += 1
                    print(f"🗑️  删除过期备份: {filename}")
            except Exception as e:
                print(f"⚠️  处理备份文件 {filename} 失败: {str(e)}")
                continue
        
        if deleted_count > 0:
            print(f"✅ 清理完成，共删除 {deleted_count} 个过期备份")
    
    def restore_backup(self, backup_path: str, restore_dir: str = "./") -> bool:
        """从备份恢复"""
        if not os.path.exists(backup_path):
            print(f"❌ 备份文件不存在: {backup_path}")
            return False
        
        print(f"🚀 开始从备份恢复: {backup_path}")
        
        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(path=restore_dir)
            
            print(f"🎉 备份恢复完成")
            return True
        
        except Exception as e:
            print(f"❌ 备份恢复失败: {str(e)}")
            return False

if __name__ == "__main__":
    # 测试备份
    backup_manager = BackupManager()
    if backup_manager.enabled:
        backup_path = backup_manager.create_backup()
        if backup_path:
            print(f"备份文件已创建: {backup_path}")
