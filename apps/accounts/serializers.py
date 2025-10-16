from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.accounts.models import User, WaitlistEntry, DemoRequest


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone', 'role', 'is_active', 'is_verified', 'mfa_enabled',
            'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user creation"""
    password = serializers.CharField(write_only=True, min_length=12)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'phone',
            'role', 'password', 'password_confirm'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user updates"""

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'phone', 'role'
        ]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=12)
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class WaitlistEntrySerializer(serializers.ModelSerializer):
    """Serializer for waitlist entries"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = WaitlistEntry
        fields = [
            'id', 'email', 'first_name', 'last_name', 'company_name',
            'job_title', 'phone', 'interest_level', 'referral_source',
            'signup_source', 'status', 'email_opt_in', 'sms_opt_in',
            'full_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WaitlistSignupSerializer(serializers.ModelSerializer):
    """Serializer for waitlist signup"""

    class Meta:
        model = WaitlistEntry
        fields = [
            'email', 'first_name', 'last_name', 'company_name',
            'job_title', 'phone', 'interest_level', 'referral_source'
        ]

    def create(self, validated_data):
        # Get client IP and user agent for tracking
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        return super().create(validated_data)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DemoRequestSerializer(serializers.ModelSerializer):
    """Serializer for demo requests"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = DemoRequest
        fields = [
            'id', 'email', 'first_name', 'last_name', 'company_name',
            'job_title', 'phone', 'preferred_date', 'preferred_time',
            'timezone', 'company_size', 'industry', 'current_solution',
            'interests', 'special_requirements', 'attendees',
            'status', 'scheduled_date', 'meeting_link', 'notes',
            'follow_up_required', 'follow_up_date', 'email_opt_in',
            'full_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'scheduled_date', 'meeting_link',
            'notes', 'follow_up_required', 'follow_up_date', 'created_at'
        ]


class DemoBookingSerializer(serializers.ModelSerializer):
    """Serializer for demo booking"""

    class Meta:
        model = DemoRequest
        fields = [
            'email', 'first_name', 'last_name', 'company_name',
            'job_title', 'phone', 'preferred_date', 'preferred_time',
            'timezone', 'company_size', 'industry', 'current_solution',
            'interests', 'special_requirements', 'attendees'
        ]

    def validate_preferred_date(self, value):
        """Validate preferred date is not in the past"""
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Preferred date cannot be in the past")
        return value

    def create(self, validated_data):
        # Get client IP and user agent for tracking
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        return super().create(validated_data)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip