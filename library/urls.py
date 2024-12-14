from django.urls import path
from .views import *

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('borrow-requests/', BorrowRequestsView.as_view(), name='borrow-requests'),
    path('update-request/<int:pk>/', UpdateBorrowRequestView.as_view(), name='update-request'),
    path('user-history/<int:user_id>/', UserBorrowHistoryView.as_view(), name='user-history'),
    path('books/', BookListView.as_view(), name='books'),
    path('borrow/', CreateBorrowRequestView.as_view(), name='borrow'),
    path('my-history/', PersonalBorrowHistoryView.as_view(), name='my-history'),
]
