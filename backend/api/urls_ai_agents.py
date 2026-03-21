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
from ai_governance_views import AIOptimizationViewSet, GovernanceViewSet

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

    # AI Optimization
    path('optimization/models/', AIOptimizationViewSet.as_view({'post': 'create_model'}), name='ai_create_model'),
    path('optimization/experience/', AIOptimizationViewSet.as_view({'post': 'record_experience'}), name='ai_record_experience'),
    path('optimization/pricing/', AIOptimizationViewSet.as_view({'post': 'optimize_pricing'}), name='ai_optimize_pricing'),
    path('optimization/negotiation/', AIOptimizationViewSet.as_view({'post': 'optimize_negotiation'}), name='ai_optimize_negotiation'),
    path('optimization/bidding/', AIOptimizationViewSet.as_view({'post': 'optimize_bidding'}), name='ai_optimize_bidding'),
    path('optimization/tasks/', AIOptimizationViewSet.as_view({'post': 'create_task'}), name='ai_create_task'),
    path('optimization/tasks/execute/', AIOptimizationViewSet.as_view({'post': 'execute_task'}), name='ai_execute_task'),
    path('optimization/hyperparams/', AIOptimizationViewSet.as_view({'post': 'update_hyperparameters'}), name='ai_update_hyperparams'),

    # Governance
    path('governance/proposals/', GovernanceViewSet.as_view({'post': 'create_proposal'}), name='gov_create_proposal'),
    path('governance/vote/', GovernanceViewSet.as_view({'post': 'cast_vote'}), name='gov_cast_vote'),
    path('governance/execute/', GovernanceViewSet.as_view({'post': 'execute_proposal'}), name='gov_execute_proposal'),
    path('governance/execute-timelock/', GovernanceViewSet.as_view({'post': 'execute_timelocked_proposal'}), name='gov_execute_timelock'),
    path('governance/proposals/<str:pk>/', GovernanceViewSet.as_view({'get': 'get_proposal'}), name='gov_get_proposal'),
    path('governance/proposals/active/', GovernanceViewSet.as_view({'get': 'active_proposals'}), name='gov_active_proposals'),
    path('governance/proposals/<str:pk>/votes/', GovernanceViewSet.as_view({'get': 'proposal_votes'}), name='gov_proposal_votes'),
    path('governance/weight/', GovernanceViewSet.as_view({'get': 'voting_weight'}), name='gov_voting_weight'),
    path('governance/config/', GovernanceViewSet.as_view({'post': 'update_config'}), name='gov_update_config'),
]
