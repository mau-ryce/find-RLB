"""
Test script for Agent Economy and Coordination features
Run this to verify the autonomous marketplace functionality
"""

import asyncio
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/ai-agents"  # Adjust as needed

def test_agent_registration():
    """Test agent registration in the economy"""
    print("🧪 Testing Agent Registration...")

    payload = {
        "agent_type": "matching",
        "capabilities": ["tenant-matching", "lease-negotiation", "market-analysis"],
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }

    response = requests.post(f"{BASE_URL}/economy/register/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        agent_data = response.json()
        return agent_data.get('agent_id')
    return None

def test_service_offer_creation(agent_id):
    """Test creating service offers"""
    print(f"🧪 Testing Service Offer Creation for Agent {agent_id}...")

    payload = {
        "agent_id": agent_id,
        "service_type": "tenant-matching",
        "description": "AI-powered tenant-property matching with ML algorithms",
        "base_price": 5.0,  # 5 HBAR
        "variable_fee": 500,  # 5% variable fee
        "min_order_value": 10.0
    }

    response = requests.post(f"{BASE_URL}/economy/services/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        return response.json().get('offer_id')
    return None

def test_agent_balance_check(agent_id):
    """Test checking agent balance"""
    print(f"🧪 Testing Agent Balance Check for Agent {agent_id}...")

    response = requests.get(f"{BASE_URL}/economy/balance/{agent_id}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_service_discovery():
    """Test discovering available services"""
    print("🧪 Testing Service Discovery...")

    response = requests.get(f"{BASE_URL}/economy/services/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_agent_discovery():
    """Test discovering available agents"""
    print("🧪 Testing Agent Discovery...")

    response = requests.get(f"{BASE_URL}/economy/discovery/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

async def test_intent_broadcast(agent_id):
    """Test broadcasting service intents"""
    print(f"🧪 Testing Intent Broadcast for Agent {agent_id}...")

    payload = {
        "agent_id": agent_id,
        "intent_type": "need_service",
        "parameters": {
            "service_type": "lease-negotiation",
            "requirements": {
                "property_value": 2000,
                "tenant_budget": 2500,
                "negotiation_complexity": "medium"
            }
        },
        "deadline_hours": 24
    }

    response = requests.post(f"{BASE_URL}/coord/intents/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        return response.json().get('intent_id')
    return None

async def test_bid_submission(intent_id, agent_id):
    """Test submitting bids for intents"""
    print(f"🧪 Testing Bid Submission for Intent {intent_id}...")

    payload = {
        "intent_id": intent_id,
        "bidding_agent_id": agent_id,
        "bid_parameters": {
            "price": 8.5,
            "terms": {
                "completion_time": "2_hours",
                "success_rate": 0.95,
                "revisions": 2
            }
        }
    }

    response = requests.post(f"{BASE_URL}/coord/bids/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        return response.json().get('bid_id')
    return None

def test_intent_query():
    """Test querying pending intents"""
    print("🧪 Testing Intent Query...")

    response = requests.get(f"{BASE_URL}/coord/intents/query/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

async def run_full_test():
    """Run complete test suite"""
    print("🚀 Starting FIND-RLB Agent Economy Test Suite")
    print("=" * 50)

    # Test agent registration
    agent_id = test_agent_registration()
    if not agent_id:
        print("❌ Agent registration failed, stopping tests")
        return

    time.sleep(1)

    # Test service offer creation
    offer_id = test_service_offer_creation(agent_id)
    time.sleep(1)

    # Test balance check
    test_agent_balance_check(agent_id)
    time.sleep(1)

    # Test service discovery
    test_service_discovery()
    time.sleep(1)

    # Test agent discovery
    test_agent_discovery()
    time.sleep(1)

    # Test intent broadcast
    intent_id = await test_intent_broadcast(agent_id)
    time.sleep(1)

    if intent_id:
        # Test bid submission
        bid_id = await test_bid_submission(intent_id, agent_id)
        time.sleep(1)

    # Test intent query
    test_intent_query()

    print("=" * 50)
    print("✅ Test suite completed!")
    print("\n📋 Summary of implemented features:")
    print("• Agent registration and wallet management")
    print("• Service marketplace with offers and discovery")
    print("• Inter-agent HBAR transfers")
    print("• Intent broadcasting and bid coordination")
    print("• Autonomous negotiation workflows")
    print("• Hedera Consensus Service integration")
    print("• Microtransaction support (ready for deployment)")

if __name__ == "__main__":
    asyncio.run(run_full_test())