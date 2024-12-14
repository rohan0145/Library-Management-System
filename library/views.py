from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Book, BorrowRequest, BorrowHistory
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer, BorrowHistorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view!"})

class CreateUserView(APIView):
    """
    post:
    Create a new library user.

    This endpoint allows a librarian to create new users.
    Permissions: Only librarians can access this endpoint.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_librarian:
            return Response({'error': 'Only librarians can create users.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BorrowRequestsView(APIView):
    """View all borrow requests"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_librarian:
            return Response({'error': 'Only librarians can view borrow requests.'}, status=status.HTTP_403_FORBIDDEN)

        requests = BorrowRequest.objects.all()
        serializer = BorrowRequestSerializer(requests, many=True)
        return Response(serializer.data)

class UpdateBorrowRequestView(APIView):
    """Approve or deny a borrow request"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_librarian:
            return Response({'error': 'Only librarians can update borrow requests.'}, status=status.HTTP_403_FORBIDDEN)

        borrow_request = get_object_or_404(BorrowRequest, pk=pk)
        status_update = request.data.get('status')
        if status_update not in ['Approved', 'Denied']:
            return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

        borrow_request.status = status_update
        borrow_request.save()

        if status_update == 'Approved':
            BorrowHistory.objects.create(
                user=borrow_request.user,
                book=borrow_request.book,
                borrow_date=borrow_request.start_date,
                return_date=borrow_request.end_date
            )

        return Response({'message': 'Borrow request updated successfully.'})

class UserBorrowHistoryView(APIView):
    """View a user's borrow history"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if not request.user.is_librarian:
            return Response({'error': 'Only librarians can view user borrow history.'}, status=status.HTTP_403_FORBIDDEN)

        history = BorrowHistory.objects.filter(user_id=user_id)
        serializer = BorrowHistorySerializer(history, many=True)
        return Response(serializer.data)

class BookListView(APIView):
    """Get a list of books"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class CreateBorrowRequestView(APIView):
    """Submit a borrow request"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BorrowRequestSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.validated_data['book']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            overlapping_request = BorrowRequest.objects.filter(
                book=book,
                status='Approved',
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exists()
            if overlapping_request:
                return Response({'error': 'Book is already borrowed for these dates.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PersonalBorrowHistoryView(APIView):
    """View personal borrow history"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = BorrowHistory.objects.filter(user=request.user)
        serializer = BorrowHistorySerializer(history, many=True)
        return Response(serializer.data)