"""
Script to list all forum topics (sub-groups) from both source and target Telegram groups
Uses the group IDs from config.py
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetForumTopicsRequest
from config import API_ID, API_HASH, PHONE_NUMBER, SESSION_NAME, SOURCE_GROUP_ID, TARGET_GROUP_ID


async def get_forum_topics_for_group(client, group_id, group_label):
    """Fetch and display all forum topics from a specific group"""
    
    print(f"\n{'=' * 80}")
    print(f"{group_label.upper()}")
    print(f"{'=' * 80}")
    
    try:
        # Get the channel/group entity
        channel = await client.get_entity(group_id)
        print(f"Group Name: {getattr(channel, 'title', 'Unknown')}")
        print(f"Group ID: {group_id}")
        print(f"Is Forum: {getattr(channel, 'forum', False)}")
        print(f"{'=' * 80}")
        
        # Check if it's a forum group
        if not getattr(channel, 'forum', False):
            print("\n⚠️  This group is not a forum group (no topics available)")
            return []
            
        # Fetch forum topics
        offset_date = 0
        offset_id = 0
        offset_topic = 0
        all_topics = []
        
        while True:
            result = await client(GetForumTopicsRequest(
                peer=channel,
                offset_date=offset_date,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=100
            ))
            
            if not result.topics:
                break
            
            all_topics.extend(result.topics)
            
            # Update offset for pagination
            if len(result.topics) < 100:
                break
                
            last_topic = result.topics[-1]
            offset_topic = last_topic.id
            offset_id = last_topic.top_message
            
        # Display all topics
        print(f"\n📋 Found {len(all_topics)} forum topics:\n")
        
        for idx, topic in enumerate(all_topics, 1):
            topic_id = topic.id
            topic_title = topic.title
            topic_msg_count = getattr(topic, 'replies', 0)
            is_closed = getattr(topic, 'closed', False)
            is_pinned = getattr(topic, 'pinned', False)
            
            status = []
            if is_pinned:
                status.append("📌 Pinned")
            if is_closed:
                status.append("🔒 Closed")
            
            status_str = f" [{', '.join(status)}]" if status else ""
            
            print(f"{idx}. Topic ID: {topic_id}")
            print(f"   Title: {topic_title}{status_str}")
            print(f"   Messages: {topic_msg_count}")
            print()
        
        return all_topics
        
    except ValueError as e:
        print(f"❌ Error: Could not find group with ID {group_id}")
        print(f"   Details: {e}")
        print("\n💡 Make sure the group ID in config.py is correct")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


async def main():
    """Main function to fetch topics from both source and target groups"""
    
    # Initialize the client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE_NUMBER)
        print(f"✓ Connected to Telegram as {await client.get_me()}")
        
        # Fetch topics from both groups
        source_topics = await get_forum_topics_for_group(client, SOURCE_GROUP_ID, "SOURCE GROUP")
        target_topics = await get_forum_topics_for_group(client, TARGET_GROUP_ID, "TARGET GROUP")
        
        # Display mapping suggestions
        print(f"\n{'=' * 80}")
        print("💡 TOPIC MAPPING SUGGESTIONS")
        print(f"{'=' * 80}\n")
        print("To forward messages from a source topic to a target topic, you'll need to:")
        print("1. Identify which source topics to monitor")
        print("2. Map each source topic to a corresponding target topic")
        print("\nExample mapping:")
        if source_topics and target_topics:
            print(f"  Source: {SOURCE_GROUP_ID}#<topic_id> → Target: {TARGET_GROUP_ID}#<topic_id>")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await client.disconnect()
        print("\n✓ Disconnected from Telegram")


if __name__ == '__main__':
    asyncio.run(main())
