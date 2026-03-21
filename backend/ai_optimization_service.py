"""
AI Optimization Service for FIND-RLB Agent Economy
Implements reinforcement learning algorithms for agent decision-making optimization
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

from django.conf import settings
from django.core.cache import cache
from django.db import models

from .hedera_integration import HederaClient
from .agent_economy_service import AgentEconomyService

logger = logging.getLogger(__name__)

@dataclass
class Experience:
    """Experience tuple for reinforcement learning"""
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any]
    timestamp: datetime

@dataclass
class LearningModel:
    """Reinforcement learning model configuration"""
    model_id: str
    agent_id: str
    model_type: str  # 'pricing', 'negotiation', 'matching', 'resource-allocation'
    parameters: Dict[str, Any]
    version: int
    accuracy: float
    training_data_points: int
    last_updated: datetime
    is_active: bool

class QLearningModel:
    """Q-Learning implementation for agent optimization"""

    def __init__(self, state_space_size: int, action_space_size: int, learning_rate: float = 0.1, discount_factor: float = 0.9, exploration_rate: float = 0.1):
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        # Initialize Q-table
        self.q_table = np.zeros((state_space_size, action_space_size))

        # Experience replay buffer
        self.experience_buffer: List[Experience] = []
        self.buffer_size = 1000

    def get_action(self, state: int, explore: bool = True) -> int:
        """Get action using epsilon-greedy policy"""
        if explore and np.random.random() < self.exploration_rate:
            return np.random.randint(self.action_space_size)
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-table using Q-learning update rule"""
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])

        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state, action] = new_q

    def add_experience(self, experience: Experience):
        """Add experience to replay buffer"""
        self.experience_buffer.append(experience)
        if len(self.experience_buffer) > self.buffer_size:
            self.experience_buffer.pop(0)

    def train_from_experiences(self, batch_size: int = 32):
        """Train model using experience replay"""
        if len(self.experience_buffer) < batch_size:
            return

        # Sample random batch from experience buffer
        batch_indices = np.random.choice(len(self.experience_buffer), batch_size, replace=False)
        batch = [self.experience_buffer[i] for i in batch_indices]

        for experience in batch:
            # Convert states to discrete values (simplified)
            state_idx = self._state_to_index(experience.state)
            next_state_idx = self._state_to_index(experience.next_state)
            action_idx = self._action_to_index(experience.action)

            self.update_q_table(state_idx, action_idx, experience.reward, next_state_idx)

    def _state_to_index(self, state: Dict[str, Any]) -> int:
        """Convert state dict to discrete index (simplified)"""
        # This is a simplified discretization - in practice, you'd use more sophisticated methods
        if 'price' in state:
            price = state['price']
            return min(int(price / 10), self.state_space_size - 1)
        elif 'competition_level' in state:
            return min(state['competition_level'], self.state_space_size - 1)
        return 0

    def _action_to_index(self, action: Dict[str, Any]) -> int:
        """Convert action dict to discrete index (simplified)"""
        if 'price_adjustment' in action:
            adjustment = action['price_adjustment']
            return min(max(int(adjustment / 5) + 5, 0), self.action_space_size - 1)
        elif 'bid_percentage' in action:
            percentage = action['bid_percentage']
            return min(int(percentage / 10), self.action_space_size - 1)
        return 0

class AIOptimizationService:
    """AI Optimization Service for agent economy"""

    def __init__(self):
        self.hedera_client = HederaClient()
        self.agent_economy = AgentEconomyService()
        self.models: Dict[str, LearningModel] = {}
        self.q_models: Dict[str, QLearningModel] = {}
        self.experiences: Dict[str, List[Experience]] = defaultdict(list)

        # RL hyperparameters
        self.hyperparams = {
            'learning_rate': 0.1,
            'discount_factor': 0.9,
            'exploration_rate': 0.1
        }

    async def create_learning_model(self, agent_id: str, model_type: str, initial_params: Dict[str, Any]) -> str:
        """Create a new learning model for an agent"""
        model_id = f"{agent_id}_{model_type}_{datetime.now().timestamp()}"

        model = LearningModel(
            model_id=model_id,
            agent_id=agent_id,
            model_type=model_type,
            parameters=initial_params,
            version=1,
            accuracy=0.5,
            training_data_points=0,
            last_updated=datetime.now(),
            is_active=True
        )

        self.models[model_id] = model

        # Initialize Q-learning model based on type
        if model_type == 'pricing':
            self.q_models[model_id] = QLearningModel(
                state_space_size=100,  # Price states (0-999 in $10 increments)
                action_space_size=21,  # Price adjustments (-100 to +100 in $5 increments)
                **self.hyperparams
            )
        elif model_type == 'negotiation':
            self.q_models[model_id] = QLearningModel(
                state_space_size=50,   # Negotiation states
                action_space_size=11,  # Counter-offer percentages (0-100% in 10% increments)
                **self.hyperparams
            )
        elif model_type == 'resource-bidding':
            self.q_models[model_id] = QLearningModel(
                state_space_size=20,   # Competition levels
                action_space_size=11,  # Bid percentages (0-100% in 10% increments)
                **self.hyperparams
            )

        # Record on blockchain
        await self._record_model_creation_on_chain(model)

        logger.info(f"Created learning model {model_id} for agent {agent_id}")
        return model_id

    async def record_experience(self, model_id: str, experience: Experience) -> str:
        """Record an experience for model training"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        self.experiences[model_id].append(experience)
        self.models[model_id].training_data_points += 1

        # Train model if enough experiences collected
        if len(self.experiences[model_id]) >= 10:
            await self._train_model(model_id)

        # Record on blockchain
        experience_id = await self._record_experience_on_chain(model_id, experience)

        return experience_id

    async def optimize_pricing(self, agent_id: str, current_price: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pricing using reinforcement learning"""
        model_id = await self._get_or_create_pricing_model(agent_id)

        # Get current state
        state = {
            'price': current_price,
            'market_demand': market_data.get('demand', 0.5),
            'competition_level': market_data.get('competition', 5),
            'time_of_day': datetime.now().hour
        }

        # Get optimal action
        q_model = self.q_models[model_id]
        state_idx = q_model._state_to_index(state)
        action_idx = q_model.get_action(state_idx, explore=False)

        # Convert action back to price adjustment
        price_adjustment = (action_idx - 10) * 5  # -50 to +50 adjustment
        optimal_price = current_price + price_adjustment

        # Ensure price stays within reasonable bounds
        optimal_price = max(10, min(1000, optimal_price))

        result = {
            'optimal_price': optimal_price,
            'adjustment': price_adjustment,
            'confidence': self.models[model_id].accuracy,
            'model_version': self.models[model_id].version
        }

        return result

    async def optimize_negotiation_strategy(self, agent_id: str, negotiation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize negotiation strategy"""
        model_id = await self._get_or_create_negotiation_model(agent_id)

        # Analyze negotiation context
        target_price = negotiation_context.get('target_price', 100)
        current_offer = negotiation_context.get('current_offer', target_price * 1.2)
        rounds_remaining = negotiation_context.get('rounds_remaining', 5)

        state = {
            'price_ratio': current_offer / target_price,
            'rounds_remaining': rounds_remaining,
            'opponent_concessions': negotiation_context.get('opponent_concessions', 0)
        }

        # Get optimal action
        q_model = self.q_models[model_id]
        state_idx = q_model._state_to_index(state)
        action_idx = q_model.get_action(state_idx, explore=False)

        # Convert to negotiation action
        counter_offer_percentage = action_idx * 10  # 0-100% in 10% increments
        counter_offer = target_price * (1 + counter_offer_percentage / 100)

        result = {
            'counter_offer': counter_offer,
            'strategy': 'firm' if counter_offer_percentage < 30 else 'moderate' if counter_offer_percentage < 70 else 'concessive',
            'confidence': self.models[model_id].accuracy
        }

        return result

    async def optimize_resource_bidding(self, agent_id: str, bidding_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource bidding strategy"""
        model_id = await self._get_or_create_bidding_model(agent_id)

        max_budget = bidding_context.get('max_budget', 1000)
        competition_level = bidding_context.get('competition_level', 5)
        resource_value = bidding_context.get('resource_value', 800)

        state = {
            'competition_level': competition_level,
            'budget_ratio': max_budget / resource_value if resource_value > 0 else 1,
            'time_pressure': bidding_context.get('time_pressure', 0.5)
        }

        # Get optimal bid
        q_model = self.q_models[model_id]
        state_idx = q_model._state_to_index(state)
        action_idx = q_model.get_action(state_idx, explore=False)

        bid_percentage = action_idx * 10  # 0-100% in 10% increments
        optimal_bid = (max_budget * bid_percentage) / 100

        result = {
            'optimal_bid': optimal_bid,
            'bid_percentage': bid_percentage,
            'strategy': 'conservative' if bid_percentage < 50 else 'aggressive',
            'confidence': self.models[model_id].accuracy
        }

        return result

    async def create_optimization_task(self, agent_id: str, task_type: str, task_params: Dict[str, Any], duration_hours: int) -> str:
        """Create an optimization task"""
        task_id = f"task_{agent_id}_{task_type}_{datetime.now().timestamp()}"

        # Get relevant models for this task
        relevant_models = []
        for model_id, model in self.models.items():
            if model.agent_id == agent_id and model.model_type in self._get_relevant_model_types(task_type):
                relevant_models.append(model_id)

        # Create task data
        task_data = {
            'task_id': task_id,
            'agent_id': agent_id,
            'task_type': task_type,
            'task_params': task_params,
            'relevant_models': relevant_models,
            'deadline': datetime.now() + timedelta(hours=duration_hours),
            'created_at': datetime.now(),
            'is_completed': False
        }

        # Cache task data
        cache.set(f"optimization_task_{task_id}", task_data, timeout=duration_hours * 3600)

        # Record on blockchain
        await self._record_task_creation_on_chain(task_data)

        return task_id

    async def execute_optimization_task(self, task_id: str) -> Dict[str, Any]:
        """Execute an optimization task"""
        task_data = cache.get(f"optimization_task_{task_id}")
        if not task_data:
            raise ValueError(f"Task {task_id} not found")

        if task_data['is_completed']:
            raise ValueError(f"Task {task_id} already completed")

        if datetime.now() > task_data['deadline']:
            raise ValueError(f"Task {task_id} deadline passed")

        # Execute optimization based on task type
        if task_data['task_type'] == 'price-optimization':
            result = await self.optimize_pricing(
                task_data['agent_id'],
                task_data['task_params'].get('current_price', 100),
                task_data['task_params']
            )
        elif task_data['task_type'] == 'negotiation-strategy':
            result = await self.optimize_negotiation_strategy(
                task_data['agent_id'],
                task_data['task_params']
            )
        elif task_data['task_type'] == 'resource-bidding':
            result = await self.optimize_resource_bidding(
                task_data['agent_id'],
                task_data['task_params']
            )
        else:
            raise ValueError(f"Unknown task type: {task_data['task_type']}")

        # Mark task as completed
        task_data['is_completed'] = True
        task_data['result'] = result
        task_data['completed_at'] = datetime.now()

        cache.set(f"optimization_task_{task_id}", task_data, timeout=24 * 3600)  # Keep for 24 hours

        # Record completion on blockchain
        await self._record_task_completion_on_chain(task_id, result)

        return result

    async def update_hyperparameters(self, new_params: Dict[str, float]):
        """Update RL hyperparameters"""
        self.hyperparams.update(new_params)

        # Update all existing models
        for model_id, q_model in self.q_models.items():
            q_model.learning_rate = new_params.get('learning_rate', q_model.learning_rate)
            q_model.discount_factor = new_params.get('discount_factor', q_model.discount_factor)
            q_model.exploration_rate = new_params.get('exploration_rate', q_model.exploration_rate)

        logger.info(f"Updated RL hyperparameters: {new_params}")

    # Private helper methods

    async def _train_model(self, model_id: str):
        """Train a model using collected experiences"""
        if model_id not in self.q_models:
            return

        q_model = self.q_models[model_id]
        experiences = self.experiences[model_id]

        # Convert experiences to training data
        for exp in experiences[-50:]:  # Use last 50 experiences
            q_model.add_experience(exp)

        # Train model
        q_model.train_from_experiences()

        # Update model accuracy (simplified metric)
        positive_rewards = sum(1 for exp in experiences if exp.reward > 0)
        accuracy = positive_rewards / len(experiences) if experiences else 0.5

        # Update model metadata
        self.models[model_id].accuracy = accuracy
        self.models[model_id].version += 1
        self.models[model_id].last_updated = datetime.now()

        logger.info(f"Trained model {model_id}, new accuracy: {accuracy:.3f}")

    async def _get_or_create_pricing_model(self, agent_id: str) -> str:
        """Get existing pricing model or create new one"""
        for model_id, model in self.models.items():
            if model.agent_id == agent_id and model.model_type == 'pricing' and model.is_active:
                return model_id

        # Create new pricing model
        return await self.create_learning_model(agent_id, 'pricing', {})

    async def _get_or_create_negotiation_model(self, agent_id: str) -> str:
        """Get existing negotiation model or create new one"""
        for model_id, model in self.models.items():
            if model.agent_id == agent_id and model.model_type == 'negotiation' and model.is_active:
                return model_id

        # Create new negotiation model
        return await self.create_learning_model(agent_id, 'negotiation', {})

    async def _get_or_create_bidding_model(self, agent_id: str) -> str:
        """Get existing bidding model or create new one"""
        for model_id, model in self.models.items():
            if model.agent_id == agent_id and model.model_type == 'resource-bidding' and model.is_active:
                return model_id

        # Create new bidding model
        return await self.create_learning_model(agent_id, 'resource-bidding', {})

    def _get_relevant_model_types(self, task_type: str) -> List[str]:
        """Get relevant model types for a task"""
        if task_type == 'price-optimization':
            return ['pricing']
        elif task_type == 'negotiation-strategy':
            return ['negotiation']
        elif task_type == 'resource-bidding':
            return ['resource-bidding']
        return []

    # Blockchain interaction methods (simplified)

    async def _record_model_creation_on_chain(self, model: LearningModel):
        """Record model creation on Hedera"""
        # This would interact with the AIOptimization smart contract
        pass

    async def _record_experience_on_chain(self, model_id: str, experience: Experience) -> str:
        """Record experience on Hedera"""
        # This would interact with the AIOptimization smart contract
        return f"exp_{model_id}_{len(self.experiences[model_id])}"

    async def _record_task_creation_on_chain(self, task_data: Dict[str, Any]):
        """Record task creation on Hedera"""
        # This would interact with the AIOptimization smart contract
        pass

    async def _record_task_completion_on_chain(self, task_id: str, result: Dict[str, Any]):
        """Record task completion on Hedera"""
        # This would interact with the AIOptimization smart contract
        pass