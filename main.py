"""
Telegram Signal Bot - Main Script
Monitors a signal group and forwards messages to a target group
"""
import asyncio
import logging
import sys
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError,
    SessionPasswordNeededError,
    ChannelPrivateError,
    RPCError
)
from telethon.tl.types import MessageActionEmpty

import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SignalBot:
    """Telegram Signal Forwarder Bot"""
    
    def __init__(self):
        """Initialize the bot with Telethon client"""
        self.client = TelegramClient(
            config.SESSION_NAME,
            config.API_ID,
            config.API_HASH
        )
        self.source_group = config.SOURCE_GROUP_ID
        self.target_group = config.TARGET_GROUP_ID
        self.forward_delay = config.FORWARD_DELAY
        
    async def start(self):
        """Connect and authenticate with Telegram"""
        logger.info("Starting Telegram Signal Bot...")
        
        try:
            # Connect to Telegram
            await self.client.connect()
            
            # Check if user is authorized
            if not await self.client.is_user_authorized():
                logger.info("First time login detected. Please authenticate.")
                await self._authenticate()
            else:
                logger.info("Session loaded successfully.")
            
            # Get user info
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} (@{me.username})")
            
            # Verify group access
            await self._verify_group_access()
            
            # Register event handlers
            self.client.add_event_handler(
                self._handle_new_message,
                events.NewMessage(chats=[self.source_group])
            )
            
            logger.info(f"Monitoring group {self.source_group} for new signals...")
            logger.info(f"Forwarding to group {self.target_group}")
            logger.info("Bot is running. Press Ctrl+C to stop.")
            
            # Keep the bot running
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()
    
    async def _authenticate(self):
        """Handle first-time authentication"""
        try:
            # Send OTP code
            await self.client.send_code_request(config.PHONE_NUMBER)
            logger.info(f"OTP code sent to {config.PHONE_NUMBER}")
            
            # Ask for the code
            code = input("Enter the code you received: ")
            
            try:
                await self.client.sign_in(config.PHONE_NUMBER, code)
            except SessionPasswordNeededError:
                # 2FA is enabled
                logger.warning("2FA is enabled on this account")
                password = input("Enter your 2FA password: ")
                await self.client.sign_in(password=password)
            
            logger.info("Authentication successful!")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def _verify_group_access(self):
        """Verify bot has access to source and target groups"""
        try:
            # Check source group
            source = await self.client.get_entity(self.source_group)
            logger.info(f"Source group verified: {getattr(source, 'title', 'Unknown')}")
            
            # Check target group
            target = await self.client.get_entity(self.target_group)
            logger.info(f"Target group verified: {getattr(target, 'title', 'Unknown')}")
            
        except ChannelPrivateError as e:
            logger.error(f"Cannot access group (not a member?): {e}")
            raise
        except Exception as e:
            logger.error(f"Group verification failed: {e}")
            raise
    
    async def _handle_new_message(self, event):
        """Handle new messages in the source group"""
        try:
            message = event.message
            
            # Filter: Ignore system messages
            if message.action and not isinstance(message.action, MessageActionEmpty):
                logger.debug(f"Ignoring system message: {type(message.action).__name__}")
                return
            
            # Filter: Only process text messages for MVP
            if not message.text:
                logger.debug(f"Ignoring non-text message (ID: {message.id})")
                return
            
            # Log the signal
            preview = message.text[:50].replace('\n', ' ')
            logger.info(f"New signal received (ID: {message.id}): {preview}...")
            
            # Forward the message
            await self._forward_message(message)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _forward_message(self, message):
        """Forward message to target group with rate limiting"""
        try:
            # Rate limiting delay
            if self.forward_delay > 0:
                logger.debug(f"Waiting {self.forward_delay}s before forwarding...")
                await asyncio.sleep(self.forward_delay)
            
            # Send message (copy, not forward with attribution)
            await self.client.send_message(
                self.target_group,
                message.text
            )
            
            logger.info(f"Message {message.id} forwarded successfully to {self.target_group}")
            
        except FloodWaitError as e:
            # Rate limit hit - wait and retry
            wait_time = e.seconds
            logger.warning(f"FloodWait: Telegram requires waiting {wait_time} seconds")
            await asyncio.sleep(wait_time)
            
            # Retry once
            logger.info("Retrying forward after FloodWait...")
            await self.client.send_message(self.target_group, message.text)
            logger.info(f"Message {message.id} forwarded after retry")
            
        except ChannelPrivateError:
            logger.error(f"Cannot forward: No access to target group {self.target_group}")
        except RPCError as e:
            logger.error(f"Telegram API error while forwarding: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while forwarding: {e}", exc_info=True)
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Shutting down bot...")
        if self.client.is_connected():
            await self.client.disconnect()
        logger.info("Bot shut down successfully")


async def main():
    """Main entry point"""
    try:
        bot = SignalBot()
        await bot.start()
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    # Run the bot
    asyncio.run(main())
