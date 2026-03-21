"""
Governance Service for FIND-RLB Agent Economy
Implements decentralized governance for agent economy decisions
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User

from .hedera_integration import HederaClient
from .agent_economy_service import AgentEconomyService

logger = logging.getLogger(__name__)

class ProposalType(Enum):
    PARAMETER_UPDATE = "parameter_update"
    CONTRACT_UPGRADE = "contract_upgrade"
    AGENT_REGULATION = "agent_regulation"
    ECONOMIC_POLICY = "economic_policy"
    SYSTEM_MAINTENANCE = "system_maintenance"

class ProposalStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

@dataclass
class Proposal:
    """Governance proposal"""
    proposal_id: str
    proposer: str
    proposal_type: ProposalType
    title: str
    description: str
    parameters: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    for_votes: int
    against_votes: int
    abstain_votes: int
    status: ProposalStatus
    executed: bool
    votes: Dict[str, Dict[str, Any]]  # voter -> vote details

@dataclass
class Vote:
    """Vote details"""
    has_voted: bool
    support: bool
    weight: int
    timestamp: datetime

@dataclass
class GovernanceConfig:
    """Governance configuration"""
    voting_period: int  # seconds
    proposal_threshold: int  # minimum tokens to propose
    quorum_threshold: int  # minimum participation (basis points)
    timelock_delay: int  # delay before execution (seconds)
    execution_grace_period: int  # execution window (seconds)

class GovernanceService:
    """Decentralized governance service for agent economy"""

    def __init__(self):
        self.hedera_client = HederaClient()
        self.agent_economy = AgentEconomyService()
        self.proposals: Dict[str, Proposal] = {}
        self.voting_power: Dict[str, int] = {}
        self.last_vote_time: Dict[str, datetime] = {}

        # Default governance configuration
        self.config = GovernanceConfig(
            voting_period=7 * 24 * 3600,  # 7 days
            proposal_threshold=1000,      # 1000 tokens minimum
            quorum_threshold=1000,        # 10% quorum
            timelock_delay=2 * 24 * 3600, # 2 days timelock
            execution_grace_period=7 * 24 * 3600  # 7 days execution window
        )

        # Timelock tracking
        self.timelock_timestamps: Dict[str, datetime] = {}

    async def create_proposal(self, proposer: str, proposal_type: ProposalType,
                            title: str, description: str, parameters: Dict[str, Any]) -> str:
        """Create a new governance proposal"""

        # Check if proposer has enough tokens
        proposer_balance = await self._get_token_balance(proposer)
        if proposer_balance < self.config.proposal_threshold:
            raise ValueError(f"Insufficient tokens to create proposal. Required: {self.config.proposal_threshold}, Have: {proposer_balance}")

        proposal_id = f"prop_{len(self.proposals) + 1}_{int(datetime.now().timestamp())}"

        proposal = Proposal(
            proposal_id=proposal_id,
            proposer=proposer,
            proposal_type=proposal_type,
            title=title,
            description=description,
            parameters=parameters,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=self.config.voting_period),
            for_votes=0,
            against_votes=0,
            abstain_votes=0,
            status=ProposalStatus.ACTIVE,
            executed=False,
            votes={}
        )

        self.proposals[proposal_id] = proposal

        # Record proposal creation on blockchain
        await self._record_proposal_creation_on_chain(proposal)

        logger.info(f"Created proposal {proposal_id} by {proposer}: {title}")
        return proposal_id

    async def cast_vote(self, proposal_id: str, voter: str, support: bool) -> bool:
        """Cast a vote on a proposal"""

        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")

        proposal = self.proposals[proposal_id]

        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(f"Proposal {proposal_id} is not active")

        current_time = datetime.now()
        if current_time < proposal.start_time or current_time > proposal.end_time:
            raise ValueError(f"Voting period for proposal {proposal_id} is not open")

        if voter in proposal.votes:
            raise ValueError(f"Voter {voter} has already voted on proposal {proposal_id}")

        # Get voting weight
        voting_weight = await self._get_voting_weight(voter)

        # Record vote
        vote = Vote(
            has_voted=True,
            support=support,
            weight=voting_weight,
            timestamp=current_time
        )

        proposal.votes[voter] = {
            'has_voted': vote.has_voted,
            'support': vote.support,
            'weight': vote.weight,
            'timestamp': vote.timestamp.isoformat()
        }

        # Update vote counts
        if support:
            proposal.for_votes += voting_weight
        else:
            proposal.against_votes += voting_weight

        self.last_vote_time[voter] = current_time

        # Record vote on blockchain
        await self._record_vote_on_chain(proposal_id, voter, vote)

        logger.info(f"Vote cast on proposal {proposal_id} by {voter}: {'FOR' if support else 'AGAINST'} (weight: {voting_weight})")
        return True

    async def execute_proposal(self, proposal_id: str) -> bool:
        """Execute a successful proposal"""

        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")

        proposal = self.proposals[proposal_id]

        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(f"Proposal {proposal_id} is not active")

        current_time = datetime.now()
        if current_time <= proposal.end_time:
            raise ValueError(f"Voting period for proposal {proposal_id} is still open")

        # Calculate results
        total_votes = proposal.for_votes + proposal.against_votes + proposal.abstain_votes
        total_supply = await self._get_total_token_supply()

        quorum_reached = (total_votes * 10000) // total_supply >= self.config.quorum_threshold
        majority_support = proposal.for_votes > proposal.against_votes

        if quorum_reached and majority_support:
            proposal.status = ProposalStatus.SUCCEEDED

            # Check if timelock is required
            if self._requires_timelock(proposal.proposal_type):
                self.timelock_timestamps[proposal_id] = current_time + timedelta(seconds=self.config.timelock_delay)
                logger.info(f"Proposal {proposal_id} succeeded, timelock set for {self.config.timelock_delay} seconds")
            else:
                await self._execute_proposal_logic(proposal)
                proposal.executed = True
                proposal.status = ProposalStatus.EXECUTED

                # Record execution on blockchain
                await self._record_proposal_execution_on_chain(proposal_id)

                logger.info(f"Proposal {proposal_id} executed successfully")
                return True
        else:
            proposal.status = ProposalStatus.DEFEATED
            logger.info(f"Proposal {proposal_id} defeated - Quorum: {quorum_reached}, Majority: {majority_support}")
            return False

    async def execute_timelocked_proposal(self, proposal_id: str) -> bool:
        """Execute a timelocked proposal"""

        if proposal_id not in self.timelock_timestamps:
            raise ValueError(f"No timelock set for proposal {proposal_id}")

        timelock_time = self.timelock_timestamps[proposal_id]
        current_time = datetime.now()

        if current_time < timelock_time:
            raise ValueError(f"Timelock for proposal {proposal_id} not expired yet")

        execution_deadline = timelock_time + timedelta(seconds=self.config.execution_grace_period)
        if current_time > execution_deadline:
            raise ValueError(f"Execution window for proposal {proposal_id} has expired")

        proposal = self.proposals[proposal_id]
        if proposal.executed:
            raise ValueError(f"Proposal {proposal_id} already executed")

        await self._execute_proposal_logic(proposal)
        proposal.executed = True
        proposal.status = ProposalStatus.EXECUTED

        del self.timelock_timestamps[proposal_id]

        # Record execution on blockchain
        await self._record_proposal_execution_on_chain(proposal_id)

        logger.info(f"Timelocked proposal {proposal_id} executed successfully")
        return True

    async def update_governance_config(self, new_config: GovernanceConfig):
        """Update governance configuration (admin function)"""
        # This would typically require admin privileges
        self.config = new_config

        # Record config update on blockchain
        await self._record_config_update_on_chain(new_config)

        logger.info("Governance configuration updated")

    async def get_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get proposal details"""
        if proposal_id not in self.proposals:
            return None

        proposal = self.proposals[proposal_id]
        return {
            'proposal_id': proposal.proposal_id,
            'proposer': proposal.proposer,
            'proposal_type': proposal.proposal_type.value,
            'title': proposal.title,
            'description': proposal.description,
            'parameters': proposal.parameters,
            'start_time': proposal.start_time.isoformat(),
            'end_time': proposal.end_time.isoformat(),
            'for_votes': proposal.for_votes,
            'against_votes': proposal.against_votes,
            'abstain_votes': proposal.abstain_votes,
            'status': proposal.status.value,
            'executed': proposal.executed,
            'votes': proposal.votes
        }

    async def get_voting_weight(self, voter: str) -> int:
        """Get voting weight for an address"""
        return await self._get_voting_weight(voter)

    async def get_active_proposals(self) -> List[Dict[str, Any]]:
        """Get all active proposals"""
        active_proposals = []
        for proposal in self.proposals.values():
            if proposal.status == ProposalStatus.ACTIVE:
                active_proposals.append(await self.get_proposal(proposal.proposal_id))
        return active_proposals

    async def get_proposal_votes(self, proposal_id: str) -> Dict[str, Any]:
        """Get voting results for a proposal"""
        if proposal_id not in self.proposals:
            return {}

        proposal = self.proposals[proposal_id]
        total_votes = proposal.for_votes + proposal.against_votes + proposal.abstain_votes

        return {
            'for_votes': proposal.for_votes,
            'against_votes': proposal.against_votes,
            'abstain_votes': proposal.abstain_votes,
            'total_votes': total_votes,
            'quorum_reached': await self._check_quorum(proposal_id),
            'majority_support': proposal.for_votes > proposal.against_votes
        }

    # Private helper methods

    async def _get_token_balance(self, address: str) -> int:
        """Get governance token balance for an address"""
        # This would query the governance token contract
        # For now, return a mock value
        return 5000  # Mock balance

    async def _get_total_token_supply(self) -> int:
        """Get total governance token supply"""
        # This would query the governance token contract
        return 100000  # Mock total supply

    async def _get_voting_weight(self, voter: str) -> int:
        """Calculate voting weight for a voter"""
        # Base weight from token balance
        token_balance = await self._get_token_balance(voter)

        # Additional weight for registered agents
        try:
            agent_data = await self.agent_economy.get_agent(voter)
            if agent_data and agent_data.get('is_active', False):
                # Agents get 2x voting weight
                token_balance *= 2
                # Additional weight based on reputation
                reputation = agent_data.get('reputation', 0)
                token_balance += reputation * 100  # 1 reputation point = 100 tokens
        except Exception:
            # Not an agent, use token balance only
            pass

        return token_balance

    async def _check_quorum(self, proposal_id: str) -> bool:
        """Check if a proposal has reached quorum"""
        proposal = self.proposals[proposal_id]
        total_votes = proposal.for_votes + proposal.against_votes + proposal.abstain_votes
        total_supply = await self._get_total_token_supply()

        return (total_votes * 10000) // total_supply >= self.config.quorum_threshold

    def _requires_timelock(self, proposal_type: ProposalType) -> bool:
        """Check if proposal type requires timelock"""
        return proposal_type in [
            ProposalType.CONTRACT_UPGRADE,
            ProposalType.ECONOMIC_POLICY,
            ProposalType.SYSTEM_MAINTENANCE
        ]

    async def _execute_proposal_logic(self, proposal: Proposal):
        """Execute the logic for a successful proposal"""
        if proposal.proposal_type == ProposalType.PARAMETER_UPDATE:
            await self._execute_parameter_update(proposal.parameters)
        elif proposal.proposal_type == ProposalType.CONTRACT_UPGRADE:
            await self._execute_contract_upgrade(proposal.parameters)
        elif proposal.proposal_type == ProposalType.AGENT_REGULATION:
            await self._execute_agent_regulation(proposal.parameters)
        elif proposal.proposal_type == ProposalType.ECONOMIC_POLICY:
            await self._execute_economic_policy(proposal.parameters)
        elif proposal.proposal_type == ProposalType.SYSTEM_MAINTENANCE:
            await self._execute_system_maintenance(proposal.parameters)

    async def _execute_parameter_update(self, parameters: Dict[str, Any]):
        """Execute parameter update"""
        param_name = parameters.get('param_name')
        new_value = parameters.get('new_value')

        if param_name == 'agent_fee':
            await self.agent_economy.update_agent_fee(new_value)
        elif param_name == 'service_fee':
            await self.agent_economy.update_service_fee(new_value)
        # Add more parameter updates as needed

    async def _execute_contract_upgrade(self, parameters: Dict[str, Any]):
        """Execute contract upgrade"""
        # This would handle contract upgrades through proxy patterns
        new_contract_address = parameters.get('new_contract_address')
        upgrade_data = parameters.get('upgrade_data', {})

        # Implementation would depend on upgrade mechanism
        logger.info(f"Contract upgrade to {new_contract_address}")

    async def _execute_agent_regulation(self, parameters: Dict[str, Any]):
        """Execute agent regulation changes"""
        agent_id = parameters.get('agent_id')
        action = parameters.get('action')  # 'suspend' or 'reactivate'
        reason = parameters.get('reason', '')

        if action == 'suspend':
            await self.agent_economy.suspend_agent(agent_id, reason)
        elif action == 'reactivate':
            await self.agent_economy.reactivate_agent(agent_id)

    async def _execute_economic_policy(self, parameters: Dict[str, Any]):
        """Execute economic policy changes"""
        policy_type = parameters.get('policy_type')
        new_value = parameters.get('new_value')

        if policy_type == 'max_service_price':
            await self.agent_economy.set_max_service_price(new_value)
        elif policy_type == 'min_agent_balance':
            await self.agent_economy.set_min_agent_balance(new_value)

    async def _execute_system_maintenance(self, parameters: Dict[str, Any]):
        """Execute system maintenance operations"""
        operation = parameters.get('operation')

        if operation == 'emergency_pause':
            await self.agent_economy.emergency_pause()
        elif operation == 'emergency_unpause':
            await self.agent_economy.emergency_unpause()

    # Blockchain interaction methods (simplified)

    async def _record_proposal_creation_on_chain(self, proposal: Proposal):
        """Record proposal creation on Hedera"""
        # This would interact with the AgentGovernance smart contract
        pass

    async def _record_vote_on_chain(self, proposal_id: str, voter: str, vote: Vote):
        """Record vote on Hedera"""
        # This would interact with the AgentGovernance smart contract
        pass

    async def _record_proposal_execution_on_chain(self, proposal_id: str):
        """Record proposal execution on Hedera"""
        # This would interact with the AgentGovernance smart contract
        pass

    async def _record_config_update_on_chain(self, config: GovernanceConfig):
        """Record config update on Hedera"""
        # This would interact with the AgentGovernance smart contract
        pass