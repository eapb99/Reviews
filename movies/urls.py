from django.urls import path

from movies.views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/registros/', consultar_registros, name='registros'),
    path('autocomplete/<str:model>/', autocomplete, name='autocomplete'),

]
