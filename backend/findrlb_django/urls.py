"""
URL configuration for findrlb_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import health_check, api_status, system_info
from api.analytics import (
    dashboard_analytics, user_metrics, property_metrics, 
    blockchain_metrics, recent_activities, system_status
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health & Status endpoints
    path('api/health/', health_check, name='health_check'),
    path('api/status/', api_status, name='api_status'),
    path('api/system/', system_info, name='system_info'),
    
    # Analytics endpoints
    path('api/admin/analytics/', dashboard_analytics, name='dashboard_analytics'),
    path('api/admin/users/', user_metrics, name='user_metrics'),
    path('api/admin/properties/', property_metrics, name='property_metrics'),
    path('api/admin/blockchain/', blockchain_metrics, name='blockchain_metrics'),
    path('api/admin/activities/', recent_activities, name='recent_activities'),
    path('api/admin/system-status/', system_status, name='system_status'),
    
    # App URLs
    path('api/auth/', include('accounts.urls')),
    path('api/properties/', include('property.urls')),
    path('api/search/', include('api.urls_search')),
    # path('api/recommendations/', include('api.urls_recommendations')),  # Temporarily disabled due to import issues

    # Commented out for now - can be enabled as modules are completed
    path('api/tenant/', include('tenant.urls')),
    # path('api/landlord/', include('landlord.urls')),
    # path('api/service/', include('service.urls')),
    # path('api/contracts/', include('api.urls_contracts')),
    # path('api/token/', include('api.urls_token')),
    path('api/ai-agents/', include('api.urls_ai_agents')),
    # path('api/wallet/', include('api.urls_wallet')),
]

