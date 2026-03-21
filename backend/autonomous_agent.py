"""
Autonomous Agent Base Class
Enhanced AI agents with economic capabilities, coordination, and marketplace integration
"""

import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod

from backend.agent_economy_service import AgentEconomyService
from backend.agent_coordinator import AgentCoordinator
from backend.hedera_integration_v2 import get_hedera_client
from backend.contracts import get_contract, call_hedera_contract


class AutonomousAgent(ABC):
    """
    Base class for autonomous AI agents with economic and coordination capabilities
    """

    def __init__(
        self,
        agent_type: str,
        capabilities: List[str],
        agent_id: Optional[int] = None,
        wallet_address: Optional[str] = None
    ):
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.agent_id = agent_id
        self.wallet_address = wallet_address or self._generate_wallet_address()

        # Initialize services
        self.economy_service = AgentEconomyService()
        self.coordinator = AgentCoordinator()
        self.hedera_client = get_hedera_client()

        # Register agent if not already registered
        if not self.agent_id:
            self._register_in_economy()

        # Service offers this agent provides
        self.service_offers: Dict[int, Dict] = {}

        # Active negotiations
        self.active_negotiations: Dict[str, Dict] = {}

        # Agent state
        self.is_active = True
        self.last_activity = datetime.now()

    def _generate_wallet_address(self) -> str:
        """Generate a mock wallet address for development"""
        return f"0x{uuid.uuid4().hex[:40]}"

    def _register_in_economy(self) -> None:
        """Register this agent in the AgentEconomy"""
        result = self.economy_service.register_agent(
            agent_type=self.agent_type,
            capabilities=self.capabilities,
            wallet_address=self.wallet_address,
            initial_balance=100.0  # Starting balance for development
        )

        if result.get('status') == 'SUCCESS':
            self.agent_id = result['agent_id']
            print(f"✅ Agent {self.agent_type} registered with ID {self.agent_id}")
        else:
            print(f"❌ Failed to register agent: {result.get('message')}")

    def get_balance(self) -> float:
        """Get current HBAR balance"""
        if self.agent_id:
            return self.economy_service.get_agent_balance(self.agent_id)
        return 0.0

    def deposit_funds(self, amount: float) -> Dict[str, Any]:
        """Deposit HBAR to agent balance"""
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        return self.economy_service.deposit_to_agent(self.agent_id, amount)

    def withdraw_funds(self, amount: float) -> Dict[str, Any]:
        """Withdraw HBAR from agent balance"""
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        return self.economy_service.withdraw_from_agent(self.agent_id, amount)

    def create_service_offer(
        self,
        service_type: str,
        description: str,
        base_price: float,
        variable_fee: int = 0,
        min_order_value: float = 0
    ) -> Dict[str, Any]:
        """
        Create a service offer in the marketplace

        Args:
            service_type: Type of service (e.g., 'lease-negotiation', 'moving-service')
            description: Human-readable description
            base_price: Base price in HBAR
            variable_fee: Variable fee in basis points (100 = 1%)
            min_order_value: Minimum order value in HBAR

        Returns:
            Service offer creation result
        """
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        result = self.economy_service.create_service_offer(
            agent_id=self.agent_id,
            service_type=service_type,
            description=description,
            base_price=base_price,
            variable_fee=variable_fee,
            min_order_value=min_order_value
        )

        if result.get('status') == 'SUCCESS':
            offer_id = result['offer_id']
            self.service_offers[offer_id] = {
                'service_type': service_type,
                'description': description,
                'base_price': base_price,
                'variable_fee': variable_fee,
                'min_order_value': min_order_value,
                'created_at': datetime.now().isoformat()
            }

        return result

    async def broadcast_service_need(
        self,
        service_type: str,
        requirements: Dict,
        max_budget: float,
        deadline_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Broadcast a need for service to other agents

        Args:
            service_type: Type of service needed
            requirements: Specific requirements
            max_budget: Maximum budget in HBAR
            deadline_hours: Hours to wait for responses

        Returns:
            Intent broadcast result
        """
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        parameters = {
            'service_type': service_type,
            'requirements': requirements,
            'max_budget': max_budget
        }

        return await self.coordinator.broadcast_intent(
            agent_id=self.agent_id,
            intent_type='need_service',
            parameters=parameters,
            deadline_hours=deadline_hours
        )

    async def submit_service_bid(
        self,
        intent_id: str,
        price: float,
        terms: Dict
    ) -> Dict[str, Any]:
        """
        Submit a bid to provide service to another agent

        Args:
            intent_id: ID of the service request intent
            price: Bid price in HBAR
            terms: Bid terms and conditions

        Returns:
            Bid submission result
        """
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        bid_parameters = {
            'price': price,
            'terms': terms,
            'bidder_capabilities': self.capabilities
        }

        return await self.coordinator.submit_bid(
            intent_id=intent_id,
            bidding_agent_id=self.agent_id,
            bid_parameters=bid_parameters
        )

    async def accept_service_bid(
        self,
        intent_id: str,
        bid_id: str
    ) -> Dict[str, Any]:
        """
        Accept a bid and execute the service transaction

        Args:
            intent_id: ID of the intent
            bid_id: ID of the bid to accept

        Returns:
            Bid acceptance result
        """
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        return await self.coordinator.accept_bid(
            intent_id=intent_id,
            bid_id=bid_id,
            accepting_agent_id=self.agent_id
        )

    async def find_available_services(
        self,
        service_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Discover available services in the marketplace

        Args:
            service_type: Optional filter by service type

        Returns:
            List of available service offers
        """
        return self.economy_service.get_service_offers(service_type)

    async def purchase_service(
        self,
        offer_id: int,
        order_value: float = 0
    ) -> Dict[str, Any]:
        """
        Purchase a service from the marketplace

        Args:
            offer_id: ID of the service offer
            order_value: Value of the order for variable fee calculation

        Returns:
            Service purchase result
        """
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        return self.economy_service.execute_service(
            offer_id=offer_id,
            requestor_agent_id=self.agent_id,
            order_value=order_value
        )

    async def transfer_to_agent(
        self,
        recipient_agent_id: int,
        amount: float,
        reason: str
    ) -> Dict[str, Any]:
        """
        Transfer HBAR to another agent

        Args:
            recipient_agent_id: ID of recipient agent
            amount: Amount in HBAR
            reason: Transfer reason

        Returns:
            Transfer result
        """
        if not self.agent_id:
            return {'status': 'ERROR', 'message': 'Agent not registered'}

        return self.economy_service.transfer_between_agents(
            from_agent_id=self.agent_id,
            to_agent_id=recipient_agent_id,
            amount=amount,
            service_type=reason
        )

    async def negotiate_service(
        self,
        service_type: str,
        requirements: Dict,
        max_budget: float
    ) -> Dict[str, Any]:
        """
        Full negotiation flow: broadcast need, evaluate bids, accept best

        Args:
            service_type: Type of service needed
            requirements: Service requirements
            max_budget: Maximum budget

        Returns:
            Negotiation result
        """
        # Step 1: Broadcast service need
        intent_result = await self.broadcast_service_need(
            service_type=service_type,
            requirements=requirements,
            max_budget=max_budget
        )

        if intent_result.get('status') != 'SUCCESS':
            return intent_result

        intent_id = intent_result['intent_id']

        # Step 2: Wait for bids (in real implementation, this would be async)
        # For now, return the intent ID for manual bid evaluation
        return {
            'status': 'SUCCESS',
            'intent_id': intent_id,
            'message': f'Negotiation initiated. Intent ID: {intent_id}',
            'next_step': 'evaluate_bids'
        }

    async def evaluate_bids(self, intent_id: str) -> List[Dict]:
        """
        Evaluate bids for a negotiation

        Args:
            intent_id: ID of the negotiation intent

        Returns:
            List of bids with evaluation scores
        """
        negotiation = await self.coordinator.get_negotiation_status(intent_id)
        if not negotiation:
            return []

        bids = negotiation.get('bids', [])

        # Evaluate bids based on agent-specific criteria
        evaluated_bids = []
        for bid in bids:
            score = self._evaluate_bid(bid)
            evaluated_bids.append({
                **bid,
                'evaluation_score': score
            })

        # Sort by score (highest first)
        evaluated_bids.sort(key=lambda x: x['evaluation_score'], reverse=True)

        return evaluated_bids

    def _evaluate_bid(self, bid: Dict) -> float:
        """
        Evaluate a bid based on agent-specific criteria
        Override in subclasses for custom evaluation logic

        Returns:
            Score from 0-100
        """
        # Default evaluation: lower price is better
        price = bid.get('bid_parameters', {}).get('price', 0)
        max_budget = 1000  # Default max budget

        # Price score (lower price = higher score)
        price_score = max(0, 100 - (price / max_budget * 100))

        # Capability match score
        bidder_caps = bid.get('bid_parameters', {}).get('bidder_capabilities', [])
        cap_match = len(set(self.capabilities) & set(bidder_caps)) / len(self.capabilities) * 50

        return price_score + cap_match

    async def execute_best_bid(self, intent_id: str) -> Dict[str, Any]:
        """
        Accept the best bid for a negotiation

        Args:
            intent_id: ID of the negotiation intent

        Returns:
            Bid acceptance result
        """
        bids = await self.evaluate_bids(intent_id)
        if not bids:
            return {'status': 'ERROR', 'message': 'No bids found'}

        best_bid = bids[0]  # Already sorted by score
        return await self.accept_service_bid(intent_id, best_bid['bid_id'])

    # Legacy Hedera integration methods
    def call_contract(self, contract_name: str, function: str, params: Dict = None) -> Dict:
        """Legacy method for calling Hedera contracts"""
        return call_hedera_contract(contract_name, function, params or {})

    def get_contract_info(self, contract_name: str) -> Dict:
        """Legacy method for getting contract info"""
        return get_contract(contract_name)

    # Abstract methods that subclasses must implement
    @abstractmethod
    async def perform_core_function(self, **kwargs) -> Dict[str, Any]:
        """Core functionality of the agent"""
        pass

    @abstractmethod
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        pass

    # Utility methods
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def is_capable(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def get_service_offers_by_type(self, service_type: str) -> List[Dict]:
        """Get agent's service offers of a specific type"""
        return [offer for offer in self.service_offers.values()
                if offer['service_type'] == service_type]