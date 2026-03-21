from django.urls import path
from ai_agent_api import (
    TenantAgentView, LandlordAgentView, MatchingEngineView, TopMatchesView,
    AdvancedTenantRecommendationView, GuardianAgentView, MovingServiceAgentView,
    SavingsToOwnAgentView, P2PCommunityAgentView, CustomerCareAgentView, HederaAuthView
)
from agent_economy_views import (
    AgentRegistrationView, AgentBalanceView, ServiceOfferView, ServiceExecutionView,
    AgentTransferView, IntentBroadcastView, BidSubmissionView, IntentQueryView,
    BidAcceptanceView, AgentDiscoveryView, NegotiationView
)

urlpatterns = [
    # Legacy AI Agents
    path('ai/tenant', TenantAgentView.as_view()),
    path('ai/landlord', LandlordAgentView.as_view()),
    path('ai/match', MatchingEngineView.as_view()),
    path('ai/top-matches', TopMatchesView.as_view()),
    path('ai/tenant/advanced', AdvancedTenantRecommendationView.as_view()),
    path('ai/guardian', GuardianAgentView.as_view()),
    path('ai/moving-service', MovingServiceAgentView.as_view()),
    path('ai/savings-to-own', SavingsToOwnAgentView.as_view()),
    path('auth/hedera', HederaAuthView.as_view()),
    path('ai/p2p-community', P2PCommunityAgentView.as_view()),
    path('ai/customer-care', CustomerCareAgentView.as_view()),

    # Agent Economy & Coordination
    path('economy/register/', AgentRegistrationView.as_view(), name='agent_register'),
    path('economy/balance/<int:agent_id>/', AgentBalanceView.as_view(), name='agent_balance'),
    path('economy/transfer/', AgentTransferView.as_view(), name='agent_transfer'),
    path('economy/services/', ServiceOfferView.as_view(), name='service_offers'),
    path('economy/services/execute/', ServiceExecutionView.as_view(), name='service_execute'),
    path('economy/discovery/', AgentDiscoveryView.as_view(), name='agent_discovery'),

    # Agent Coordination
    path('coord/intents/', IntentBroadcastView.as_view(), name='intent_broadcast'),
    path('coord/bids/', BidSubmissionView.as_view(), name='bid_submit'),
    path('coord/intents/query/', IntentQueryView.as_view(), name='intent_query'),
    path('coord/bids/accept/', BidAcceptanceView.as_view(), name='bid_accept'),
    path('coord/negotiate/', NegotiationView.as_view(), name='negotiation'),
]
