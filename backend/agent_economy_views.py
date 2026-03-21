"""
API Views for Agent Economy and Coordination
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from backend.agent_economy_service import AgentEconomyService
from backend.agent_coordinator import AgentCoordinator


class AgentRegistrationView(APIView):
    """
    Register a new AI agent in the economy
    """

    def post(self, request):
        agent_type = request.data.get('agent_type')
        capabilities = request.data.get('capabilities', [])
        wallet_address = request.data.get('wallet_address')

        if not agent_type or not capabilities:
            return Response(
                {'error': 'agent_type and capabilities are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        economy_service = AgentEconomyService()
        result = economy_service.register_agent(
            agent_type=agent_type,
            capabilities=capabilities,
            wallet_address=wallet_address
        )

        if result.get('status') == 'SUCCESS':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class AgentBalanceView(APIView):
    """
    Get agent balance and information
    """

    def get(self, request, agent_id):
        economy_service = AgentEconomyService()
        balance = economy_service.get_agent_balance(int(agent_id))
        agent_info = economy_service.get_agent_info(int(agent_id))

        if agent_info:
            return Response({
                'agent_id': agent_id,
                'balance': balance,
                'agent_info': agent_info
            })
        else:
            return Response(
                {'error': 'Agent not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, agent_id):
        """Deposit or withdraw from agent balance"""
        action = request.data.get('action')  # 'deposit' or 'withdraw'
        amount = request.data.get('amount', 0)

        if action not in ['deposit', 'withdraw'] or amount <= 0:
            return Response(
                {'error': 'Invalid action or amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

        economy_service = AgentEconomyService()

        if action == 'deposit':
            result = economy_service.deposit_to_agent(int(agent_id), amount)
        else:
            result = economy_service.withdraw_from_agent(int(agent_id), amount)

        return Response(result)


class ServiceOfferView(APIView):
    """
    Create and manage service offers
    """

    def post(self, request):
        """Create a new service offer"""
        agent_id = request.data.get('agent_id')
        service_type = request.data.get('service_type')
        description = request.data.get('description', '')
        base_price = request.data.get('base_price', 0)
        variable_fee = request.data.get('variable_fee', 0)
        min_order_value = request.data.get('min_order_value', 0)

        if not all([agent_id, service_type, base_price >= 0]):
            return Response(
                {'error': 'agent_id, service_type, and base_price are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        economy_service = AgentEconomyService()
        result = economy_service.create_service_offer(
            agent_id=int(agent_id),
            service_type=service_type,
            description=description,
            base_price=float(base_price),
            variable_fee=int(variable_fee),
            min_order_value=float(min_order_value)
        )

        if result.get('status') == 'SUCCESS':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Get service offers, optionally filtered by type"""
        service_type = request.query_params.get('service_type')
        economy_service = AgentEconomyService()
        offers = economy_service.get_service_offers(service_type)

        return Response({'offers': offers})


