from __future__ import annotations

import json
from functools import lru_cache
from urllib.parse import quote

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.infrastructure.config.settings import Settings, get_settings


class S3Storage:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._bucket_ready = False
        self._client: BaseClient = boto3.client(
            "s3",
            endpoint_url=self._settings.s3_endpoint,
            aws_access_key_id=self._settings.s3_access_key,
            aws_secret_access_key=self._settings.s3_secret_key,
            region_name=self._settings.s3_region,
            config=Config(
                s3={"addressing_style": "path"},
                connect_timeout=10,
                read_timeout=30,
                retries={"max_attempts": 3, "mode": "standard"},
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        )

    def ensure_bucket(self) -> None:
        if self._bucket_ready:
            return
        bucket = self._settings.s3_bucket
        try:
            self._client.head_bucket(Bucket=bucket)
        except ClientError:
            self._client.create_bucket(Bucket=bucket)
        self._client.put_bucket_policy(
            Bucket=bucket,
            Policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicRead",
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket}/*"],
                        }
                    ],
                }
            ),
        )
        self._bucket_ready = True

    def public_url(self, key: str) -> str:
        endpoint = self._settings.s3_public_endpoint.rstrip("/")
        bucket = self._settings.s3_bucket
        return f"{endpoint}/{bucket}/{quote(key)}"

    def put(self, key: str, body: bytes, content_type: str) -> str:
        self.ensure_bucket()
        self._client.put_object(
            Bucket=self._settings.s3_bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
        )
        return self.public_url(key)

    def delete(self, key: str) -> None:
        self._client.delete_object(
            Bucket=self._settings.s3_bucket,
            Key=key,
        )


@lru_cache
def get_s3_storage() -> S3Storage:
    return S3Storage()


def try_ensure_bucket() -> None:
    try:
        get_s3_storage().ensure_bucket()
    except (BotoCoreError, ClientError, OSError):
        return
