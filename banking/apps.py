from django.apps import AppConfig
import sys
import os

class BankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banking'

    def ready(self):
        from .scheduler import scheduler  # Import scheduler to ensure it starts
        # Start the scheduler only if it is not already running
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN'):
                print('yooooo')
                # Start the scheduler
                scheduler.start()
