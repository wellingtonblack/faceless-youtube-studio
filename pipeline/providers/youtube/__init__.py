"""Approval-gated YouTube OAuth, private-upload and publication boundary."""

from pipeline.providers.youtube.oauth import (
    YouTubeOAuthClient,
    YouTubeOAuthError,
    access_token_from_refresh_token,
    authorize_local,
    verify_refresh_token,
)
from pipeline.providers.youtube.upload import YouTubeUploadError, private_upload_plan, upload_private_video
from pipeline.providers.youtube.publish import YouTubePublishError, public_publish_plan, publish_public_video

__all__ = (
    "YouTubeOAuthClient",
    "YouTubeOAuthError",
    "YouTubePublishError",
    "YouTubeUploadError",
    "access_token_from_refresh_token",
    "authorize_local",
    "private_upload_plan",
    "public_publish_plan",
    "publish_public_video",
    "upload_private_video",
    "verify_refresh_token",
)
