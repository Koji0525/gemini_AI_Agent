"""複数のエラータイプのテスト"""
import asyncio
from main_hybrid_fix import HybridFixSystem, HybridFixConfig

async def test_multiple_errors():
    system = HybridFixSystem(config=HybridFixConfig())
    await system.initialize()
    
    # テスト1: ImportError
    try:
        import nonexistent_module
    except Exception as e:
        await system.handle_error(e, "Test-Import", "test_file.py")
    
    # テスト2: TypeError
    try:
        result = "string" + 123
    except Exception as e:
        await system.handle_error(e, "Test-Type", "test_file.py")
    
    # テスト3: KeyError
    try:
        data = {}
        value = data['missing_key']
    except Exception as e:
        await system.handle_error(e, "Test-Key", "test_file.py")
    
    system.print_system_stats()

asyncio.run(test_multiple_errors())
