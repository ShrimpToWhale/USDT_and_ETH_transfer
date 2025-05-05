import random
from src.utils.logger_config import logger
from dataclasses import dataclass
from typing import List, Tuple
from src.models.wallet import Wallet
import time

@dataclass
class UserConfig:
    min_account_delay: int
    max_account_delay: int  
    min_action_delay: int
    max_action_delay: int
    shuffle_wallets: bool


def get_delay_settings() -> Tuple[int, int, int, int]:

    while True:
        try:
            min_account_delay = int(input('Enter minimum delay between wallets: '))
            max_account_delay = int(input('Enter maximum delay between wallets: '))
            min_action_delay = int(input('Enter minimum delay between actions: '))
            max_action_delay = int(input('Enter maximum delay between actions: '))

            if (max_account_delay > min_account_delay) and (max_action_delay > min_action_delay):
                return min_account_delay, max_account_delay, min_action_delay, max_action_delay
            else:
                logger.error('Maximum delay must be greater than minimum')
        except ValueError:
            logger.error('The value you entered is not an integer digit')


def get_shuffle_setting() -> bool:

    while True:
        shuffle = input('Do you want to shuffle wallets (y/n)? ')
        if shuffle.lower() not in ('y', 'n'):
            logger.error('You entered an incorrect answer')
        else:
            return shuffle.lower() == 'y'


def get_user_config() -> UserConfig:
    min_account_delay, max_account_delay, min_action_delay, max_action_delay = get_delay_settings()
    shuffle_wallets = get_shuffle_setting()

    return UserConfig(
        min_account_delay=min_account_delay,
        max_account_delay=max_account_delay,
        min_action_delay=min_action_delay,
        max_action_delay=max_action_delay,
        shuffle_wallets=shuffle_wallets
    )


def shuffle_wallets_if_needed(wallets: List[Wallet], should_shuffle: bool) -> List[Wallet]:
    if should_shuffle:
        shuffled_wallets = wallets.copy()
        random.shuffle(shuffled_wallets)
        return shuffled_wallets
    return wallets


def sleep_between_actions(min_delay: int, max_delay: int) -> None:
    delay = random.randint(min_delay, max_delay)
    logger.info(f'Sleep for {delay} seconds between actions')
    time.sleep(delay)


def sleep_between_accounts(min_delay: int, max_delay: int) -> None:
    delay = random.randint(min_delay, max_delay)
    logger.info(f'Sleep for {delay} seconds between accounts')
    time.sleep(delay) 