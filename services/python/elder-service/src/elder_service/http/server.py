from __future__ import annotations

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status

from elder_service.application.service import (
    ElderProfileAlreadyExistsError,
    ElderProfileNotFoundError,
    ElderService,
)
from elder_service.http.schemas import (
    ElderProfileCreateRequest,
    ElderProfileListResponse,
    ElderProfileResponse,
)
from elder_service.service import create_default_service


def create_app(service: ElderService | None = None) -> FastAPI:
    service = service or create_default_service()

    app = FastAPI(
        title="elder-service",
        version="0.1.0",
        description="Regional Health Platform elder profile service",
    )

    def get_service() -> ElderService:
        return service

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/elders", response_model=ElderProfileListResponse)
    def list_profiles(service: ElderService = Depends(get_service)) -> ElderProfileListResponse:
        items = [ElderProfileResponse.from_domain(profile) for profile in service.list_profiles()]
        return ElderProfileListResponse(items=items)

    @app.get("/elders/{elder_id}", response_model=ElderProfileResponse)
    def get_profile(elder_id: str, service: ElderService = Depends(get_service)) -> ElderProfileResponse:
        try:
            profile = service.get_profile(elder_id)
        except ElderProfileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return ElderProfileResponse.from_domain(profile)

    @app.post(
        "/elders",
        response_model=ElderProfileResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_profile(
        payload: ElderProfileCreateRequest,
        service: ElderService = Depends(get_service),
    ) -> ElderProfileResponse:
        try:
            profile = service.create_profile(
                elder_id=payload.elder_id,
                elder_code=payload.elder_code,
                full_name=payload.full_name,
                age=payload.age,
                risk_level=payload.risk_level,
                stay_info=payload.stay_info.to_domain(),
                family_contacts=[contact.to_domain() for contact in payload.family_contacts],
            )
        except ElderProfileAlreadyExistsError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

        return ElderProfileResponse.from_domain(profile)

    return app


app = create_app()


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    uvicorn.run("elder_service.http.server:app", host=host, port=port, reload=False)
