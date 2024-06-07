from django.urls import path
from .views import OpenAIView, CustomerDataView, ContactViewSet

urlpatterns = [
    path('ask/', OpenAIView.as_view(), name='ask'),
    path('add-context-data/', CustomerDataView.as_view(), name='add_data'),
    path('delete-context-data/', CustomerDataView.as_view(), name='delete-data'),
    path('update-contacts/', ContactViewSet.as_view(), name='contact-list-create'),
]
