"""
Agent Economy Service
Implements the agent marketplace and economic coordination layer
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

from .hedera_integration_v2 import HederaClient
from .contracts import CONTRACTS


class AgentEconomyService:
    """
    Service for managing agent-to-agent economic interactions on Hedera
    """

    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera = hedera_client or HederaClient()
        self.contract_id = os.getenv('HEDERA_AGENT_ECONOMY_CONTRACT_ID', CONTRACTS.get('AgentEconomy', {}).get('hedera_id'))

        # Agent registry (in-memory for now, could be database)
        self.agent_registry: Dict[int, Dict] = {}
        self.service_offers: Dict[int, Dict] = {}
        self.next_agent_id = 1
        self.next_offer_id = 1

    def register_agent(
        self,
        agent_type: str,
        capabilities: List[str],
        wallet_address: str,
        initial_balance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Register a new AI agent in the economy

        Args:
            agent_type: Type of agent (matching, moving, guardian, etc.)
            capabilities: List of service capabilities
            wallet_address: Hedera wallet address
            initial_balance: Initial HBAR balance

        Returns:
            Registration result
        """
        try:
            # Call AgentEconomy contract
            if self.contract_id and self.hedera:
                result = self.hedera.call_contract(
                    contract_id=self.contract_id,
                    function_name='registerAgent',
                    parameters={
                        'agentType': agent_type,
                        'capabilities': capabilities,
                        'walletAddress': wallet_address
                    }
                )

                if result.get('status') == 'SUCCESS':
                    agent_id = int(result.get('agentId', self.next_agent_id))
                    self.next_agent_id = max(self.next_agent_id, agent_id + 1)

                    # Store locally
                    self.agent_registry[agent_id] = {
                        'agent_id': agent_id,
                        'agent_type': agent_type,
                        'capabilities': capabilities,
                        'wallet_address': wallet_address,
                        'balance': initial_balance,
                        'reputation': 50,
                        'staked_amount': 0,
                        'is_active': True,
                        'registered_at': datetime.now().isoformat(),
                        'last_activity': datetime.now().isoformat()
                    }

                    return {
                        'status': 'SUCCESS',
                        'agent_id': agent_id,
                        'message': f'Agent registered successfully with ID {agent_id}'
                    }

            # Fallback: Register locally only
            agent_id = self.next_agent_id
            self.next_agent_id += 1

            self.agent_registry[agent_id] = {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'capabilities': capabilities,
                'wallet_address': wallet_address,
                'balance': initial_balance,
                'reputation': 50,
                'staked_amount': 0,
                'is_active': True,
                'registered_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }

            return {
                'status': 'SUCCESS',
                'agent_id': agent_id,
                'message': f'Agent registered locally with ID {agent_id}'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to register agent'
            }

    def create_service_offer(
        self,
        agent_id: int,
        service_type: str,
        description: str,
        base_price: float,
        variable_fee: int = 0,  # basis points (100 = 1%)
        min_order_value: float = 0
    ) -> Dict[str, Any]:
        """
        Create a service offer that other agents can purchase

        Args:
            agent_id: ID of the offering agent
            service_type: Type of service offered
            description: Human-readable description
            base_price: Base price in HBAR
            variable_fee: Variable fee in basis points
            min_order_value: Minimum order value in HBAR

        Returns:
            Service offer creation result
        """
        try:
            if agent_id not in self.agent_registry:
                return {
                    'status': 'ERROR',
                    'message': f'Agent {agent_id} not registered'
                }

            # Convert prices to tinybars (1 HBAR = 10^8 tinybars)
            base_price_tinybars = int(base_price * 10**8)
            min_order_tinybars = int(min_order_value * 10**8)

            # Call contract
            if self.contract_id and self.hedera:
                result = self.hedera.call_contract(
                    contract_id=self.contract_id,
                    function_name='createServiceOffer',
                    parameters={
                        'agentId': agent_id,
                        'serviceType': service_type,
                        'description': description,
                        'basePrice': base_price_tinybars,
                        'variableFee': variable_fee,
                        'minOrderValue': min_order_tinybars
                    }
                )

                if result.get('status') == 'SUCCESS':
                    offer_id = int(result.get('offerId', self.next_offer_id))
                    self.next_offer_id = max(self.next_offer_id, offer_id + 1)

                    self.service_offers[offer_id] = {
                        'offer_id': offer_id,
                        'agent_id': agent_id,
                        'service_type': service_type,
                        'description': description,
                        'base_price': base_price,
                        'variable_fee': variable_fee,
                        'min_order_value': min_order_value,
                        'is_active': True,
                        'created_at': datetime.now().isoformat(),
                        'total_transactions': 0,
                        'total_revenue': 0.0
                    }

                    return {
                        'status': 'SUCCESS',
                        'offer_id': offer_id,
                        'message': f'Service offer created with ID {offer_id}'
                    }

            # Fallback: Create locally
            offer_id = self.next_offer_id
            self.next_offer_id += 1

            self.service_offers[offer_id] = {
                'offer_id': offer_id,
                'agent_id': agent_id,
                'service_type': service_type,
                'description': description,
                'base_price': base_price,
                'variable_fee': variable_fee,
                'min_order_value': min_order_value,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'total_transactions': 0,
                'total_revenue': 0.0
            }

            return {
                'status': 'SUCCESS',
                'offer_id': offer_id,
                'message': f'Service offer created locally with ID {offer_id}'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to create service offer'
            }

    def execute_service(
        self,
        offer_id: int,
        requestor_agent_id: int,
        order_value: float
    ) -> Dict[str, Any]:
        """
        Execute a service by purchasing it from another agent

        Args:
            offer_id: ID of the service offer
            requestor_agent_id: ID of the requesting agent
            order_value: Value of the order for variable fee calculation

        Returns:
            Service execution result
        """
        try:
            if offer_id not in self.service_offers:
                return {
                    'status': 'ERROR',
                    'message': f'Service offer {offer_id} not found'
                }

            if requestor_agent_id not in self.agent_registry:
                return {
                    'status': 'ERROR',
                    'message': f'Requestor agent {requestor_agent_id} not registered'
                }

            offer = self.service_offers[offer_id]
            requestor = self.agent_registry[requestor_agent_id]

            if not offer['is_active']:
                return {
                    'status': 'ERROR',
                    'message': f'Service offer {offer_id} is not active'
                }

            if order_value < offer['min_order_value']:
                return {
                    'status': 'ERROR',
                    'message': f'Order value {order_value} below minimum {offer["min_order_value"]}'
                }

            # Calculate total price
            variable_amount = (order_value * offer['variable_fee']) / 10000  # basis points to decimal
            total_price = offer['base_price'] + variable_amount

            if requestor['balance'] < total_price:
                return {
                    'status': 'ERROR',
                    'message': f'Insufficient balance. Required: {total_price}, Available: {requestor["balance"]}'
                }

            # Execute transaction
            order_value_tinybars = int(order_value * 10**8)

            if self.contract_id and self.hedera:
                result = self.hedera.call_contract(
                    contract_id=self.contract_id,
                    function_name='executeService',
                    parameters={
                        'offerId': offer_id,
                        'requestorAgentId': requestor_agent_id,
                        'orderValue': order_value_tinybars
                    }
                )

                if result.get('status') == 'SUCCESS':
                    # Update local state
                    self.agent_registry[requestor_agent_id]['balance'] -= total_price
                    self.agent_registry[offer['agent_id']]['balance'] += total_price
                    self.service_offers[offer_id]['total_transactions'] += 1
                    self.service_offers[offer_id]['total_revenue'] += total_price

                    # Update activity timestamps
                    self.agent_registry[requestor_agent_id]['last_activity'] = datetime.now().isoformat()
                    self.agent_registry[offer['agent_id']]['last_activity'] = datetime.now().isoformat()

                    return {
                        'status': 'SUCCESS',
                        'total_price': total_price,
                        'transaction_id': result.get('transactionId'),
                        'message': f'Service executed successfully for {total_price} HBAR'
                    }

            # Fallback: Execute locally
            self.agent_registry[requestor_agent_id]['balance'] -= total_price
            self.agent_registry[offer['agent_id']]['balance'] += total_price
            self.service_offers[offer_id]['total_transactions'] += 1
            self.service_offers[offer_id]['total_revenue'] += total_price

            return {
                'status': 'SUCCESS',
                'total_price': total_price,
                'message': f'Service executed locally for {total_price} HBAR'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to execute service'
            }

    def transfer_between_agents(
        self,
        from_agent_id: int,
        to_agent_id: int,
        amount: float,
        service_type: str = "direct_transfer"
    ) -> Dict[str, Any]:
        """
        Direct HBAR transfer between agents

        Args:
            from_agent_id: Sending agent ID
            to_agent_id: Receiving agent ID
            amount: Amount in HBAR
            service_type: Description of transfer reason

        Returns:
            Transfer result
        """
        try:
            if from_agent_id not in self.agent_registry or to_agent_id not in self.agent_registry:
                return {
                    'status': 'ERROR',
                    'message': 'One or both agents not registered'
                }

            from_agent = self.agent_registry[from_agent_id]
            to_agent = self.agent_registry[to_agent_id]

            if from_agent['balance'] < amount:
                return {
                    'status': 'ERROR',
                    'message': f'Insufficient balance. Required: {amount}, Available: {from_agent["balance"]}'
                }

            # Convert to tinybars
            amount_tinybars = int(amount * 10**8)

            # Execute transfer
            if self.contract_id and self.hedera:
                result = self.hedera.call_contract(
                    contract_id=self.contract_id,
                    function_name='transferBetweenAgents',
                    parameters={
                        'fromAgentId': from_agent_id,
                        'toAgentId': to_agent_id,
                        'amount': amount_tinybars,
                        'serviceType': service_type
                    }
                )

                if result.get('status') == 'SUCCESS':
                    # Update balances
                    self.agent_registry[from_agent_id]['balance'] -= amount
                    self.agent_registry[to_agent_id]['balance'] += amount

                    return {
                        'status': 'SUCCESS',
                        'amount': amount,
                        'transaction_id': result.get('transactionId'),
                        'message': f'Transfer completed: {amount} HBAR from agent {from_agent_id} to {to_agent_id}'
                    }

            # Fallback: Transfer locally
            self.agent_registry[from_agent_id]['balance'] -= amount
            self.agent_registry[to_agent_id]['balance'] += amount

            return {
                'status': 'SUCCESS',
                'amount': amount,
                'message': f'Transfer completed locally: {amount} HBAR from agent {from_agent_id} to {to_agent_id}'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': 'Failed to transfer between agents'
            }

    def get_agent_balance(self, agent_id: int) -> float:
        """Get agent balance"""
        if agent_id in self.agent_registry:
            return self.agent_registry[agent_id]['balance']
        return 0.0

    def get_agent_info(self, agent_id: int) -> Optional[Dict]:
        """Get agent information"""
        return self.agent_registry.get(agent_id)

    def get_service_offers(self, service_type: Optional[str] = None) -> List[Dict]:
        """Get service offers, optionally filtered by type"""
        offers = list(self.service_offers.values())
        if service_type:
            offers = [o for o in offers if o['service_type'] == service_type and o['is_active']]
        else:
            offers = [o for o in offers if o['is_active']]
        return offers

    def get_agents_by_type(self, agent_type: str) -> List[Dict]:
        """Get all agents of a specific type"""
        return [agent for agent in self.agent_registry.values()
                if agent['agent_type'] == agent_type and agent['is_active']]

    def deposit_to_agent(self, agent_id: int, amount: float) -> Dict[str, Any]:
        """Deposit HBAR to agent balance"""
        try:
            if agent_id not in self.agent_registry:
                return {'status': 'ERROR', 'message': 'Agent not found'}

            self.agent_registry[agent_id]['balance'] += amount
            return {
                'status': 'SUCCESS',
                'new_balance': self.agent_registry[agent_id]['balance'],
                'message': f'Deposited {amount} HBAR to agent {agent_id}'
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}

    def withdraw_from_agent(self, agent_id: int, amount: float) -> Dict[str, Any]:
        """Withdraw HBAR from agent balance"""
        try:
            if agent_id not in self.agent_registry:
                return {'status': 'ERROR', 'message': 'Agent not found'}

            agent = self.agent_registry[agent_id]
            if agent['balance'] < amount:
                return {'status': 'ERROR', 'message': 'Insufficient balance'}

            agent['balance'] -= amount
            return {
                'status': 'SUCCESS',
                'new_balance': agent['balance'],
                'message': f'Withdrew {amount} HBAR from agent {agent_id}'
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}