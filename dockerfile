# Dockerfile - ハイブリッド型自律コード修正システム
FROM python:3.11-slim

# メンテナ情報
LABEL maintainer="your-email@example.com"
LABEL description="Hybrid Autonomous Code Fixing System"

# 作業ディレクトリ
WORKDIR /app

# 環境変数
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# システムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 基本ツール
    git \
    curl \
    wget \
    vim \
    less \
    # ビルドツール
    build-essential \
    gcc \
    g++ \
    # Playwright/Chromium用
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    # WP-CLI用
    php-cli \
    php-mysql \
    php-curl \
    php-json \
    php-mbstring \
    php-xml \
    # その他
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# WP-CLIのインストール
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp

# GitHub CLIのインストール（オプション）
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Playwrightブラウザのインストール
RUN playwright install chromium && \
    playwright install-deps chromium

# アプリケーションファイルをコピー
COPY . .

# ディレクトリ作成
RUN mkdir -p \
    /app/backups \
    /app/logs \
    /app/storage_cache \
    /app/test_results \
    /app/session

# 権限設定
RUN chmod +x /app/*.py

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# ポート公開（必要に応じて）
# EXPOSE 8080

# デフォルトコマンド
CMD ["python", "main_hybrid_fix.py"]

# ========================================
# マルチステージビルド版（最適化）
# ========================================

# ビルドステージ
FROM python:3.11-slim as builder

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 実行ステージ
FROM python:3.11-slim

WORKDIR /app

# システムパッケージ（最小限）
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    php-cli \
    && rm -rf /var/lib/apt/lists/*

# ビルドステージからPythonパッケージをコピー
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# WP-CLI
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp

# アプリケーション
COPY . .

# ディレクトリ
RUN mkdir -p /app/backups /app/logs /app/storage_cache

CMD ["python", "main_hybrid_fix.py"]