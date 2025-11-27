"""
Test script to verify cricket API integration.

This helps you test and configure the API endpoints.
"""

import asyncio
from models.state import initialize_match_state
from utils.cricket_api import CricketAPIClient, poll_cricket_api


async def test_api_client():
    """Test the API client with a match."""
    print("Testing Cricket API Client...")
    print("=" * 50)
    
    state = initialize_match_state()
    client = CricketAPIClient(state.match_id)
    
    print(f"Match ID: {state.match_id}")
    print(f"Current State: {state.total_runs}/{state.wickets_lost}")
    print("\nFetching match data...")
    
    # Try to fetch data
    match_data = await client.fetch_match_data()
    
    if match_data:
        print("✅ API fetch successful!")
        print(f"Data: {match_data}")
        
        # Try to detect new event
        event = client.detect_new_event(match_data, state)
        if event:
            print(f"\n✅ New event detected: {event.event_type}")
        else:
            print("\nℹ️  No new events (state unchanged)")
    else:
        print("⚠️  API fetch failed or not configured")
        print("\nThis is normal if:")
        print("  1. API endpoints need to be configured")
        print("  2. Match is not live")
        print("  3. API structure differs from expected")
        print("\nManual JSON input still works perfectly!")


async def test_polling():
    """Test the polling mechanism."""
    print("\n" + "=" * 50)
    print("Testing Auto-Polling (5 second test)...")
    print("=" * 50)
    
    state = initialize_match_state()
    event_queue = asyncio.Queue()
    
    # Create polling task
    polling_task = asyncio.create_task(
        poll_cricket_api(state.match_id, state, event_queue, poll_interval=5)
    )
    
    # Wait a bit and check for events
    await asyncio.sleep(10)
    
    # Check queue
    events_found = 0
    while not event_queue.empty():
        event = await event_queue.get()
        print(f"✅ Event received: {event.event_type}")
        events_found += 1
    
    if events_found == 0:
        print("ℹ️  No events received (API may need configuration)")
    
    # Cancel polling
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    
    print("\n✅ Polling test complete")


if __name__ == "__main__":
    print("Cricket API Integration Test")
    print("=" * 50)
    
    # Test 1: API Client
    asyncio.run(test_api_client())
    
    # Test 2: Polling (optional, uncomment to test)
    # asyncio.run(test_polling())
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nNext steps:")
    print("1. Configure API endpoints in utils/cricket_api.py")
    print("2. Test with: python test_api_integration.py")
    print("3. Run main system: python main.py")

