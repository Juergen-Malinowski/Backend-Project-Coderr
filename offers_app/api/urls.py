from django.urls import path

from .views import (
    OfferDetailRetrieveView,
    OfferDetailView,
    OfferListCreateView,
)

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offer-detail-retrieve'),
]