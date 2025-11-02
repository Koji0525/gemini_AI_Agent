# 再利用可能な設計パターン集

## 1. ExecutionController パターン

**用途:** 実行モード制御が必要な全てのシステム

**適用例:**
- 24時間自律システム
- バッチ処理システム
- テスト実行フレームワーク

**使い方:**
```python
from utils.execution_controller import ExecutionController

controller = ExecutionController()

while controller.cycle_manager.should_continue():
    await controller.execute_cycle(your_function, args)
    
    wait_time = controller.cycle_manager.get_wait_time()
    if wait_time > 0:
        await asyncio.sleep(wait_time)
```

---

## 2. 二重ループ回避パターン

**問題:** 外側と内側で独立した制御ロジックを持つと制御不能に

**解決策:** 
- 制御は最外部で統一
- 内部コンポーネントはパラメータで制御
- `single_cycle=True`のような明示的パラメータ

---

## 3. Mode-Driven Development

**原則:** 実行モードに応じて動作を切り替える

**実装:**
```python
if execution_mode.is_test():
    # テスト用の簡易実行
elif execution_mode.is_production():
    # 本番用の完全実行
```

---

## 今後追加すべきパターン

- [ ] RetryController（リトライ制御の統一）
- [ ] StateManager（状態管理の汎用化）
- [ ] EventBus（イベント駆動アーキテクチャ）
