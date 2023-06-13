import logging
import threading
from datetime import date
import time
from betconnect import resources
from betconnect.resources import filters
import betconnect

logger = logging.getLogger(__name__)

"""
This file contains examples of simple data requests to BetConnect
"""

NEXT_SCAN = 3 # Change this number to change the interval at which the next scan happens in seconds

# Get today's date
today = date.today()

# Configure logging to save output to a file
log_filename = f"Betconnect bets_{today}.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(log_filename, mode='a'),
        logging.StreamHandler()
    ]
)

# Create a trading client instance
client = None

# Flag variable for controlling the script loop
running = True

# Function to initialize the client and perform login
def initialize_client():
    global client
    client = betconnect.APIClient(
        username='jwillow84',
        password='password12345',
        api_key='5e82fede-91c2-493b-9209-c9cc133ec5ab',
        personalised_production_url='https://jwillow84.betconnect.com/'
    )
    # Login
    client.account.login()
    
# Function to run the script

def run_script():
    iteration = 1
    
    while running:
        
        # Get active sports with bets
        active_sports = client.betting.active_sports(with_bets=True)
        print("Active Sports:", len(active_sports))

        market_bet_request = []
        logged_bets = set()

        for active_sport in active_sports:
                
            if active_sport.bets_available == 0:
                continue
                
            if active_sport.display_name == "Horse Racing":
                print("Skipping Horse Racing sport...")
                print("\n")
                continue

            logging.info("Active sport: %s", active_sport.display_name)
            logging.info("Number of bets available total: %s", active_sport.bets_available)

            counter = active_sport.bets_available
            
            while counter > 0:
                try:
                    bet_request_get = client.betting.bet_request_get(
                        request_filter=filters.GetBetRequestFilter(sport_id=active_sport.sport_id)
                    )
                except Exception as e:
                    logging.error(f"Issue with request for: {client.betting.api_url}/bet_request_get, message: {str(e)}")
                    break

                if isinstance(bet_request_get, resources.BetRequest):
                    bet_info = (
                        bet_request_get.sport_name,
                        bet_request_get.competition_name,
                        bet_request_get.region_name,
                        bet_request_get.market_name,
                        bet_request_get.selection_name,
                        bet_request_get.competitor,
                        bet_request_get.start_time_utc,
                        bet_request_get.price.price,
                        bet_request_get.requested_stake,
                        bet_request_get.sport_id,
                        bet_request_get.fixture_name,
                        bet_request_get.fixture_id,
                        bet_request_get.market_type_id,
                        bet_request_get.liability,
                        bet_request_get.locked_stake,
                        bet_request_get.others_viewing_bet,
                        bet_request_get.lockable,
                        
                        
                    )
                    if bet_info not in logged_bets:
                        logged_bets.add(bet_info)
                        market_bet_request.append(bet_request_get)
                        counter -= 1
                        logging.info("Bet added:")
                        logging.info("Sport: %s", bet_request_get.sport_name)
                        logging.info("Competition name: %s", bet_request_get.competition_name)
                        logging.info("Region name: %s", bet_request_get.region_name)
                        logging.info("Market: %s", bet_request_get.market_name)
                        logging.info("Name: %s", bet_request_get.selection_name)
                        logging.info("Playing against: %s", bet_request_get.competitor)
                        logging.info("Time: %s", bet_request_get.start_time_utc)
                        logging.info("Pricing: %s", bet_request_get.price.price)
                        logging.info("Location: %s", bet_request_get.region_name)
                        logging.info("Stake: %s", bet_request_get.requested_stake)
                        
                        logging.info("Sport ID: %s", bet_request_get.sport_id)
                        logging.info("Fixture name: %s", bet_request_get.fixture_name)
                        logging.info("Fixture ID: %s", bet_request_get.fixture_id)
                        logging.info("Market type ID: %s", bet_request_get.market_type_id)
                        logging.info("Liability: %s", bet_request_get.liability)
                        logging.info("Locked stake: %s", bet_request_get.locked_stake)
                        logging.info("Others viewing bet: %s", bet_request_get.others_viewing_bet)
                        logging.info("Lockable : %s", bet_request_get.lockable)
                        
                        logging.info("\n")
                    elif bet_info in logged_bets:
                        logging.info(bet_request_get.selection_name + " has already been added.")

        # Sleep for a certain duration before running the script again
        # Adjust the sleep duration as per your requirement
        time.sleep(NEXT_SCAN)  # Sleep for 5 seconds
        print("Iteration:", iteration)
        iteration += 1

# Initialize the client and perform login
initialize_client()

# Start the script thread
script_thread = threading.Thread(target=run_script)
script_thread.start()
logging.info("Script thread started")
logging.info("\n")

try:
    while True:
        pass
except KeyboardInterrupt:
    running = False
    logging.info("Keyboard interrupt detected. Exiting...")
    logging.info("\n")

# Wait for the script thread to complete
script_thread.join()
logging.info("Script thread completed")

# Logout before exiting the program
client.account.logout()
