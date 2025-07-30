from api_helper import ShoonyaApiPy
import pyotp

# Make sure to install pyotp: pip install pyotp

# I'll need to import the config. To make this a module, I'll use a relative import.
# When running scripts inside the trading_bot directory, python path might need to be set.
# For now, I'll assume standard package structure.
try:
    from . import config
except ImportError:
    import config


class Authenticator:
    """
    Handles the authentication with the Shoonya API.
    """
    def __init__(self):
        self.api = ShoonyaApiPy()
        self.credentials = config.credentials

    def login(self):
        """
        Logs into the Shoonya API using credentials from the config file.
        It can handle both a direct TOTP pin or generate one if a secret key is provided.
        """
        two_fa_value = self.credentials['factor2']

        # Check if the factor2 value is a TOTP secret key (typically longer than 6 digits)
        if len(str(two_fa_value)) > 8:
            try:
                totp = pyotp.TOTP(two_fa_value).now()
            except Exception as e:
                print(f"Failed to generate TOTP from the provided key: {e}")
                return None
        else:
            totp = two_fa_value

        ret = self.api.login(
            userid=self.credentials['user'],
            password=self.credentials['pwd'],
            twoFA=totp,
            vendor_code=self.credentials['vc'],
            api_secret=self.credentials['apikey'],
            imei=self.credentials['imei']
        )

        if ret and ret.get('stat') == 'Ok':
            print("Successfully logged in.")
            return self.api
        else:
            error_msg = ret.get('emsg') if ret else "Unknown error"
            print(f"Login failed: {error_msg}")
            return None

# Example of how to use this module
if __name__ == '__main__':
    # This block is for testing purposes.
    # It demonstrates how to instantiate and use the Authenticator.
    # Note: You need to have a valid config.py with credentials for this to work.

    print("Testing Authenticator...")
    authenticator = Authenticator()
    # The login will fail because the credentials in config.py are placeholders.
    api_session = authenticator.login()

    if api_session:
        print("Authentication successful. API session object created.")
        # You can now use the api_session object to make other API calls.
        # For example:
        # holdings = api_session.get_holdings()
        # print(holdings)
    else:
        print("Authentication failed.")
