from django.urls import path

from .views import ContactViewSet, CustomerDataView, OtwChatbotView, LeadCreateView

urlpatterns = [
    path('ask/', OtwChatbotView.as_view(), name='ask'),
    path('add-context-data/', CustomerDataView.as_view(), name='add_data'),
    path('delete-context-data/', CustomerDataView.as_view(), name='delete-data'),
    path('update-contacts/', ContactViewSet.as_view(), name='contact-list-create'),
    path('delete-contact/', ContactViewSet.as_view(), name='contact-list-delete'),
    path('add-lead/', LeadCreateView.as_view(), name='add-lead'),
]
