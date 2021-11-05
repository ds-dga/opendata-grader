import schedule
import time
from resource_api import process_invalid_api_resources, process_api_resources

schedule.every().day.at("10:35").do(process_api_resources)
schedule.every().wednesday.at("18:00").do(process_invalid_api_resources)


while True:
    schedule.run_pending()
    time.sleep(1)
