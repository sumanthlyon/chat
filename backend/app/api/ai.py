from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.core.auth_dependencies import (
    get_current_user,
)

from app.database.models import User

from app.schema.ai import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
)

from app.services.ai_services import (
    analyse_message,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/analyse",
    response_model=MessageAnalysisResponse,
)
def analyse_chat_message(
    request: MessageAnalysisRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return analyse_message(
            request.text
        )

    except Exception as error:
        print(
            "AI ANALYSIS ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "AI analysis is currently unavailable"
            ),
        )