"""
Telegram Signal Copy Bot - Main Bot File
Forwards messages from multiple sources to targets based on configured mappings
Supports groups, channels, and forum topics
"""

import asyncio
import re
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors.common import TypeNotFoundError
from telethon.errors import AuthKeyDuplicatedError
from telethon.tl.types import Message
import os
from config import (
    API_ID,
    API_HASH,
    PHONE_NUMBER,
    SESSION_NAME,
    FORWARD_MAPPINGS,
    FORWARD_DELAY,
    LOG_FILE,
    LOG_LEVEL,
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class _SuppressTypeNotFound(logging.Filter):
    """Suppress benign TypeNotFoundError noise from Telethon's network layer.

    This error occurs when Telegram sends a TL object type that the current
    Telethon version doesn't recognise (e.g. new API types added by Telegram).
    It is non-fatal and does not affect bot operation.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return "TypeNotFoundError" not in record.getMessage()


# Apply filter to the telethon sender logger that emits this error
logging.getLogger("telethon.network.mtprotosender").addFilter(_SuppressTypeNotFound())


# ============================================================================
# CONTACT INFO FILTER
# ============================================================================
# Messages from these source IDs that contain links, phone numbers, or
# @usernames will be skipped and NOT forwarded.
CONTACT_FILTER_SOURCES = {
    -1002871747055,  # OBIOFLAGOS FX COMMUNITY
    -1003108945324,  # Gilly Options Signals
}

# Patterns that indicate contact info in message text
_CONTACT_PATTERNS = re.compile(
    r"("
    r"https?://"  # URLs with http/https
    r"|www\.[a-zA-Z0-9]"  # URLs starting with www.
    r"|t\.me/"  # Telegram links
    r"|@[a-zA-Z0-9_]{3,}"  # @usernames
    r"|\+?[0-9][0-9 .\-]{7,}[0-9]"  # Phone numbers (8+ digits, various formats)
    r")",
    re.IGNORECASE,
)


def _contains_contact_info(text: str) -> bool:
    """Return True if text contains a URL, phone number, or @username."""
    return bool(_CONTACT_PATTERNS.search(text))


class SignalForwarder:
    """Handles message forwarding based on configured mappings"""

    def __init__(self, client: TelegramClient, mappings: list):
        self.client = client
        self.mappings = mappings
        self.source_to_targets = self._build_mapping_index()
        self.entity_names = {}  # Cache for entity names

    async def get_entity_name(self, entity_id):
        """Get and cache entity name for logging"""
        if entity_id not in self.entity_names:
            try:
                entity = await self.client.get_entity(entity_id)
                name = getattr(entity, "title", getattr(entity, "username", "Unknown"))
                self.entity_names[entity_id] = name
            except Exception:
                self.entity_names[entity_id] = "Unknown"
        return self.entity_names[entity_id]

    def _build_mapping_index(self):
        """Build an index for quick lookup of targets based on source"""
        index = {}

        for mapping in self.mappings:
            source_id = mapping["source_id"]
            source_topic_id = mapping.get("source_topic_id")

            # Create a key for this source (group or group+topic)
            if source_topic_id:
                key = f"{source_id}#{source_topic_id}"
            else:
                key = str(source_id)

            # Add target info to this source key
            if key not in index:
                index[key] = []

            index[key].append(
                {
                    "target_id": mapping["target_id"],
                    "target_topic_id": mapping.get("target_topic_id"),
                }
            )

        return index

    def get_targets_for_message(self, message: Message):
        """Get all target destinations for a given message.

        Telegram forum topics use three different structures depending on the message:
          1. Root/first message of a topic: reply_to is None, but message.id == topic_id
          2. Direct reply to topic root: reply_to.reply_to_msg_id == topic_id,
             reply_to_top_id is None (or same as reply_to_msg_id)
          3. Nested reply inside a topic: reply_to.reply_to_top_id == topic_id
        """
        source_id = (
            message.peer_id.channel_id
            if hasattr(message.peer_id, "channel_id")
            else None
        )

        if not source_id:
            return []

        # Make it negative (Telegram convention)
        source_id = -1000000000000 - source_id if source_id > 0 else source_id

        source_topic_id = None

        if message.reply_to:
            reply = message.reply_to
            # Case 3: nested reply — reply_to_top_id points to the topic root
            if getattr(reply, "reply_to_top_id", None):
                source_topic_id = reply.reply_to_top_id
            # Case 2: direct reply to topic root — only reply_to_msg_id is set
            elif getattr(reply, "reply_to_msg_id", None):
                source_topic_id = reply.reply_to_msg_id
        else:
            # Case 1: this IS the root/first message of a topic.
            # Its message.id equals the topic_id in Telegram's forum model.
            # Check if this message id matches any configured source topic for this group.
            candidate_key = f"{source_id}#{message.id}"
            if candidate_key in self.source_to_targets:
                return self.source_to_targets[candidate_key]

        # Try exact topic match
        if source_topic_id:
            key = f"{source_id}#{source_topic_id}"
            if key in self.source_to_targets:
                return self.source_to_targets[key]

        # Fall back to group-level match (no topic filter)
        key = str(source_id)
        return self.source_to_targets.get(key, [])

    async def forward_message(self, message: Message):
        """Copy message to all configured targets (without 'Forwarded from' label)"""
        targets = self.get_targets_for_message(message)

        if not targets:
            logger.debug(f"No targets configured for message from {message.peer_id}")
            return

        source_id = (
            message.peer_id.channel_id
            if hasattr(message.peer_id, "channel_id")
            else None
        )
        source_id = (
            -1000000000000 - source_id if source_id and source_id > 0 else source_id
        )

        # Get source name for logging
        source_name = await self.get_entity_name(source_id)

        # Get message preview
        msg_preview = ""
        if message.text:
            msg_preview = message.text[:50].replace("\n", " ")
            if len(message.text) > 50:
                msg_preview += "..."
        elif message.media:
            msg_preview = f"[{type(message.media).__name__}]"

        logger.info(f"📨 New message from {source_name} ({source_id}): {msg_preview}")
        logger.info(f"   Copying to {len(targets)} target(s)")

        for idx, target in enumerate(targets, 1):
            try:
                target_id = target["target_id"]
                target_topic_id = target.get("target_topic_id")

                # Get target name for logging
                target_name = await self.get_entity_name(target_id)

                # Get target entity
                target_entity = await self.client.get_entity(target_id)

                # Copy the message (not forward - no "Forwarded from" label)
                # This preserves all content: text, media, files, formatting, etc.
                if target_topic_id:
                    # Send to specific topic in forum group
                    await self.client.send_message(
                        entity=target_entity,
                        message=message.text or "",
                        file=message.media if message.media else None,
                        formatting_entities=message.entities,
                        link_preview=False,
                        reply_to=target_topic_id,  # Post in specific topic
                    )
                    logger.info(
                        f"   ✓ [{idx}/{len(targets)}] Copied to {target_name} ({target_id}) → Topic #{target_topic_id}"
                    )
                else:
                    # Send to group/channel (no specific topic)
                    await self.client.send_message(
                        entity=target_entity,
                        message=message.text or "",
                        file=message.media if message.media else None,
                        formatting_entities=message.entities,
                        link_preview=False,
                    )
                    logger.info(
                        f"   ✓ [{idx}/{len(targets)}] Copied to {target_name} ({target_id})"
                    )

                # Anti-spam delay
                await asyncio.sleep(FORWARD_DELAY)

            except Exception as e:
                # Check for protected chat restriction
                # Error format often contains: "You can't forward messages from a protected chat"
                error_str = str(e).lower()
                if (
                    "protected chat" in error_str or "sendmediarequest" in error_str
                ) and message.media:
                    logger.warning(
                        f"   ⚠️ Protected chat detected. Downloading and re-uploading media..."
                    )
                    path = None
                    try:
                        # Download media to a temp file
                        path = await message.download_media()
                        if path:
                            logger.info(f"   ⬇️ Downloaded media to {path}")

                            # Send with the downloaded file
                            if target_topic_id:
                                await self.client.send_message(
                                    entity=target_entity,
                                    message=message.text or "",
                                    file=path,
                                    formatting_entities=message.entities,
                                    link_preview=False,
                                    reply_to=target_topic_id,
                                )
                                logger.info(
                                    f"   ✓ [{idx}/{len(targets)}] Copied (via download) to {target_name} → Topic #{target_topic_id}"
                                )
                            else:
                                await self.client.send_message(
                                    entity=target_entity,
                                    message=message.text or "",
                                    file=path,
                                    formatting_entities=message.entities,
                                    link_preview=False,
                                )
                                logger.info(
                                    f"   ✓ [{idx}/{len(targets)}] Copied (via download) to {target_name}"
                                )
                        else:
                            logger.error(
                                f"   ❌ Failed to download media from protected chat"
                            )

                    except Exception as upload_e:
                        logger.error(f"   ❌ Failed to re-upload media: {upload_e}")

                    finally:
                        # Clean up
                        if path and os.path.exists(path):
                            try:
                                os.remove(path)
                                logger.debug(f"   🗑️ Deleted temp file {path}")
                            except Exception as cleanup_e:
                                logger.warning(
                                    f"   ⚠️ Failed to delete temp file {path}: {cleanup_e}"
                                )
                else:
                    logger.error(
                        f"   ❌ [{idx}/{len(targets)}] Failed to copy to {target.get('target_id', 'Unknown')}: {e}"
                    )


async def main():
    """Main bot function"""

    # Initialize client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    # Initialize forwarder
    forwarder = SignalForwarder(client, FORWARD_MAPPINGS)

    # Get all unique source IDs to monitor
    source_ids = set()
    for mapping in FORWARD_MAPPINGS:
        source_ids.add(mapping["source_id"])

    logger.info(
        f"Monitoring {len(source_ids)} source(s) with {len(FORWARD_MAPPINGS)} mapping(s)"
    )

    # Register event handler for new messages
    @client.on(events.NewMessage(chats=list(source_ids)))
    async def handle_new_message(event):
        """Handle incoming messages from monitored sources"""
        try:
            message = event.message

            # Log message details
            source_id = (
                message.peer_id.channel_id
                if hasattr(message.peer_id, "channel_id")
                else None
            )
            source_id = (
                -1000000000000 - source_id if source_id and source_id > 0 else source_id
            )

            logger.info(
                f"📨 New message from {source_id}: {message.message[:50] if message.message else '[Media]'}..."
            )

            # Skip messages with contact info from filtered sources
            if source_id in CONTACT_FILTER_SOURCES:
                text = message.message or ""
                if _contains_contact_info(text):
                    logger.info(
                        f"   ⏭️ Skipped (contact info detected) from {source_id}"
                    )
                    return

            # Forward the message
            await forwarder.forward_message(message)

        except Exception as e:
            logger.error(f"❌ Error handling message: {e}", exc_info=True)

    # Start the client (with phone number to avoid interactive prompt in Docker)
    await client.start(phone=PHONE_NUMBER)

    # Get current user info
    me = await client.get_me()
    logger.info(f"✓ Bot started as {me.first_name} (@{me.username})")
    logger.info(
        f"✓ Monitoring {len(source_ids)} source(s) with {len(FORWARD_MAPPINGS)} mapping(s)"
    )
    logger.info("=" * 80)
    logger.info("ACTIVE MAPPINGS:")
    logger.info("=" * 80)

    # Print detailed mapping summary with names
    for idx, mapping in enumerate(FORWARD_MAPPINGS, 1):
        source_id = mapping["source_id"]
        source_name = await forwarder.get_entity_name(source_id)
        source_topic_id = mapping.get("source_topic_id")

        target_id = mapping["target_id"]
        target_name = await forwarder.get_entity_name(target_id)
        target_topic_id = mapping.get("target_topic_id")

        # Build source string
        source_str = f"{source_name} ({source_id})"
        if source_topic_id:
            source_str += f" → Topic #{source_topic_id}"

        # Build target string
        target_str = f"{target_name} ({target_id})"
        if target_topic_id:
            target_str += f" → Topic #{target_topic_id}"

        logger.info(f"{idx}. {source_str}")
        logger.info(f"   ↓")
        logger.info(f"   {target_str}")
        logger.info("")

    logger.info("=" * 80)
    logger.info("✓ Waiting for messages...")
    logger.info("=" * 80)

    # Keep the bot running — auto-reconnect on TypeNotFoundError (Telegram sends
    # new TL constructor types that older Telethon builds don't recognise; this
    # is non-fatal and does NOT affect bot operation).
    #
    # AuthKeyDuplicatedError means the session was used from two different IPs at
    # the same time (e.g. overlapping deploys). The session is now revoked by
    # Telegram — reconnecting is pointless and will keep failing. We exit cleanly
    # so Fly.io restarts with a single fresh connection.
    while True:
        try:
            await client.run_until_disconnected()
            break  # clean disconnect (e.g. KeyboardInterrupt forwarded)
        except AuthKeyDuplicatedError:
            logger.error(
                "🔑 AuthKeyDuplicatedError: session used from two IPs simultaneously — "
                "session is now revoked. Exiting so it can be restarted cleanly."
            )
            raise  # let start.py / Fly.io restart the process
        except TypeNotFoundError as e:
            logger.warning(
                f"⚠️  Telethon TypeNotFoundError (unknown TL constructor — harmless): {e}. "
                "Reconnecting in 5 s..."
            )
            await asyncio.sleep(5)
            # Re-connect and keep the same handlers alive
            await client.connect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}", exc_info=True)
