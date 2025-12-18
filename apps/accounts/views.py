from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, WaitlistEntry, DemoRequest
from apps.accounts.serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    LoginSerializer, ChangePasswordSerializer,
    WaitlistEntrySerializer, WaitlistSignupSerializer,
    DemoRequestSerializer, DemoBookingSerializer
)
from apps.core.permissions import IsTenantMember


class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        """Filter users by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.filter(tenant=self.request.user.tenant)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user
        """
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set tenant from request or create default
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            from apps.tenants.models import Tenant
            tenant = Tenant.objects.filter(is_active=True).first()
            if not tenant:
                return Response(
                    {'error': 'No active tenant found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        user = serializer.save(tenant=tenant)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        Login user
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password changed successfully'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user details
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class WaitlistViewSet(viewsets.ModelViewSet):
    """
    Waitlist management viewset
    """
    serializer_class = WaitlistEntrySerializer
    queryset = WaitlistEntry.objects.all()
    permission_classes = [IsAuthenticated]  # Only authenticated users can manage waitlist

    def get_queryset(self):
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return WaitlistEntry.objects.none()
        # Only superusers can see all entries, others see their own
        if self.request.user.is_superuser:
            return WaitlistEntry.objects.all()
        return WaitlistEntry.objects.filter(email=self.request.user.email)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def join(self, request):
        """
        Join the waitlist - public endpoint
        """
        serializer = WaitlistSignupSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Check if email already exists
        email = serializer.validated_data['email']
        if WaitlistEntry.objects.filter(email=email).exists():
            return Response(
                {'message': 'You are already on the waitlist!'},
                status=status.HTTP_200_OK
            )

        entry = serializer.save()
        return Response({
            'message': 'Successfully joined the waitlist!',
            'position': WaitlistEntry.objects.filter(created_at__lte=entry.created_at).count(),
            'entry': WaitlistEntrySerializer(entry).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def count(self, request):
        """
        Get waitlist count - public endpoint
        """
        total_count = WaitlistEntry.objects.count()
        return Response({
            'total_count': total_count,
            'message': f'Join {total_count} others on the waitlist!'
        })


class DemoViewSet(viewsets.ModelViewSet):
    """
    Demo booking management viewset
    """
    serializer_class = DemoRequestSerializer
    queryset = DemoRequest.objects.all()
    permission_classes = [IsAuthenticated]  # Only authenticated users can manage demos

    def get_queryset(self):
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return DemoRequest.objects.none()
        # Only superusers can see all requests, others see their own
        if self.request.user.is_superuser:
            return DemoRequest.objects.all()
        return DemoRequest.objects.filter(email=self.request.user.email)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def book(self, request):
        """
        Book a demo - public endpoint
        """
        serializer = DemoBookingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        demo_request = serializer.save()
        return Response({
            'message': 'Demo request submitted successfully!',
            'request_id': demo_request.id,
            'status': 'pending',
            'estimated_response': 'We will contact you within 24 hours to schedule your demo.',
            'request': DemoRequestSerializer(demo_request).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def availability(self, request):
        """
        Get demo availability - public endpoint
        """
        from datetime import datetime, timedelta
        import pytz

        # Generate next 7 days of availability (9 AM - 5 PM business hours)
        availability = []
        utc = pytz.UTC

        for i in range(7):
            date = datetime.now(utc).date() + timedelta(days=i)
            if date.weekday() < 5:  # Monday-Friday
                availability.append({
                    'date': date.isoformat(),
                    'slots': [
                        {'time': '09:00', 'available': True},
                        {'time': '10:00', 'available': True},
                        {'time': '11:00', 'available': True},
                        {'time': '14:00', 'available': True},
                        {'time': '15:00', 'available': True},
                        {'time': '16:00', 'available': True},
                    ]
                })

        return Response({
            'timezone': 'UTC',
            'availability': availability,
            'note': 'All times are in UTC. We will confirm your preferred time slot.'
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def schedule(self, request, pk=None):
        """
        Schedule a demo (admin only)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can schedule demos'},
                status=status.HTTP_403_FORBIDDEN
            )

        demo_request = self.get_object()
        scheduled_date = request.data.get('scheduled_date')
        meeting_link = request.data.get('meeting_link')

        if scheduled_date:
            demo_request.scheduled_date = scheduled_date
        if meeting_link:
            demo_request.meeting_link = meeting_link

        demo_request.status = 'scheduled'
        demo_request.save()

        return Response({
            'message': 'Demo scheduled successfully',
            'demo_request': DemoRequestSerializer(demo_request).data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """
        Mark demo as completed (admin only)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can complete demos'},
                status=status.HTTP_403_FORBIDDEN
            )

        demo_request = self.get_object()
        demo_request.status = 'completed'
        demo_request.notes = request.data.get('notes', '')
        demo_request.save()

        return Response({
            'message': 'Demo marked as completed',
            'demo_request': DemoRequestSerializer(demo_request).data
        })