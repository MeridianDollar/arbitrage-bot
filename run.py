import time
import logging
from main import check_for_arbitrage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

amount_in = int(10e18)  # Example value, ensure this is defined or passed as a parameter
use_stables = False  # Set to False if denominating in TARA


def main_loop(sleep_time=30):
    while True:
        try:
            check_for_arbitrage(amount_in, use_stables)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")

    