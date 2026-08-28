"""Cloud OCR engine backed by Amazon Textract or Amazon Bedrock.

The Textract path adapts the logic from the previous serverless project
(screen-snip-ocr, backend/extract_text/app.py): call DetectDocumentText with
raw image bytes and join LINE blocks. The Bedrock path uses a vision-capable
model to transcribe text, useful for handwriting or noisy images.
"""

from __future__ import annotations

import json

from .base import OcrEngine, OcrError, OcrResult

_MAX_IMAGE_BYTES = 5 * 1024 * 1024  # Textract synchronous byte limit
_BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
_BEDROCK_PROMPT = (
    "Transcribe all text visible in this image exactly as it appears. "
    "Return only the transcribed text with no commentary or explanation."
)


class AwsOcrEngine(OcrEngine):
    """Runs OCR in the cloud. Requires internet and AWS credentials."""

    name = "aws"

    def __init__(self, region: str = "us-east-1", backend: str = "textract") -> None:
        self.region = region
        self.backend = backend

    def is_available(self) -> tuple[bool, str]:
        try:
            import boto3  # noqa: F401
        except ImportError:
            return False, "boto3 is not installed."
        try:
            import botocore.session

            creds = botocore.session.get_session().get_credentials()
        except Exception:  # noqa: BLE001 - credential resolution can raise broadly
            creds = None
        if creds is None:
            return (
                False,
                "No AWS credentials found. Configure them (aws configure) to use "
                "cloud OCR.",
            )
        return True, f"AWS {self.backend} is available."

    def extract(self, image_bytes: bytes) -> OcrResult:
        if len(image_bytes) > _MAX_IMAGE_BYTES:
            raise OcrError("Captured image exceeds the 5MB cloud limit.")
        if self.backend == "bedrock":
            return self._extract_bedrock(image_bytes)
        return self._extract_textract(image_bytes)

    def _extract_textract(self, image_bytes: bytes) -> OcrResult:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client = boto3.client("textract", region_name=self.region)
        try:
            response = client.detect_document_text(Document={"Bytes": image_bytes})
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            if code == "InvalidParameterException":
                raise OcrError("Image format not supported by Textract.") from exc
            raise OcrError(f"Textract error: {code}") from exc
        except BotoCoreError as exc:
            raise OcrError(f"Could not reach Textract: {exc}") from exc

        lines = [
            block["Text"]
            for block in response.get("Blocks", [])
            if block.get("BlockType") == "LINE"
        ]
        return OcrResult(text="\n".join(lines), engine="aws:textract")

    def _extract_bedrock(self, image_bytes: bytes) -> OcrResult:
        import base64

        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client = boto3.client("bedrock-runtime", region_name=self.region)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64.b64encode(image_bytes).decode("ascii"),
                            },
                        },
                        {"type": "text", "text": _BEDROCK_PROMPT},
                    ],
                }
            ],
        }
        try:
            response = client.invoke_model(
                modelId=_BEDROCK_MODEL_ID,
                body=json.dumps(body),
            )
            payload = json.loads(response["body"].read())
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            raise OcrError(f"Bedrock error: {code}") from exc
        except BotoCoreError as exc:
            raise OcrError(f"Could not reach Bedrock: {exc}") from exc

        parts = [
            block.get("text", "")
            for block in payload.get("content", [])
            if block.get("type") == "text"
        ]
        return OcrResult(text="\n".join(parts).strip(), engine="aws:bedrock")
