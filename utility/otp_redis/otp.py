from decouple import config  # noqa
import redis
import random


class CodeGenerator:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), db=0)

    def generate_and_store_code(self, phone_number):
        """
        Generate a verification code and store it in Redis associated with the phone number if it doesn't already exist.

        Args:
            phone_number (str): The phone number to associate the code with.

        Returns:
            str: The generated code or the existing code if it was already set.
        """
        code = ''.join(random.choices('0123456789', k=6))
        expiration_time = 120

        if self.redis_client.setnx(phone_number, code):
            self.redis_client.expire(phone_number, expiration_time)
            return code
        else:
            return self.redis_client.get(phone_number).decode()

    def get_code_for_number(self, phone_number):
        """
        Retrieve the verification code associated with a phone number from Redis.

        Args:
            phone_number (str): The phone number to retrieve the code for.

        Returns:
            str: The verification code associated with the phone number.
        """
        return self.redis_client.get(phone_number)
