"""
Agent Coordination Protocol
Implements agent-to-agent messaging and negotiation using Hedera Consensus Service
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .hedera_integration_v2 import HederaClient


class AgentCoordinator:
    """
    Coordinates agent interactions using Hedera Consensus Service (HCS)
    Enables asynchronous negotiation, bidding, and service discovery
    """

    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera = hedera_client or HederaClient()
        self.topic_id = os.getenv('HEDERA_AGENT_COORDINATION_TOPIC_ID', '0.0.123456')  # Default topic

        # In-memory state (could be database in production)
        self.pending_intents: Dict[str, Dict] = {}  # intent_id -> intent data
        self.active_negotiations: Dict[str, Dict] = {}  # intent_id -> negotiation state
        self.intent_bids: Dict[str, List[Dict]] = {}  # intent_id -> list of bids

    async def broadcast_intent(
        self,
        agent_id: int,
        intent_type: str,
        parameters: Dict,
        deadline_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Agent broadcasts what it needs/offers to the coordination topic

        Args:
            agent_id: ID of the broadcasting agent
            intent_type: Type of intent (need_service, offer_service, buy, sell)
            parameters: Intent parameters (service type, requirements, etc.)
            deadline_hours: Hours until intent expires

        Returns:
            Intent broadcast result
        """
        try:
            intent_id = str(uuid.uuid4())
            deadline = datetime.now() + timedelta(hours=deadline_hours)

            intent_msg = {
                'intent_id': intent_id,
                'agent_id': agent_id,
                'intent_type': intent_type,  # "need_service" | "offer_service" | "buy" | "sell"
                'parameters': parameters,
                'timestamp': datetime.now().isoformat(),
                'deadline': deadline.isoformat(),
                'status': 'active'
            }

            # Submit to HCS topic (immutable, ordered, auditable)
            if self.hedera and hasattr(self.hedera, 'submit_consensus_message'):
                result = self.hedera.submit_consensus_message(
                    topic_id=self.topic_id,
                    message=json.dumps(intent_msg)
                )

                if result.get('status') == 'SUCCESS':
                    intent_msg['sequence_number'] = result.get('sequenceNumber')
                    intent_msg['transaction_id'] = result.get('transactionId')

            # Store locally
            self.pending_intents[intent_id] = intent_msg

            return {
                'status': 'SUCCESS',
                'intent_id': intent_id,
                'deadline': deadline.isoformat(),
                'message': f'Intent broadcasted successfully. Expires: {deadline.isoformat()}'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to broadcast intent'
            }

    async def submit_bid(
        self,
        intent_id: str,
        bidding_agent_id: int,
        bid_parameters: Dict
    ) -> Dict[str, Any]:
        """
        Agent submits a bid to fulfill an intent

        Args:
            intent_id: ID of the intent to bid on
            bidding_agent_id: ID of the bidding agent
            bid_parameters: Bid details (price, capacity, terms, etc.)

        Returns:
            Bid submission result
        """
        try:
            if intent_id not in self.pending_intents:
                return {
                    'status': 'ERROR',
                    'message': f'Intent {intent_id} not found or expired'
                }

            intent = self.pending_intents[intent_id]

            # Check if intent is still active
            if datetime.now() > datetime.fromisoformat(intent['deadline']):
                return {
                    'status': 'ERROR',
                    'message': f'Intent {intent_id} has expired'
                }

            bid_id = str(uuid.uuid4())
            bid_msg = {
                'bid_id': bid_id,
                'intent_id': intent_id,
                'bidding_agent_id': bidding_agent_id,
                'bid_parameters': bid_parameters,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }

            # Submit bid to HCS
            if self.hedera and hasattr(self.hedera, 'submit_consensus_message'):
                result = self.hedera.submit_consensus_message(
                    topic_id=self.topic_id,
                    message=json.dumps(bid_msg)
                )

                if result.get('status') == 'SUCCESS':
                    bid_msg['sequence_number'] = result.get('sequenceNumber')
                    bid_msg['transaction_id'] = result.get('transactionId')

            # Store bid
            if intent_id not in self.intent_bids:
                self.intent_bids[intent_id] = []
            self.intent_bids[intent_id].append(bid_msg)

            # Initialize negotiation if not exists
            if intent_id not in self.active_negotiations:
                self.active_negotiations[intent_id] = {
                    'intent': intent,
                    'bids': [bid_msg],
                    'status': 'negotiating'
                }
            else:
                self.active_negotiations[intent_id]['bids'].append(bid_msg)

            return {
                'status': 'SUCCESS',
                'bid_id': bid_id,
                'message': f'Bid submitted successfully for intent {intent_id}'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to submit bid'
            }

    async def accept_bid(
        self,
        intent_id: str,
        bid_id: str,
        accepting_agent_id: int
    ) -> Dict[str, Any]:
        """
        Accept a bid and execute the transaction

        Args:
            intent_id: ID of the intent
            bid_id: ID of the accepted bid
            accepting_agent_id: ID of the agent accepting the bid

        Returns:
            Bid acceptance result
        """
        try:
            if intent_id not in self.active_negotiations:
                return {
                    'status': 'ERROR',
                    'message': f'Negotiation for intent {intent_id} not found'
                }

            negotiation = self.active_negotiations[intent_id]
            intent = negotiation['intent']

            # Verify accepting agent owns the intent
            if intent['agent_id'] != accepting_agent_id:
                return {
                    'status': 'ERROR',
                    'message': 'Only the intent owner can accept bids'
                }

            # Find the bid
            bid = None
            for b in negotiation['bids']:
                if b['bid_id'] == bid_id:
                    bid = b
                    break

            if not bid:
                return {
                    'status': 'ERROR',
                    'message': f'Bid {bid_id} not found'
                }

            # Log acceptance on HCS for audit trail
            acceptance_msg = {
                'acceptance_id': str(uuid.uuid4()),
                'intent_id': intent_id,
                'bid_id': bid_id,
                'accepting_agent_id': accepting_agent_id,
                'accepted_bid': bid,
                'timestamp': datetime.now().isoformat(),
                'status': 'accepted'
            }

            if self.hedera and hasattr(self.hedera, 'submit_consensus_message'):
                result = self.hedera.submit_consensus_message(
                    topic_id=self.topic_id,
                    message=json.dumps(acceptance_msg)
                )

                if result.get('status') == 'SUCCESS':
                    acceptance_msg['sequence_number'] = result.get('sequenceNumber')
                    acceptance_msg['transaction_id'] = result.get('transactionId')

            # Update negotiation status
            negotiation['status'] = 'completed'
            negotiation['accepted_bid'] = bid
            negotiation['completed_at'] = datetime.now().isoformat()

            # Mark intent as fulfilled
            intent['status'] = 'fulfilled'

            return {
                'status': 'SUCCESS',
                'acceptance_id': acceptance_msg['acceptance_id'],
                'accepted_bid': bid,
                'message': f'Bid accepted. Ready for transaction execution.'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to accept bid'
            }

    async def get_pending_intents(
        self,
        agent_type_filter: Optional[str] = None,
        service_type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Query pending intents that agents can respond to

        Args:
            agent_type_filter: Filter by agent type that can fulfill
            service_type_filter: Filter by service type needed

        Returns:
            List of pending intents
        """
        try:
            intents = []
            now = datetime.now()

            for intent in self.pending_intents.values():
                # Skip expired intents
                if now > datetime.fromisoformat(intent['deadline']):
                    continue

                # Skip fulfilled intents
                if intent.get('status') == 'fulfilled':
                    continue

                # Apply filters
                if service_type_filter:
                    intent_service = intent.get('parameters', {}).get('service_type')
                    if intent_service != service_type_filter:
                        continue

                if agent_type_filter:
                    # Check if this agent type can fulfill the intent
                    if not self._can_agent_type_fulfill(agent_type_filter, intent):
                        continue

                intents.append(intent)

            return intents

        except Exception as e:
            print(f"Error getting pending intents: {e}")
            return []

    async def get_negotiation_status(self, intent_id: str) -> Optional[Dict]:
        """Get the current status of a negotiation"""
        return self.active_negotiations.get(intent_id)

    async def get_agent_bids(self, agent_id: int) -> List[Dict]:
        """Get all bids submitted by an agent"""
        bids = []
        for intent_bids in self.intent_bids.values():
            for bid in intent_bids:
                if bid['bidding_agent_id'] == agent_id:
                    bids.append(bid)
        return bids

    def _can_agent_type_fulfill(self, agent_type: str, intent: Dict) -> bool:
        """
        Check if an agent type can fulfill a given intent
        This is a simple mapping - could be more sophisticated
        """
        intent_type = intent.get('intent_type')
        service_type = intent.get('parameters', {}).get('service_type')

        # Define which agent types can fulfill which services
        capability_map = {
            'moving': ['moving-service', 'transportation'],
            'matching': ['tenant-matching', 'property-matching', 'compatibility-analysis'],
            'landlord': ['rent-optimization', 'market-analysis', 'property-management'],
            'guardian': ['payment-authorization', 'budget-monitoring'],
            'p2p-community': ['peer-recommendations', 'trust-scoring'],
            'savings': ['savings-planning', 'ownership-conversion']
        }

        if agent_type in capability_map:
            required_caps = capability_map[agent_type]
            return service_type in required_caps

        return False

    async def cleanup_expired_intents(self) -> int:
        """Clean up expired intents and negotiations"""
        now = datetime.now()
        expired_count = 0

        # Clean expired intents
        expired_intents = []
        for intent_id, intent in self.pending_intents.items():
            if now > datetime.fromisoformat(intent['deadline']):
                expired_intents.append(intent_id)
                expired_count += 1

        for intent_id in expired_intents:
            del self.pending_intents[intent_id]
            if intent_id in self.intent_bids:
                del self.intent_bids[intent_id]
            if intent_id in self.active_negotiations:
                del self.active_negotiations[intent_id]

        return expired_count

    # HCS Message Processing (would be called by a background service)
    async def process_consensus_message(self, message: str) -> None:
        """
        Process incoming HCS messages
        This would be called by a message listener service
        """
        try:
            data = json.loads(message)

            if 'intent_id' in data and 'bid_id' not in data and 'acceptance_id' not in data:
                # New intent
                self.pending_intents[data['intent_id']] = data
            elif 'bid_id' in data:
                # New bid
                intent_id = data['intent_id']
                if intent_id not in self.intent_bids:
                    self.intent_bids[intent_id] = []
                self.intent_bids[intent_id].append(data)
            elif 'acceptance_id' in data:
                # Bid acceptance
                intent_id = data['intent_id']
                if intent_id in self.active_negotiations:
                    self.active_negotiations[intent_id]['status'] = 'completed'
                    self.active_negotiations[intent_id]['completed_at'] = data['timestamp']

        except json.JSONDecodeError:
            print(f"Invalid JSON in consensus message: {message}")
        except Exception as e:
            print(f"Error processing consensus message: {e}")