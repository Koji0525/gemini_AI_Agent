# cloud_storage_manager.py
"""
クラウドストレージマネージャー
ローカルとクラウドストレージの透過的な連携
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudStorageManager:
    """
    クラウドストレージマネージャー

    機能:
    - ローカルとクラウドストレージの透過的なアクセス
    - 自動同期
    - キャッシュ管理
    - 複数のクラウドプロバイダー対応
    """

    def __init__(
        self,
        provider: str = "local",  # local, gcs, s3, azure
        bucket_name: Optional[str] = None,
        local_cache_dir: str = "./storage_cache",
        auto_sync: bool = True,
    ):
        """
        初期化

        Args:
            provider: ストレージプロバイダー
            bucket_name: バケット/コンテナ名
            local_cache_dir: ローカルキャッシュディレクトリ
            auto_sync: 自動同期フラグ
        """
        self.provider = provider
        self.bucket_name = bucket_name
        self.local_cache_dir = Path(local_cache_dir)
        self.auto_sync = auto_sync

        # キャッシュディレクトリ作成
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)

        # クラウドクライアント
        self.client = None
        self.bucket = None

        # 統計情報
        self.stats = {"uploads": 0, "downloads": 0, "cache_hits": 0, "cache_misses": 0}

        # プロバイダー初期化
        if provider != "local":
            self._init_cloud_provider()

        logger.info(f"✅ CloudStorageManager 初期化完了 (provider={provider})")

    def _init_cloud_provider(self):
        """クラウドプロバイダーを初期化"""
        try:
            if self.provider == "gcs":
                self._init_gcs()
            elif self.provider == "s3":
                self._init_s3()
            elif self.provider == "azure":
                self._init_azure()
            else:
                logger.warning(f"⚠️ 未サポートのプロバイダー: {self.provider}")

        except Exception as e:
            logger.error(f"❌ クラウドプロバイダー初期化エラー: {e}")
            logger.warning("⚠️ ローカルモードにフォールバック")
            self.provider = "local"

    def _init_gcs(self):
        """Google Cloud Storage初期化"""
        try:
            from google.cloud import storage

            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"✅ GCS バケット接続: {self.bucket_name}")
        except ImportError:
            logger.error("❌ google-cloud-storage パッケージがインストールされていません")
            raise

    def _init_s3(self):
        """AWS S3初期化"""
        try:
            import boto3

            self.client = boto3.client("s3")
            self.bucket_name = self.bucket_name
            logger.info(f"✅ S3 バケット接続: {self.bucket_name}")
        except ImportError:
            logger.error("❌ boto3 パッケージがインストールされていません")
            raise

    def _init_azure(self):
        """Azure Blob Storage初期化"""
        try:
            from azure.storage.blob import BlobServiceClient

            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            self.client = BlobServiceClient.from_connection_string(connection_string)
            self.bucket = self.client.get_container_client(self.bucket_name)
            logger.info(f"✅ Azure コンテナ接続: {self.bucket_name}")
        except ImportError:
            logger.error("❌ azure-storage-blob パッケージがインストールされていません")
            raise

    # ========================================
    # 基本操作（透過的API）
    # ========================================

    async def read_file(
        self, file_path: str, encoding: Optional[str] = "utf-8"
    ) -> Union[str, bytes]:
        """
        ファイルを読み込み（ローカル/クラウド透過的）

        Args:
            file_path: ファイルパス
            encoding: エンコーディング（Noneの場合はバイナリ）

        Returns:
            Union[str, bytes]: ファイル内容
        """
        try:
            # キャッシュチェック
            cached_path = self._get_cache_path(file_path)

            if cached_path.exists():
                self.stats["cache_hits"] += 1
                logger.debug(f"📦 キャッシュヒット: {file_path}")

                if encoding:
                    return await asyncio.to_thread(cached_path.read_text, encoding=encoding)
                else:
                    return await asyncio.to_thread(cached_path.read_bytes)

            self.stats["cache_misses"] += 1

            # クラウドから読み込み
            if self.provider != "local":
                content = await self._download_from_cloud(file_path)

                # キャッシュに保存
                if self.auto_sync:
                    await self._save_to_cache(file_path, content)

                if encoding and isinstance(content, bytes):
                    return content.decode(encoding)
                return content

            # ローカルから読み込み
            local_path = Path(file_path)
            if encoding:
                return await asyncio.to_thread(local_path.read_text, encoding=encoding)
            else:
                return await asyncio.to_thread(local_path.read_bytes)

        except Exception as e:
            logger.error(f"❌ ファイル読み込みエラー: {file_path} - {e}")
            raise

    async def write_file(
        self, file_path: str, content: Union[str, bytes], encoding: Optional[str] = "utf-8"
    ):
        """
        ファイルを書き込み（ローカル/クラウド透過的）

        Args:
            file_path: ファイルパス
            content: 書き込む内容
            encoding: エンコーディング
        """
        try:
            # ローカルに書き込み
            local_path = Path(file_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(content, str):
                await asyncio.to_thread(local_path.write_text, content, encoding=encoding)
            else:
                await asyncio.to_thread(local_path.write_bytes, content)

            # クラウドに同期
            if self.provider != "local" and self.auto_sync:
                await self._upload_to_cloud(file_path, content)

            # キャッシュを更新
            await self._save_to_cache(file_path, content)

            logger.debug(f"✅ ファイル書き込み成功: {file_path}")

        except Exception as e:
            logger.error(f"❌ ファイル書き込みエラー: {file_path} - {e}")
            raise

    async def file_exists(self, file_path: str) -> bool:
        """ファイルの存在確認"""
        try:
            # ローカルチェック
            if Path(file_path).exists():
                return True

            # クラウドチェック
            if self.provider != "local":
                return await self._exists_in_cloud(file_path)

            return False

        except Exception as e:
            logger.error(f"❌ 存在確認エラー: {file_path} - {e}")
            return False

    async def delete_file(self, file_path: str):
        """ファイル削除"""
        try:
            # ローカル削除
            local_path = Path(file_path)
            if local_path.exists():
                await asyncio.to_thread(local_path.unlink)

            # クラウド削除
            if self.provider != "local":
                await self._delete_from_cloud(file_path)

            # キャッシュ削除
            cached_path = self._get_cache_path(file_path)
            if cached_path.exists():
                await asyncio.to_thread(cached_path.unlink)

            logger.debug(f"✅ ファイル削除成功: {file_path}")

        except Exception as e:
            logger.error(f"❌ ファイル削除エラー: {file_path} - {e}")
            raise

    # ========================================
    # クラウド操作（プロバイダー別）
    # ========================================

    async def _download_from_cloud(self, file_path: str) -> bytes:
        """クラウドからダウンロード"""
        self.stats["downloads"] += 1

        if self.provider == "gcs":
            return await self._download_from_gcs(file_path)
        elif self.provider == "s3":
            return await self._download_from_s3(file_path)
        elif self.provider == "azure":
            return await self._download_from_azure(file_path)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _upload_to_cloud(self, file_path: str, content: Union[str, bytes]):
        """クラウドにアップロード"""
        self.stats["uploads"] += 1

        if isinstance(content, str):
            content = content.encode("utf-8")

        if self.provider == "gcs":
            await self._upload_to_gcs(file_path, content)
        elif self.provider == "s3":
            await self._upload_to_s3(file_path, content)
        elif self.provider == "azure":
            await self._upload_to_azure(file_path, content)

    async def _exists_in_cloud(self, file_path: str) -> bool:
        """クラウドでの存在確認"""
        if self.provider == "gcs":
            return await self._exists_in_gcs(file_path)
        elif self.provider == "s3":
            return await self._exists_in_s3(file_path)
        elif self.provider == "azure":
            return await self._exists_in_azure(file_path)
        return False

    async def _delete_from_cloud(self, file_path: str):
        """クラウドから削除"""
        if self.provider == "gcs":
            await self._delete_from_gcs(file_path)
        elif self.provider == "s3":
            await self._delete_from_s3(file_path)
        elif self.provider == "azure":
            await self._delete_from_azure(file_path)

    # ========================================
    # GCS操作
    # ========================================

    async def _download_from_gcs(self, file_path: str) -> bytes:
        """GCSからダウンロード"""
        blob = self.bucket.blob(file_path)
        return await asyncio.to_thread(blob.download_as_bytes)

    async def _upload_to_gcs(self, file_path: str, content: bytes):
        """GCSにアップロード"""
        blob = self.bucket.blob(file_path)
        await asyncio.to_thread(blob.upload_from_string, content)

    async def _exists_in_gcs(self, file_path: str) -> bool:
        """GCSでの存在確認"""
        blob = self.bucket.blob(file_path)
        return await asyncio.to_thread(blob.exists)

    async def _delete_from_gcs(self, file_path: str):
        """GCSから削除"""
        blob = self.bucket.blob(file_path)
        await asyncio.to_thread(blob.delete)

    # ========================================
    # S3操作
    # ========================================

    async def _download_from_s3(self, file_path: str) -> bytes:
        """S3からダウンロード"""
        response = await asyncio.to_thread(
            self.client.get_object, Bucket=self.bucket_name, Key=file_path
        )
        return response["Body"].read()

    async def _upload_to_s3(self, file_path: str, content: bytes):
        """S3にアップロード"""
        await asyncio.to_thread(
            self.client.put_object, Bucket=self.bucket_name, Key=file_path, Body=content
        )

    async def _exists_in_s3(self, file_path: str) -> bool:
        """S3での存在確認"""
        try:
            await asyncio.to_thread(self.client.head_object, Bucket=self.bucket_name, Key=file_path)
            return True
        except:
            return False

    async def _delete_from_s3(self, file_path: str):
        """S3から削除"""
        await asyncio.to_thread(self.client.delete_object, Bucket=self.bucket_name, Key=file_path)

    # ========================================
    # Azure操作
    # ========================================

    async def _download_from_azure(self, file_path: str) -> bytes:
        """Azureからダウンロード"""
        blob_client = self.bucket.get_blob_client(file_path)
        return await asyncio.to_thread(blob_client.download_blob().readall)

    async def _upload_to_azure(self, file_path: str, content: bytes):
        """Azureにアップロード"""
        blob_client = self.bucket.get_blob_client(file_path)
        await asyncio.to_thread(blob_client.upload_blob, content, overwrite=True)

    async def _exists_in_azure(self, file_path: str) -> bool:
        """Azureでの存在確認"""
        blob_client = self.bucket.get_blob_client(file_path)
        return await asyncio.to_thread(blob_client.exists)

    async def _delete_from_azure(self, file_path: str):
        """Azureから削除"""
        blob_client = self.bucket.get_blob_client(file_path)
        await asyncio.to_thread(blob_client.delete_blob)

    # ========================================
    # キャッシュ管理
    # ========================================

    def _get_cache_path(self, file_path: str) -> Path:
        """キャッシュパスを取得"""
        # ファイルパスをキャッシュディレクトリ内のパスに変換
        safe_path = file_path.replace("/", "_").replace("\\", "_")
        return self.local_cache_dir / safe_path

    async def _save_to_cache(self, file_path: str, content: Union[str, bytes]):
        """キャッシュに保存"""
        try:
            cached_path = self._get_cache_path(file_path)

            if isinstance(content, str):
                await asyncio.to_thread(cached_path.write_text, content, encoding="utf-8")
            else:
                await asyncio.to_thread(cached_path.write_bytes, content)

        except Exception as e:
            logger.warning(f"⚠️ キャッシュ保存失敗: {file_path} - {e}")

    async def clear_cache(self):
        """キャッシュをクリア"""
        try:
            for cache_file in self.local_cache_dir.glob("*"):
                await asyncio.to_thread(cache_file.unlink)

            logger.info("✅ キャッシュクリア完了")

        except Exception as e:
            logger.error(f"❌ キャッシュクリアエラー: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        cache_hit_rate = 0.0
        total_cache_ops = self.stats["cache_hits"] + self.stats["cache_misses"]

        if total_cache_ops > 0:
            cache_hit_rate = self.stats["cache_hits"] / total_cache_ops

        return {**self.stats, "cache_hit_rate": cache_hit_rate, "provider": self.provider}
