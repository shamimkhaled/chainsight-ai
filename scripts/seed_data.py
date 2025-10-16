#!/usr/bin/env python
"""
Script to seed initial data for development
"""
import os
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tenants.models import Tenant
from apps.accounts.models import User


def create_default_tenant():
    """Create default tenant for development"""
    tenant, created = Tenant.objects.get_or_create(
        subdomain='default',
        defaults={
            'name': 'Default Organization',
            'plan_type': 'professional',
            'max_users': 50,
            'max_contracts': 1000,
            'max_storage_gb': 100,
        }
    )

    if created:
        print(f"Created default tenant: {tenant.name}")
    else:
        print(f"Default tenant already exists: {tenant.name}")

    return tenant


def create_admin_user(tenant):
    """Create admin user for development"""
    admin_user, created = User.objects.get_or_create(
        email='admin@chainsight.ai',
        defaults={
            'tenant': tenant,
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )

    if created:
        admin_user.set_password('admin123!')
        admin_user.save()
        print(f"Created admin user: {admin_user.email}")
    else:
        print(f"Admin user already exists: {admin_user.email}")

    return admin_user


def create_sample_users(tenant):
    """Create sample users for development"""
    sample_users = [
        {
            'email': 'manager@chainsight.ai',
            'first_name': 'John',
            'last_name': 'Manager',
            'role': 'manager',
        },
        {
            'email': 'user@chainsight.ai',
            'first_name': 'Jane',
            'last_name': 'User',
            'role': 'user',
        },
        {
            'email': 'viewer@chainsight.ai',
            'first_name': 'Bob',
            'last_name': 'Viewer',
            'role': 'viewer',
        },
    ]

    for user_data in sample_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'tenant': tenant,
                'username': user_data['email'].split('@')[0],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_active': True,
            }
        )

        if created:
            user.set_password('password123!')
            user.save()
            print(f"Created sample user: {user.email}")
        else:
            print(f"Sample user already exists: {user.email}")


def main():
    """Main seeding function"""
    print("Starting data seeding...")

    # Create default tenant
    tenant = create_default_tenant()

    # Create admin user
    create_admin_user(tenant)

    # Create sample users
    create_sample_users(tenant)

    print("Data seeding completed!")


if __name__ == '__main__':
    main()