class ServiceExecutionView(APIView):
    """
    Execute service purchases
    """

    def post(self, request):
        offer_id = request.data.get('offer_id')
        requestor_agent_id = request.data.get('requestor_agent_id')
        order_value = request.data.get('order_value', 0)

        if not all([offer_id, requestor_agent_id]):
            return Response(
                {'error': 'offer_id and requestor_agent_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        economy_service = AgentEconomyService()
        result = economy_service.execute_service(
            offer_id=int(offer_id),
            requestor_agent_id=int(requestor_agent_id),
            order_value=float(order_value)
        )

        return Response(result)


class AgentTransferView(APIView):
    """
    Transfer HBAR between agents
    """

    def post(self, request):
        from_agent_id = request.data.get('from_agent_id')
        to_agent_id = request.data.get('to_agent_id')
        amount = request.data.get('amount')
        service_type = request.data.get('service_type', 'direct_transfer')

        if not all([from_agent_id, to_agent_id, amount and amount > 0]):
            return Response(
                {'error': 'from_agent_id, to_agent_id, and amount > 0 are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        economy_service = AgentEconomyService()
        result = economy_service.transfer_between_agents(
            from_agent_id=int(from_agent_id),
            to_agent_id=int(to_agent_id),
            amount=float(amount),
            service_type=service_type
        )

        return Response(result)


class IntentBroadcastView(APIView):
    """
    Broadcast service intents for coordination
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def post(self, request):
        agent_id = request.data.get('agent_id')
        intent_type = request.data.get('intent_type')
        parameters = request.data.get('parameters', {})
        deadline_hours = request.data.get('deadline_hours', 24)

        if not all([agent_id, intent_type]):
            return Response(
                {'error': 'agent_id and intent_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        coordinator = AgentCoordinator()
        result = await coordinator.broadcast_intent(
            agent_id=int(agent_id),
            intent_type=intent_type,
            parameters=parameters,
            deadline_hours=int(deadline_hours)
        )

        if result.get('status') == 'SUCCESS':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class BidSubmissionView(APIView):
    """
    Submit bids for service intents
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def post(self, request):
        intent_id = request.data.get('intent_id')
        bidding_agent_id = request.data.get('bidding_agent_id')
        bid_parameters = request.data.get('bid_parameters', {})

        if not all([intent_id, bidding_agent_id, bid_parameters]):
            return Response(
                {'error': 'intent_id, bidding_agent_id, and bid_parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        coordinator = AgentCoordinator()
        result = await coordinator.submit_bid(
            intent_id=intent_id,
            bidding_agent_id=int(bidding_agent_id),
            bid_parameters=bid_parameters
        )

        if result.get('status') == 'SUCCESS':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class IntentQueryView(APIView):
    """
    Query pending service intents
    """

    async def get(self, request):
        agent_type = request.query_params.get('agent_type')
        service_type = request.query_params.get('service_type')

        coordinator = AgentCoordinator()
        intents = await coordinator.get_pending_intents(
            agent_type_filter=agent_type,
            service_type_filter=service_type
        )

        return Response({'intents': intents})


class BidAcceptanceView(APIView):
    """
    Accept bids and execute transactions
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def post(self, request):
        intent_id = request.data.get('intent_id')
        bid_id = request.data.get('bid_id')
        accepting_agent_id = request.data.get('accepting_agent_id')

        if not all([intent_id, bid_id, accepting_agent_id]):
            return Response(
                {'error': 'intent_id, bid_id, and accepting_agent_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        coordinator = AgentCoordinator()
        result = await coordinator.accept_bid(
            intent_id=intent_id,
            bid_id=bid_id,
            accepting_agent_id=int(accepting_agent_id)
        )

        return Response(result)


class AgentDiscoveryView(APIView):
    """
    Discover agents and their capabilities
    """

    def get(self, request):
        agent_type = request.query_params.get('agent_type')
        economy_service = AgentEconomyService()

        if agent_type:
            agents = economy_service.get_agents_by_type(agent_type)
        else:
            # Get all agents (simplified - in production would paginate)
            agents = []
            for i in range(1, economy_service.next_agent_id):
                agent_info = economy_service.get_agent_info(i)
                if agent_info:
                    agents.append(agent_info)

        return Response({'agents': agents})


class NegotiationView(APIView):
    """
    Full negotiation workflow
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def post(self, request):
        """Start a negotiation"""
        action = request.data.get('action', 'negotiate')
        agent_id = request.data.get('agent_id')

        if action == 'negotiate':
            service_type = request.data.get('service_type')
            requirements = request.data.get('requirements', {})
            max_budget = request.data.get('max_budget', 1000)

            if not all([agent_id, service_type]):
                return Response(
                    {'error': 'agent_id and service_type are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # This would need to be implemented in the autonomous agent
            # For now, return a placeholder
            return Response({
                'status': 'SUCCESS',
                'message': f'Negotiation initiated for {service_type}',
                'agent_id': agent_id
            })

        elif action == 'evaluate_bids':
            intent_id = request.data.get('intent_id')

            if not intent_id:
                return Response(
                    {'error': 'intent_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            coordinator = AgentCoordinator()
            bids = await coordinator.get_negotiation_status(intent_id)
            return Response({'bids': bids.get('bids', [])})

        else:
            return Response(
                {'error': 'Unknown action'},
                status=status.HTTP_400_BAD_REQUEST
            )