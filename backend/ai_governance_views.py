"""
API Views for AI Optimization and Governance Services
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from typing import Dict, Any
import json
import asyncio
from asgiref.sync import async_to_sync

from .ai_optimization_service import AIOptimizationService
from .governance_service import GovernanceService, ProposalType, ProposalStatus

class AIOptimizationViewSet(viewsets.ViewSet):
    """ViewSet for AI optimization operations"""

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_service = AIOptimizationService()

    @action(detail=False, methods=['post'])
    def create_model(self, request):
        """Create a new learning model"""
        agent_id = request.data.get('agent_id')
        model_type = request.data.get('model_type')
        initial_params = request.data.get('initial_params', {})

        if not agent_id or not model_type:
            return Response(
                {'error': 'agent_id and model_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            model_id = async_to_sync(self.ai_service.create_learning_model)(
                agent_id, model_type, initial_params
            )

            return Response({
                'model_id': model_id,
                'message': 'Learning model created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def record_experience(self, request):
        """Record an experience for model training"""
        model_id = request.data.get('model_id')
        state = request.data.get('state', {})
        action = request.data.get('action', {})
        reward = request.data.get('reward', 0.0)
        next_state = request.data.get('next_state', {})

        if not model_id:
            return Response(
                {'error': 'model_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .ai_optimization_service import Experience
            from datetime import datetime

            experience = Experience(
                state=state,
                action=action,
                reward=float(reward),
                next_state=next_state,
                timestamp=datetime.now()
            )

            experience_id = async_to_sync(self.ai_service.record_experience)(
                model_id, experience
            )

            return Response({
                'experience_id': experience_id,
                'message': 'Experience recorded successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def optimize_pricing(self, request):
        """Optimize pricing using AI"""
        agent_id = request.data.get('agent_id')
        current_price = request.data.get('current_price', 100.0)
        market_data = request.data.get('market_data', {})

        if not agent_id:
            return Response(
                {'error': 'agent_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = async_to_sync(self.ai_service.optimize_pricing)(
                agent_id, float(current_price), market_data
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def optimize_negotiation(self, request):
        """Optimize negotiation strategy"""
        agent_id = request.data.get('agent_id')
        negotiation_context = request.data.get('negotiation_context', {})

        if not agent_id:
            return Response(
                {'error': 'agent_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = async_to_sync(self.ai_service.optimize_negotiation_strategy)(
                agent_id, negotiation_context
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def optimize_bidding(self, request):
        """Optimize resource bidding"""
        agent_id = request.data.get('agent_id')
        bidding_context = request.data.get('bidding_context', {})

        if not agent_id:
            return Response(
                {'error': 'agent_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = async_to_sync(self.ai_service.optimize_resource_bidding)(
                agent_id, bidding_context
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def create_task(self, request):
        """Create an optimization task"""
        agent_id = request.data.get('agent_id')
        task_type = request.data.get('task_type')
        task_params = request.data.get('task_params', {})
        duration_hours = request.data.get('duration_hours', 24)

        if not agent_id or not task_type:
            return Response(
                {'error': 'agent_id and task_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task_id = async_to_sync(self.ai_service.create_optimization_task)(
                agent_id, task_type, task_params, int(duration_hours)
            )

            return Response({
                'task_id': task_id,
                'message': 'Optimization task created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def execute_task(self, request):
        """Execute an optimization task"""
        task_id = request.data.get('task_id')

        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = async_to_sync(self.ai_service.execute_optimization_task)(task_id)

            return Response({
                'task_id': task_id,
                'result': result,
                'message': 'Task executed successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_hyperparameters(self, request):
        """Update RL hyperparameters"""
        new_params = request.data.get('hyperparameters', {})

        try:
            async_to_sync(self.ai_service.update_hyperparameters)(new_params)

            return Response({
                'message': 'Hyperparameters updated successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GovernanceViewSet(viewsets.ViewSet):
    """ViewSet for governance operations"""

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.governance_service = GovernanceService()

    @action(detail=False, methods=['post'])
    def create_proposal(self, request):
        """Create a new governance proposal"""
        proposal_type_str = request.data.get('proposal_type')
        title = request.data.get('title')
        description = request.data.get('description')
        parameters = request.data.get('parameters', {})

        if not proposal_type_str or not title or not description:
            return Response(
                {'error': 'proposal_type, title, and description are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            proposal_type = ProposalType(proposal_type_str)
        except ValueError:
            return Response(
                {'error': f'Invalid proposal type: {proposal_type_str}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            proposal_id = async_to_sync(self.governance_service.create_proposal)(
                request.user.username, proposal_type, title, description, parameters
            )

            return Response({
                'proposal_id': proposal_id,
                'message': 'Proposal created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def cast_vote(self, request):
        """Cast a vote on a proposal"""
        proposal_id = request.data.get('proposal_id')
        support = request.data.get('support')

        if proposal_id is None or support is None:
            return Response(
                {'error': 'proposal_id and support are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            success = async_to_sync(self.governance_service.cast_vote)(
                proposal_id, request.user.username, bool(support)
            )

            return Response({
                'message': 'Vote cast successfully',
                'support': support
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def execute_proposal(self, request):
        """Execute a successful proposal"""
        proposal_id = request.data.get('proposal_id')

        if not proposal_id:
            return Response(
                {'error': 'proposal_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            success = async_to_sync(self.governance_service.execute_proposal)(proposal_id)

            return Response({
                'proposal_id': proposal_id,
                'executed': success,
                'message': 'Proposal execution attempted'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def execute_timelocked_proposal(self, request):
        """Execute a timelocked proposal"""
        proposal_id = request.data.get('proposal_id')

        if not proposal_id:
            return Response(
                {'error': 'proposal_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            success = async_to_sync(self.governance_service.execute_timelocked_proposal)(proposal_id)

            return Response({
                'proposal_id': proposal_id,
                'executed': success,
                'message': 'Timelocked proposal executed successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def get_proposal(self, request, pk=None):
        """Get proposal details"""
        try:
            proposal = async_to_sync(self.governance_service.get_proposal)(pk)

            if proposal is None:
                return Response(
                    {'error': 'Proposal not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(proposal, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def active_proposals(self, request):
        """Get all active proposals"""
        try:
            proposals = async_to_sync(self.governance_service.get_active_proposals)()

            return Response({
                'proposals': proposals,
                'count': len(proposals)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def proposal_votes(self, request, pk=None):
        """Get voting results for a proposal"""
        try:
            votes = async_to_sync(self.governance_service.get_proposal_votes)(pk)

            return Response(votes, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def voting_weight(self, request):
        """Get voting weight for current user"""
        try:
            weight = async_to_sync(self.governance_service.get_voting_weight)(request.user.username)

            return Response({
                'voting_weight': weight
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_config(self, request):
        """Update governance configuration (admin only)"""
        # This would require admin permissions
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin privileges required'},
                status=status.HTTP_403_FORBIDDEN
            )

        config_data = request.data.get('config', {})

        try:
            from .governance_service import GovernanceConfig

            config = GovernanceConfig(
                voting_period=config_data.get('voting_period', 7 * 24 * 3600),
                proposal_threshold=config_data.get('proposal_threshold', 1000),
                quorum_threshold=config_data.get('quorum_threshold', 1000),
                timelock_delay=config_data.get('timelock_delay', 2 * 24 * 3600),
                execution_grace_period=config_data.get('execution_grace_period', 7 * 24 * 3600)
            )

            async_to_sync(self.governance_service.update_governance_config)(config)

            return Response({
                'message': 'Governance configuration updated successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )