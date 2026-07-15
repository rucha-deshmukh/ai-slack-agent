"""Slack Bolt app entrypoint (Socket Mode)."""

from __future__ import annotations

import logging
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.agent import run_agent
from app.config import get_settings
from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def _strip_mention(text: str) -> str:
    """Remove a leading <@USERID> mention from the message text."""
    return re.sub(r"^\s*<@[\w]+>\s*", "", text).strip()


def build_app() -> App:
    settings = get_settings()
    app = App(token=settings.slack_bot_token)

    @app.event("app_mention")
    def handle_mention(event, say):
        _respond(event, say)

    @app.event("message")
    def handle_dm(event, say):
        # Only respond to direct messages, and ignore the bot's own messages.
        if event.get("channel_type") == "im" and not event.get("bot_id"):
            _respond(event, say)

    def _respond(event, say):
        question = _strip_mention(event.get("text", ""))
        if not question:
            say("Hi! Ask me about product stock or the weather.")
            return
        try:
            reply = run_agent(question)
        except Exception:
            logger.exception("agent failed")
            reply = "Sorry, something went wrong handling that."
        say(reply)

    return app


def main() -> None:
    settings = get_settings()
    app = build_app()
    handler = SocketModeHandler(app, settings.slack_app_token)
    logger.info("starting ai-slack-agent in Socket Mode")
    handler.start()


if __name__ == "__main__":
    main()
