"""
Helper script to list all groups/channels the user is in
Run this to find the IDs for SOURCE_GROUP_ID and TARGET_GROUP_ID
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
import config

async def list_groups():
    """List all groups and channels with their IDs"""
    print("Connecting to Telegram...")
    
    client = TelegramClient(
        config.SESSION_NAME,
        config.API_ID,
        config.API_HASH
    )
    
    try:
        await client.connect()
        
        # Authenticate if needed
        if not await client.is_user_authorized():
            print("Please authenticate first by running main.py")
            return
        
        me = await client.get_me()
        print(f"\nLogged in as: {me.first_name} (@{me.username})\n")
        print("=" * 80)
        print("YOUR GROUPS AND CHANNELS:")
        print("=" * 80)
        
        groups = []
        channels = []
        
        # Get all dialogs (chats)
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            
            # Filter for groups and channels only (not private chats)
            if isinstance(entity, (Channel, Chat)):
                name = dialog.name
                chat_id = dialog.id
                
                # Determine type
                if isinstance(entity, Channel):
                    if entity.broadcast:
                        chat_type = "Channel"
                        channels.append((name, chat_id))
                    else:
                        chat_type = "Group (Supergroup)"
                        groups.append((name, chat_id))
                else:
                    chat_type = "Group"
                    groups.append((name, chat_id))
        
        # Display groups
        if groups:
            print(f"\n📁 GROUPS ({len(groups)}):")
            print("-" * 80)
            for name, chat_id in sorted(groups, key=lambda x: x[0].lower()):
                print(f"  {name}")
                print(f"  ID: {chat_id}")
                print()
        
        # Display channels
        if channels:
            print(f"\n📢 CHANNELS ({len(channels)}):")
            print("-" * 80)
            for name, chat_id in sorted(channels, key=lambda x: x[0].lower()):
                print(f"  {name}")
                print(f"  ID: {chat_id}")
                print()
        
        if not groups and not channels:
            print("\n⚠️  No groups or channels found!")
            print("Join some groups/channels first, then run this script again.")
        else:
            print("=" * 80)
            print("\n💡 USAGE:")
            print("1. Copy the ID of your SOURCE group (where signals come from)")
            print("2. Copy the ID of your TARGET group (where to forward signals)")
            print("3. Edit config.py and replace the placeholder IDs:")
            print("   SOURCE_GROUP_ID = <your_source_id>")
            print("   TARGET_GROUP_ID = <your_target_id>")
            print("\n" + "=" * 80)
    
    except Exception as e:
        print(f"Error: {e}")
        print("\nIf you haven't authenticated yet, run main.py first.")
    
    finally:
        await client.disconnect()
        print("\nDone!")

if __name__ == '__main__':
    asyncio.run(list_groups())
