from setuptools import setup, find_packages

# 明示的にパッケージを指定（自動検出を無効化）
setup(
    name="gemini_ai_agent",
    version="1.21.0",
    description="AI自律開発エージェントシステム",
    
    # 明示的にパッケージを指定
    packages=[
        "agents",
        "core_agents", 
        "task_executor",
        "browser_control",
        "configuration",
        "tools",
        "knowledge_system",
        "knowledge_system.utils",
        "knowledge_system.scripts",
    ],
    
    # パッケージ自動検出を無効化
    py_modules=[],  # 単一ファイルモジュールなし
    
    # 依存関係
    install_requires=[
        "click>=8.0.0",
        "google-api-python-client>=2.0.0",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=0.4.0",
        "pathlib2>=2.3.0; python_version < '3.4'",
    ],
    
    # エントリポイント
    entry_points={
        'console_scripts': [
            'run-agent=agents.complete_engine_ultimate:main',
            'run-tasks=run_3_cycles.py:main',
        ],
    },
    
    # パッケージ検出の設定
    include_package_data=False,
    zip_safe=False,
)
