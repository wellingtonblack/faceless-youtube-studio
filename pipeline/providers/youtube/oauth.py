"""Local OAuth 2.0 authorization for the YouTube upload adapter.

This module uses a loopback callback and PKCE.  It only requests the upload
scope, writes the resulting refresh token to the ignored local ``.env`` file,
and never prints secrets.  Upload and publication operations intentionally do
not exist here.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

from pipeline.providers.voice.elevenlabs import load_local_env_value


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


class YouTubeOAuthError(RuntimeError):
    """A safe-to-display failure from the local YouTube OAuth flow."""


@dataclass(frozen=True)
class YouTubeOAuthClient:
    """The credential pair needed for OAuth token exchange."""

    client_id: str
    client_secret: str

    @classmethod
    def from_local_environment(cls, repository_root: Path) -> "YouTubeOAuthClient":
        client_id = load_local_env_value(repository_root / ".env", "YOUTUBE_CLIENT_ID")
        client_secret = load_local_env_value(repository_root / ".env", "YOUTUBE_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise YouTubeOAuthError("YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET is missing or empty")
        return cls(client_id=client_id, client_secret=client_secret)


def authorize_local(repository_root: Path, *, timeout_seconds: float = 300.0) -> None:
    """Open the owner-controlled consent screen and save a refresh token locally."""
    client = YouTubeOAuthClient.from_local_environment(repository_root)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    state = secrets.token_urlsafe(32)
    callback = _CallbackServer(state)
    callback.start()
    try:
        redirect_uri = callback.redirect_uri
        query = urlencode({
            "client_id": client.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": YOUTUBE_UPLOAD_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        })
        authorization_url = f"{_AUTHORIZATION_ENDPOINT}?{query}"
        print("Opening the Google authorization page in your browser.")
        print("Sign in to the Google account that manages the YouTube channel and approve upload access.")
        print("No video will be uploaded and no channel settings will be changed.")
        if not webbrowser.open(authorization_url):
            print(f"If your browser did not open, visit this URL locally:\n{authorization_url}")

        code = callback.wait_for_code(timeout_seconds)
        token = _exchange_authorization_code(client, code, redirect_uri, verifier)
        refresh_token = token.get("refresh_token")
        if not isinstance(refresh_token, str) or not refresh_token:
            raise YouTubeOAuthError("Google did not return a refresh token; revoke prior access and run authorization again")
        _set_local_env_value(repository_root / ".env", "YOUTUBE_REFRESH_TOKEN", refresh_token)
    finally:
        callback.stop()


def verify_refresh_token(repository_root: Path) -> None:
    """Confirm the configured refresh token can obtain an access token; no API resource is changed."""
    client = YouTubeOAuthClient.from_local_environment(repository_root)
    refresh_token = load_local_env_value(repository_root / ".env", "YOUTUBE_REFRESH_TOKEN")
    if not refresh_token:
        raise YouTubeOAuthError("YOUTUBE_REFRESH_TOKEN is missing or empty; run 'provider youtube authorize'")
    access_token_from_refresh_token(repository_root)


def access_token_from_refresh_token(repository_root: Path) -> str:
    """Return a short-lived access token without exposing the refresh token."""
    client = YouTubeOAuthClient.from_local_environment(repository_root)
    refresh_token = load_local_env_value(repository_root / ".env", "YOUTUBE_REFRESH_TOKEN")
    if not refresh_token:
        raise YouTubeOAuthError("YOUTUBE_REFRESH_TOKEN is missing or empty; run 'provider youtube authorize'")
    payload = _post_token({
        "client_id": client.client_id,
        "client_secret": client.client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    return str(payload["access_token"])


def _exchange_authorization_code(client: YouTubeOAuthClient, code: str, redirect_uri: str, verifier: str) -> dict[str, object]:
    return _post_token({
        "code": code,
        "client_id": client.client_id,
        "client_secret": client.client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": verifier,
    })


def _post_token(form: dict[str, str]) -> dict[str, object]:
    request = Request(
        _TOKEN_ENDPOINT,
        data=urlencode(form).encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in (400, 401):
            raise YouTubeOAuthError("Google rejected the OAuth credentials or authorization grant") from error
        raise YouTubeOAuthError(f"Google OAuth request failed with HTTP {error.code}") from error
    except (URLError, TimeoutError) as error:
        raise YouTubeOAuthError("could not reach Google OAuth") from error
    except json.JSONDecodeError as error:
        raise YouTubeOAuthError("Google OAuth returned invalid JSON") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("access_token"), str):
        raise YouTubeOAuthError("Google OAuth returned an invalid token response")
    return payload


class _CallbackServer:
    def __init__(self, expected_state: str) -> None:
        self._expected_state = expected_state
        self._event = threading.Event()
        self._code: str | None = None
        self._error: str | None = None
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                values = parse_qs(urlparse(self.path).query)
                if values.get("state", [None])[0] != parent._expected_state:
                    parent._error = "OAuth callback state did not match; authorization was cancelled"
                elif values.get("error", [None])[0]:
                    parent._error = "Google authorization was denied or cancelled"
                else:
                    parent._code = values.get("code", [None])[0]
                    if not parent._code:
                        parent._error = "Google returned an OAuth callback without an authorization code"
                body = b"Authorization received. You may close this browser tab and return to the terminal."
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                parent._event.set()

            def log_message(self, _format: str, *_args: object) -> None:
                return

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def redirect_uri(self) -> str:
        return f"http://127.0.0.1:{self._server.server_port}/oauth2callback"

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)

    def wait_for_code(self, timeout_seconds: float) -> str:
        if not self._event.wait(timeout_seconds):
            raise YouTubeOAuthError("timed out waiting for Google authorization")
        if self._error:
            raise YouTubeOAuthError(self._error)
        if not self._code:
            raise YouTubeOAuthError("OAuth authorization did not return a code")
        return self._code


def _set_local_env_value(env_path: Path, variable_name: str, value: str) -> None:
    """Replace one local .env setting atomically without logging its secret value."""
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        lines = []
    prefix = f"{variable_name}="
    replacement = f"{prefix}{value}"
    replaced = False
    updated: list[str] = []
    for line in lines:
        if line.strip().startswith(prefix):
            updated.append(replacement)
            replaced = True
        else:
            updated.append(line)
    if not replaced:
        updated.append(replacement)
    temporary_path = env_path.with_suffix(".tmp")
    temporary_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
    os.replace(temporary_path, env_path)
