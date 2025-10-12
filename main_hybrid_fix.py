logger.info("\n🧪 テストエラーを生成して自動修正をテスト")
    
    try:
        # 意図的にエラーを発生させる
        test_data = None
        result = getattr(test_data, 'get', None)  # Fixed: safe attribute access('key')  # AttributeError
    
    except Exception as e:
        # エラーを自動修正システムに送信
        handle_result = await system.handle_error(
            error=e,
