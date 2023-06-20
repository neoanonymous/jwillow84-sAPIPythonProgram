import logging
import asyncio
from datetime import date
import time
import betconnect
from betconnect import resources
from betconnect.resources import filters
import keyboard
import sys

# Get today's date
today = date.today()
current_time = time.strftime("%H:%M:%S")

# Configure logging to save output to a file
log_filename = f"Betconnect bets_{today}.txt"
default_logger = logging.getLogger("default")
default_logger.setLevel(logging.INFO)
default_logger.addHandler(logging.FileHandler(log_filename, mode='a'))

log_filename_australia = f"Betconnect bets_Australia_{today}.txt"
australia_logger = logging.getLogger("australia")
australia_logger.setLevel(logging.INFO)
australia_logger.addHandler(logging.FileHandler(log_filename_australia, mode='a'))

# Adding "betconnect" logger
betconnect_logger = logging.getLogger("betconnect")
betconnect_logger.setLevel(logging.INFO)
betconnect_logger.addHandler(logging.FileHandler(log_filename, mode='a'))
betconnect_logger.addHandler(logging.StreamHandler())

# Create a trading client instance
client = None

# Flag variable for controlling the script loop
running = True

# Function to initialize the client and perform login
async def initialize_client():
    global client
    client = betconnect.APIClient(
        username='jwillow84',
        password='Qwerty123!',
        api_key='5e82fede-91c2-493b-9209-c9cc133ec5ab',
        personalised_production_url='https://jwillow84.betconnect.com/'
    )
    # Login
    betconnect_logger.info("********************************************************************************")
    await asyncio.get_running_loop().run_in_executor(None, client.account.login)

def process_request_exception(self, response, response_json):
    if response.status_code == 400:
        sys.stderr.write(
            f"Bad Request for: {response.url}, message: {response_json.get('message')}"
        )
    elif response.status_code == 500:
        sys.stderr.write(
            f"Server Error for: {response.url}, message: {response_json.get('message')}"
        )
    elif response_json is None:
        sys.stderr.write(
            f"Unrecognized content encoding type for: {response.url}, message: {response_json.get('message')}"
        )
    else:
        # Log other unexpected statuses as well
        sys.stderr.write(
            f"Unexpected status code {response.status_code} for: {response.url}, message: {response_json.get('message')}"
        )
    return response_json

# Function to log the data to a different logger when the location is Australia
def log_bet_info(bet_info):
    logger = australia_logger if bet_info[2] == "Australia" else default_logger
    logger.info("-Bet added-")
    logger.info("Sport: %s", bet_info[0])
    logger.info("Competition name: %s", bet_info[1])
    logger.info("Region name: %s", bet_info[2])
    logger.info("Market: %s", bet_info[3])
    logger.info("Name: %s", bet_info[4])
    logger.info("Playing against: %s", bet_info[5])
    logger.info("Time: %s", bet_info[6])
    logger.info("Pricing: %s", bet_info[7])
    logger.info("Stake: %s", bet_info[8])
    logger.info("Sport ID: %s", bet_info[9])
    logger.info("Fixture name: %s", bet_info[10])
    logger.info("Fixture ID: %s", bet_info[11])
    logger.info("Market type ID: %s", bet_info[12])
    logger.info("Liability: %s", bet_info[13])
    logger.info("Locked stake: %s", bet_info[14])
    logger.info("Others viewing bet: %s", bet_info[15])
    logger.info("Lockable: %s", bet_info[16])
    logger.info("\n")

# Function to download bet data
async def download_bets():
    default_logger.info("Date: %s", today)
    default_logger.info("Time: %s", current_time)
    iteration = 1
    totalCounter = 0
    while running:
        # Get active sports with bets
        active_sports = await asyncio.to_thread(client.betting.active_sports, with_bets=True)

        market_bet_request = []
        logged_bets = set()

        print("----------------------------")

        for active_sport in active_sports:
            if active_sport.bets_available == 0:
                continue

            if active_sport.display_name == "Horse Racing":
                print("Skipping Horse Racing sport...")
                continue

            if active_sport.display_name == "Greyhounds":
                print("Skipping Greyhounds...")
                continue

            default_logger.info("Number of bets available total: %s", active_sport.bets_available)

            counter = active_sport.bets_available

            while counter > 0:
                try:
                    bet_request_get = await asyncio.to_thread(
                        client.betting.bet_request_get,
                        request_filter=filters.GetBetRequestFilter(sport_id=active_sport.sport_id)
                    )
                except Exception as e:
                    sys.stderr.write("Active sport ID when throwing an Exception %s", active_sport.sport_id)
                    sys.stderr.write(f"Issue with request for: {client.betting.api_url}/bet_request_get, message: {str(e)}")
                    await asyncio.sleep(10)
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
                        totalCounter += 1
                        log_bet_info(bet_info)  # Log to the correct logger
                    elif bet_info in logged_bets:
                        default_logger.info(bet_request_get.selection_name + " has already been added.")

        # Sleep for a certain duration before running the again
        # Adjust the sleep duration as per your requirement
        print("----------------------------------------")
        print("")
        await asyncio.sleep(1)  # Sleep for X seconds
        print("Iteration:", iteration)
        print("Bets logged this session:", totalCounter)
        iteration += 1

# Function to display bet data
async def display_bets():
    while running:
        print("Displaying bets...")
        await asyncio.sleep(1)  # Sleep for X seconds

async def main():
    default_logger.info("Script thread started")
    await initialize_client()

    # Create tasks
    download_task = asyncio.create_task(download_bets())
    display_task = asyncio.create_task(display_bets())

    # Wait for tasks to complete
    await asyncio.gather(download_task, display_task)

# Function to stop the script
def stop_script():
    global running
    running = False

    # Logout before exiting the program
    betconnect_logger.info("Script thread completed")
    client.account.logout()
    betconnect_logger.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

# Just set running to False in the hotkey callback
# keyboard.add_hotkey("esc", lambda: globals().update(running=False), suppress=True)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    stop_script()
