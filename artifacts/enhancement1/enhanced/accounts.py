import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from authenticator import authenticator
from models.accounts import (
    AccountForm,
    AccountIn,
    AccountList,
    AccountOut,
    AccountToken,
    HttpError,
)
from queries.accounts import AccountQueries, DuplicateAccountError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/accounts", response_model=AccountToken | HttpError)
async def create_account(
    info: AccountIn,
    request: Request,
    response: Response,
    accounts: AccountQueries = Depends(),
):
    # Basic input validation/sanitization beyond what Pydantic already
    # guarantees at the type level.
    username = info.username.strip() if info.username else ""
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty.",
        )
    if not info.password or len(info.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long.",
        )
    info.username = username

    hashed_password = authenticator.hash_password(info.password)

    try:
        account = accounts.create_account(info, hashed_password)
    except DuplicateAccountError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    except Exception:
        # Anything other than a duplicate account was previously an
        # unhandled 500 with no record of what went wrong.
        logger.exception(
            "Unexpected error creating account for username: %s", username
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create account at this time.",
        )

    form = AccountForm(username=info.username, password=info.password)

    try:
        token = await authenticator.login(response, request, form, accounts)
    except Exception:
        logger.exception(
            "Account created but login failed for username: %s", username
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account created, but automatic login failed. Please log in.",
        )

    return AccountToken(account=account, **token.dict())


@router.get("/token", response_model=AccountToken | None)
async def get_token(
    request: Request,
    account: AccountOut = Depends(authenticator.try_get_current_account_data),
) -> AccountToken | None:
    # Explicit return in every branch, matching the declared response
    # model instead of relying on an implicit None.
    if account and authenticator.cookie_name in request.cookies:
        return AccountToken(
            access_token=request.cookies[authenticator.cookie_name],
            type="Bearer",
            account=account,
        )
    return None


@router.get("/api/accounts", response_model=AccountList)
def accounts_list(queries: AccountQueries = Depends()):
    try:
        return {"accounts": queries.get_all_accounts()}
    except Exception:
        logger.exception("Unexpected error retrieving account list.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve accounts at this time.",
        )
