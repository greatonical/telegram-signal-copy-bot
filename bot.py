"""
Telegram Signal Copy Bot - Main Bot File
Forwards messages from multiple sources to targets based on configured mappings
Supports groups, channels, and forum topics
"""

import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Message
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
        """Get all target destinations for a given message"""
        source_id = (
            message.peer_id.channel_id
            if hasattr(message.peer_id, "channel_id")
            else None
        )

        if not source_id:
            return []

        # Make it negative (Telegram convention)
        source_id = -1000000000000 - source_id if source_id > 0 else source_id

        # Check if message has a topic (reply_to with reply_to_top_id)
        source_topic_id = None
        if message.reply_to and hasattr(message.reply_to, "reply_to_top_id"):
            source_topic_id = message.reply_to.reply_to_top_id
        elif (
            message.reply_to
            and hasattr(message.reply_to, "forum_topic")
            and message.reply_to.forum_topic
        ):
            # Some messages might have the topic in a different field
            source_topic_id = message.reply_to.reply_to_msg_id

        # Try to find exact match (group + topic)
        if source_topic_id:
            key = f"{source_id}#{source_topic_id}"
            if key in self.source_to_targets:
                return self.source_to_targets[key]

        # Fall back to group-level match
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

    # Keep the bot running
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}", exc_info=True)
