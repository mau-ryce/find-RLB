from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Temporarily disabled to allow migrations to run
        # ensure demo credentials exist for quick testing
        pass
        # try:
        #     from django.contrib.auth import get_user_model
        #     User = get_user_model()
        #     demo_users = [
        #         {'username': 'tenant1', 'password': 'password123', 'role': 'tenant'},
        #         {'username': 'landlord1', 'password': 'password123', 'role': 'landlord'},
        #         {'username': 'service1', 'password': 'password123', 'role': 'service_provider'},
        #     ]
        #     for info in demo_users:
        #         if not User.objects.filter(username=info['username']).exists():
        #             user = User.objects.create_user(
        #                 username=info['username'],
        #                 password=info['password'],
        #             )
        #             user.role = info['role']
        #             user.save()
        # except Exception:
        #     pass  # Ignore errors during app initialization
