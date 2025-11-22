import logging
import time
import random
from datetime import datetime
import uuid

def get_logger(name: str) -> logging.Logger:
    """
    指定された名前でロガーを設定し、取得します。
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # コンソールハンドラ
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # ファイルハンドラ (オプション)
        # fh = logging.FileHandler(f'{name}.log')
        # fh.setLevel(logging.DEBUG)
        # fh.setFormatter(formatter)
        # logger.addHandler(fh)
    return logger

def simulate_process(process_name: str, duration: float, success_rate: float = 0.9) -> tuple[bool, str]:
    """
    非同期処理や外部サービスとの連携をシミュレートします。
    指定された成功率に基づいて成功または失敗を返します。
    """
    logger = get_logger("Simulator")
    logger.debug(f"シミュレーション開始: {process_name} (所要時間: {duration:.2f}s, 成功率: {success_rate*100:.0f}%)")
    
    time.sleep(duration) # 処理時間のシミュレート

    if random.random() < success_rate:
        message = f"{process_name} が正常に完了しました。"
        logger.debug(f"シミュレーション成功: {message}")
        return True, message
    else:
        error_types = ["Network Error", "API Timeout", "Resource Exhaustion", "Logic Failure"]
        message = f"{process_name} が失敗しました: {random.choice(error_types)}"
        logger.warning(f"シミュレーション失敗: {message}")
        return False, message

def generate_unique_id() -> str:
    """
    ユニークなIDを生成します。
    """
    return str(uuid.uuid4())

def create_report_section(title: str, content: str, level: int = 2) -> str:
    """
    レポートのセクションをMarkdown形式で生成します。
    """
    prefix = "#" * level
    return f"{prefix} {title}\n\n{content}\n\n"

def generate_flow_diagram_mermaid(flow_data: list[tuple[str, str, str | None]]) -> str:
    """
    Mermaid記法でフローチャート図を生成します。
    flow_dataは (source, target, label) のタプルのリストです。
    """
    mermaid_code = ["```mermaid", "graph TD"]
    
    # ノード定義 (重複を避ける)
    nodes = set()
    for source, target, _ in flow_data:
        nodes.add(source)
        nodes.add(target)
    
    # 簡略化したノードID (スペースなどをアンダースコアに変換)
    node_map = {node: node.replace(' ', '_').replace('-', '_').replace(':', '_').replace('(', '').replace(')', '').replace('/', '_').replace('.', '_') for node in nodes}

    for source, target, label in flow_data:
        src_id = node_map[source]
        tgt_id = node_map[target]
        
        # 表示名を設定 (スペースなどを元に戻す)
        mermaid_code.append(f"    {src_id}[{source}]")
        mermaid_code.append(f"    {tgt_id}[{target}]")

        if label:
            mermaid_code.append(f"    {src_id} -->|{label}| {tgt_id}")
        else:
            mermaid_code.append(f"    {src_id} --> {tgt_id}")
    
    mermaid_code.append("```")
    return "\n".join(mermaid_code)