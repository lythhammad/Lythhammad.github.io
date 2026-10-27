import logging
import os

from fastapi import Depends, HTTPException, status
from jwtdown_fastapi.authentication import Authenticator

from models.accounts import Account, AccountOut
from queries.accounts import AccountQueries

logger = logging.getLogger(__name__)


class MyAuthenticator(Authenticator):
    async def get_account_data(
        self,
        username: str,
        accounts: AccountQueries,
    ):
        # Basic input validation: reject empty/blank usernames before
        # they ever reach the database layer.
        if not username or not username.strip():
            logger.warning("Login attempt with empty username.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required.",
            )

        try:
            account = accounts.get_user_account(username)
        except Exception:
            # Don't let a database failure surface as a raw,
            # unhandled 500 with no record of what happened.
            logger.exception(
                "Error retrieving account data for username: %s", username
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to process login at this time.",
            )

        return account

    def get_account_getter(
        self,
        accounts: AccountQueries = Depends(),
    ):
        # Return the accounts. That's it.
        return accounts

    def get_hashed_password(self, account: Account):
        # Return the encrypted password value from your
        # account object
        if not account or not getattr(account, "hashed_password", None):
            logger.warning("get_hashed_password called with an invalid account.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid account credentials.",
            )
        return account.hashed_password

    def get_account_data_for_cookie(self, account: AccountOut):
        # Return the username and the data for the cookie.
        # You must return TWO values from this method.
        return account.username, AccountOut(**account.dict())


authenticator = MyAuthenticator(os.environ["SIGNING_KEY"])
