#!/usr/bin/env python3
"""
WordPressエージェント健全性チェック
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_wordpress_agents():
    """WordPressエージェントの健全性チェック"""
    agents = [
        ('wp_cpt_agent', 'WordPressCPTAgent'),
        ('wp_acf_agent', 'WordPressACFAgent'),
        ('wp_requirements_agent', 'WordPressRequirementsAgent'),
        ('wp_dev_agent', 'WordPressDevAgent'),
    ]
    
    print("🔧 WordPressエージェント健全性チェック")
    print("=" * 50)
    
    all_healthy = True
    for module, class_name in agents:
        try:
            exec(f'from wordpress.{module} import {class_name}')
            agent_class = eval(class_name)
            
            # 基本チェック
            checks = [
                ('インポート', True),
                ('executeメソッド', hasattr(agent_class, 'execute')),
                ('__init__メソッド', hasattr(agent_class, '__init__')),
            ]
            
            print(f"📋 {class_name}:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if not result:
                    all_healthy = False
                    
        except Exception as e:
            print(f"❌ {class_name}: インポート失敗 - {e}")
            all_healthy = False
    
    print("=" * 50)
    if all_healthy:
        print("🎉 すべてのエージェントが健全です")
    else:
        print("💥 問題のあるエージェントがあります")
    
    return all_healthy

if __name__ == "__main__":
    check_wordpress_agents()
