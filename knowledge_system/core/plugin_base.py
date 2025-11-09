#!/usr/bin/env python3
import os
import importlib.util
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """プラグインの基底クラス"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """プラグインのメイン実行メソッド"""
        pass
    
    def validate(self):
        """プラグインの検証"""
        return True

class PluginManager:
    """プラグインマネージャー"""
    
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """プラグインをロード"""
        if not os.path.exists(self.plugins_dir):
            return
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]
                self.load_plugin(plugin_name)
    
    def load_plugin(self, plugin_name):
        """単一プラグインをロード"""
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_name, 
                os.path.join(self.plugins_dir, f"{plugin_name}.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # プラグインクラスを取得（規約: {PluginName}Plugin）
            plugin_class = getattr(module, f"{plugin_name.capitalize()}Plugin", None)
            if plugin_class and issubclass(plugin_class, BasePlugin):
                self.plugins[plugin_name] = plugin_class
                print(f"✅ プラグインをロード: {plugin_name}")
            
        except Exception as e:
            print(f"❌ プラグインロード失敗 {plugin_name}: {e}")
    
    def execute_plugin(self, plugin_name, *args, **kwargs):
        """プラグインを実行"""
        if plugin_name in self.plugins:
            plugin_instance = self.plugins[plugin_name]()
            if plugin_instance.enabled and plugin_instance.validate():
                return plugin_instance.execute(*args, **kwargs)
        return None

# 使用例
if __name__ == "__main__":
    manager = PluginManager()
    result = manager.execute_plugin("quality_assessor", "タイトル", "内容", "タグ")
    print(f"プラグイン実行結果: {result}")
