"""talentmap_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_expiring_authtoken import views as auth_views
from djangosaml2.views import echo_attributes
from talentmap_api.saml2.acs_patch import assertion_consumer_service

schema_view = get_schema_view(
    openapi.Info(
        title="TalentMAP API",
        default_version='v1',
    ),
    public=False,
)

urlpatterns = [
    # Administration related resources
    url(r'^api/v1/homepage/', include('talentmap_api.administration.urls.homepage')),
    url(r'^api/v1/aboutpage/', include('talentmap_api.administration.urls.aboutpage')),
    url(r'^api/v1/fsbid/admin/panel/', include('talentmap_api.fsbid.urls.admin_panel')),

    # Reference
    url(r'^api/v1/fsbid/bid_seasons/', include('talentmap_api.fsbid.urls.bid_seasons')),
    url(r'^api/v1/fsbid/reference/', include('talentmap_api.fsbid.urls.reference')),

    # Bureau
    url(r'^api/v1/fsbid/bureau/positions/', include('talentmap_api.fsbid.urls.bureau')),
    url(r'^api/v1/bureau/', include('talentmap_api.bureau.urls.bureau')),
    url(r'^api/v1/fsbid/bureau_exceptions/', include('talentmap_api.fsbid.urls.bureau_exceptions')),
    url(r'^api/v1/fsbid/assignment_cycles/', include('talentmap_api.fsbid.urls.assignment_cycles')),

    # Available Positions
    url(r'^api/v1/fsbid/available_positions/', include('talentmap_api.fsbid.urls.available_positions')),
    url(r'^api/v1/fsbid/positions/', include('talentmap_api.fsbid.urls.positions')),
    url(r'^api/v1/available_position/', include('talentmap_api.available_positions.urls.available_positions')),
    url(r'^api/v1/available_position/tandem/', include('talentmap_api.available_tandem.urls.available_tandem')),

    #Organization Stats
    url(r'^api/v1/fsbid/org_stats/', include('talentmap_api.fsbid.urls.org_stats')),

    # Projected Vacancies
    url(r'^api/v1/fsbid/projected_vacancies/', include('talentmap_api.fsbid.urls.projected_vacancies')),
    url(r'^api/v1/projected_vacancy/', include('talentmap_api.projected_vacancies.urls.projected_vacancies')),
    url(r'^api/v1/projected_vacancy/tandem/', include('talentmap_api.projected_tandem.urls.projected_tandem')),

    # Projected Vacancies Management
    url(r'^api/v1/fsbid/admin/projected_vacancies/', include('talentmap_api.fsbid.urls.admin_projected_vacancies')),
    
    # Cycle Job Categories
    url(r'^api/v1/fsbid/cycle_job_categories/', include('talentmap_api.fsbid.urls.cycle_job_categories')),

    # Job Categories
    url(r'^api/v1/fsbid/job_categories/', include('talentmap_api.fsbid.urls.job_categories')),

    # Position Management
    url(r'^api/v1/fsbid/post_access/', include('talentmap_api.fsbid.urls.post_access')),
    url(r'^api/v1/fsbid/manage_bid_seasons/', include('talentmap_api.fsbid.urls.manage_bid_seasons')),
    url(r'^api/v1/fsbid/capsule_descriptions/', include('talentmap_api.fsbid.urls.capsule_descriptions')),
    url(r'^api/v1/fsbid/publishable_positions/', include('talentmap_api.fsbid.urls.publishable_positions')),

    # Position Classifications
    url(r'^api/v1/fsbid/position_classifications/', include('talentmap_api.fsbid.urls.position_classifications')),

    # CDO
    url(r'^api/v1/fsbid/cdo/', include('talentmap_api.fsbid.urls.cdo')),
    url(r'^api/v1/fsbid/client/', include('talentmap_api.fsbid.urls.client')),
    url(r'^api/v1/cdo/', include('talentmap_api.cdo.urls.cdo')),

    # Employee Info
    url(r'^api/v1/fsbid/assignment_history/', include('talentmap_api.fsbid.urls.assignment_history')),
    url(r'^api/v1/fsbid/classifications/', include('talentmap_api.fsbid.urls.classifications')),
    url(r'^api/v1/fsbid/employee/', include('talentmap_api.fsbid.urls.employee')),
    url(r'^api/v1/fsbid/bidlist/', include('talentmap_api.fsbid.urls.bidlist')),
    url(r'^api/v1/fsbid/persons/', include('talentmap_api.fsbid.urls.persons')),

    # Agenda
    url(r'^api/v1/fsbid/agenda/', include('talentmap_api.fsbid.urls.agenda')),
    url(r'^api/v1/fsbid/agenda_employees/', include('talentmap_api.fsbid.urls.agenda_employees')),

    # Panel
    url(r'^api/v1/fsbid/panel/', include('talentmap_api.fsbid.urls.panel')),

    # Remark
    url(r'^api/v1/fsbid/remark/', include('talentmap_api.fsbid.urls.remark')),

    # TMOne Notification 
    url(r'^api/v1/fsbid/notification/', include('talentmap_api.fsbid.urls.notifications')),
 
    # Bidding
    url(r'^api/v1/bidding/', include('talentmap_api.bidding.urls.bidding')),
    url(r'^api/v1/bidhandshakecycle/', include('talentmap_api.bidding.urls.bidhandshakecycle')),
    url(r'^api/v1/fsbid/bid_audit/', include('talentmap_api.fsbid.urls.bid_audit')),

    # Bidding Tool
    url(r'^api/v1/fsbid/bidding_tool/', include('talentmap_api.fsbid.urls.bidding_tool')),

    # Permission resources
    url(r'^api/v1/permission/user/', include('talentmap_api.permission.urls.user')),
    url(r'^api/v1/permission/group/', include('talentmap_api.permission.urls.group')),

    # Profile and account related resources
    url(r'^api/v1/profile/', include('talentmap_api.user_profile.urls.profile')),
    url(r'^api/v1/searches/', include('talentmap_api.user_profile.urls.searches')),

    # Messaging related resources
    url(r'^api/v1/notification/', include('talentmap_api.messaging.urls.notification')),

    # Glossary
    url(r'^api/v1/glossary/', include('talentmap_api.glossary.urls.glossary')),

    # Feature Flags
    url(r'^api/v1/featureflags/', include('talentmap_api.feature_flags.urls.featureflags')),

    # Log viewing
    url(r'^api/v1/logs/', include('talentmap_api.log_viewer.urls.log_entry')),

    # Login statistics
    url(r'^api/v1/stats/', include('talentmap_api.stats.urls.logins')),

    # Redoc
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Swagger
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Health Check
    url(r'^ht/', include('health_check.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Auth patterns
urlpatterns += [
    url(r'^api/v1/accounts/token/$', auth_views.obtain_expiring_auth_token),
    url(r'^api/v1/accounts/', include('rest_framework.urls')),
    url(r'^api/v1/accounts/token/view/', include('talentmap_api.common.tokens.urls')),
]

if settings.ENABLE_SAML2:  # pragma: no cover
    urlpatterns += [
        url(r'^api/v1/saml2/acs/$', assertion_consumer_service, name='saml2_acs'),
        url(r'^api/v1/saml2/', include('djangosaml2.urls')),
    ]
    if settings.DEBUG:
        urlpatterns += [
            url(r'^saml2-test/', echo_attributes),
        ]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
