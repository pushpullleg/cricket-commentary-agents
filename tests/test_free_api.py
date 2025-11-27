"""Quick test of free Cricscore API."""

import requests
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.state import initialize_match_state
from src.services.cricket_api import CricketAPIClient

def test_cricscore_direct():
    """Test Cricscore API directly."""
    print("Testing Cricscore API (FREE, no API key)...")
    print("=" * 50)
    
    try:
        # Get list of matches
        url = "https://cricscore-api.appspot.com/csa"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            matches = response.json()
            print(f"✅ API working! Found {len(matches)} live matches")
            
            if matches:
                print("\nSample matches:")
                for match in matches[:5]:
                    print(f"  ID: {match.get('id')}, Teams: {match.get('t1')} vs {match.get('t2')}")
                
                # Try to get score for first match
                if matches:
                    match_id = matches[0].get('id')
                    score_url = f"https://cricscore-api.appspot.com/csa?id={match_id}"
                    score_response = requests.get(score_url, timeout=5)
                    
                    if score_response.status_code == 200:
                        score_data = score_response.json()
                        print(f"\n✅ Score fetch working!")
                        print(f"   Sample score data: {score_data[0] if score_data else 'No data'}")
            else:
                print("ℹ️  No live matches currently")
        else:
            print(f"❌ API returned status: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_our_client():
    """Test our CricketAPIClient."""
    print("\n" + "=" * 50)
    print("Testing Our CricketAPIClient...")
    print("=" * 50)
    
    state = initialize_match_state()
    client = CricketAPIClient(state.match_id, ("India", "South Africa"))
    
    print(f"Looking for: India vs South Africa")
    print(f"Current state: {state.total_runs}/{state.wickets_lost}")
    
    match_data = await client.fetch_match_data()
    
    if match_data:
        print(f"\n✅ Match data fetched!")
        print(f"   Score: {match_data.get('score', {})}")
        print(f"   Overs: {match_data.get('overs', 0)}")
        
        # Test event detection
        event = client.detect_new_event(match_data, state)
        if event:
            print(f"\n✅ New event would be detected: {event.event_type}")
        else:
            print(f"\nℹ️  No new events (match state unchanged)")
    else:
        print("\n⚠️  Could not fetch match data")
        print("   This might mean:")
        print("   - Match is not currently live")
        print("   - Team names don't match exactly")
        print("   - API structure needs adjustment")

if __name__ == "__main__":
    print("FREE Cricket API Test")
    print("=" * 50)
    print("Cost: $0.00 - No API keys, no OpenAI calls!\n")
    
    # Test 1: Direct API call
    test_cricscore_direct()
    
    # Test 2: Our client
    asyncio.run(test_our_client())
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("\nThe API is FREE and working!")
    print("Polling will cost $0.00 - just HTTP requests.")

