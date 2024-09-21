import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from banking.tasks import update_sentiment_data

# Configure logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# Create the scheduler
scheduler = BackgroundScheduler(
    executors={
        'default': ThreadPoolExecutor(10)
    },
    job_defaults={
        'coalesce': False,
        'max_instances': 1
    },
    timezone='UTC'
)

# Define the job function
def update_sentiment():
    start_time = time.time()
    logging.info("Starting sentiment update job")
    update_sentiment_data()  # Call the function directly from tasks.py
    elapsed_time = time.time() - start_time
    logging.info(f"Sentiment update job completed in {elapsed_time} seconds")

# Schedule the job
scheduler.add_job(update_sentiment, 'interval', minutes=1, id='update_sentiment')
