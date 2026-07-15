from collections import Counter
from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admission_model import AdmissionApplicationStatus
from app.models.class_model import Class
from app.models.user import User
from app.repositories.admission_repository import (
    admission_application_repository,
    admission_document_repository,
)


class AdmissionApplicationService:
    async def create_application(self, session: AsyncSession, data: dict):
        await self._validate_application(session, data)
        item = await admission_application_repository.create(session, data)
        await session.commit()
        return item

    async def update_application(
        self, session: AsyncSession, application_id: UUID, data: dict
    ):
        item = await self.get_application(session, application_id)
        merged = {
            "applicant_name": item.applicant_name,
            "applied_class": item.applied_class,
            "application_date": item.application_date,
            "status": item.status,
            "remarks": item.remarks,
        }
        merged.update(data)
        await self._validate_application(session, merged)
        item = await admission_application_repository.update(session, item, data)
        await session.commit()
        return item

    async def delete_application(self, session: AsyncSession, application_id: UUID):
        item = await self.get_application(session, application_id)
        await admission_application_repository.delete(session, item)
        await session.commit()

    async def get_application(self, session: AsyncSession, application_id: UUID):
        item = await admission_application_repository.get_by_id(session, application_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admission application not found",
            )
        return item

    async def get_applications(self, session: AsyncSession):
        return await admission_application_repository.get_all(session)

    async def get_by_status(self, session: AsyncSession, status_value: str):
        normalized = self._validate_status(status_value)
        return await admission_application_repository.get_by_status(session, normalized)

    async def get_summary(self, session: AsyncSession) -> dict:
        applications = await self.get_applications(session)
        counts = Counter(
            app.status.value if hasattr(app.status, "value") else app.status
            for app in applications
        )
        return {
            "total_applications": len(applications),
            "pending": counts["PENDING"],
            "approved": counts["APPROVED"],
            "rejected": counts["REJECTED"],
        }

    async def approve_application(self, session: AsyncSession, application_id: UUID):
        item = await self.get_application(session, application_id)
        documents = await admission_document_repository.get_by_application(
            session, application_id
        )
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one verified document is required before approval",
            )
        if any(not document.verified for document in documents):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All documents must be verified before approval",
            )
        item = await admission_application_repository.update(
            session, item, {"status": AdmissionApplicationStatus.APPROVED}
        )
        await session.commit()
        return item

    async def _validate_application(self, session: AsyncSession, data: dict) -> None:
        if not str(data["applicant_name"]).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Applicant name cannot be empty",
            )
        if await session.get(Class, data["applied_class"]) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Applied class must exist",
            )
        if data["application_date"] > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application date cannot be in the future",
            )
        data["status"] = self._validate_status(data["status"])

    def _validate_status(self, status_value) -> AdmissionApplicationStatus:
        if isinstance(status_value, AdmissionApplicationStatus):
            return status_value
        normalized = str(status_value).upper()
        if normalized not in AdmissionApplicationStatus.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="status must be one of PENDING, UNDER_REVIEW, APPROVED, REJECTED",
            )
        return AdmissionApplicationStatus(normalized)


class AdmissionDocumentService:
    async def create_document(self, session: AsyncSession, data: dict):
        await self._validate_document(session, data)
        item = await admission_document_repository.create(session, data)
        await session.commit()
        return item

    async def update_document(self, session: AsyncSession, document_id: UUID, data: dict):
        item = await self.get_document(session, document_id)
        merged = {
            "application_id": item.application_id,
            "document_type": item.document_type,
            "file_path": item.file_path,
            "verified": item.verified,
            "verified_by": item.verified_by,
            "verified_date": item.verified_date,
        }
        merged.update(data)
        await self._validate_document(session, merged)
        item = await admission_document_repository.update(session, item, data)
        await session.commit()
        return item

    async def verify_document(
        self, session: AsyncSession, document_id: UUID, data: dict
    ):
        item = await self.get_document(session, document_id)
        update_data = {
            "verified": True,
            "verified_by": data["verified_by"],
            "verified_date": data["verified_date"],
        }
        merged = {
            "application_id": item.application_id,
            "document_type": item.document_type,
            "file_path": item.file_path,
            **update_data,
        }
        await self._validate_document(session, merged)
        item = await admission_document_repository.update(session, item, update_data)
        await session.commit()
        return item

    async def delete_document(self, session: AsyncSession, document_id: UUID):
        item = await self.get_document(session, document_id)
        await admission_document_repository.delete(session, item)
        await session.commit()

    async def get_document(self, session: AsyncSession, document_id: UUID):
        item = await admission_document_repository.get_by_id(session, document_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admission document not found",
            )
        return item

    async def get_documents(self, session: AsyncSession):
        return await admission_document_repository.get_all(session)

    async def get_by_application(self, session: AsyncSession, application_id: UUID):
        if await admission_application_repository.get_by_id(session, application_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admission application not found",
            )
        return await admission_document_repository.get_by_application(
            session, application_id
        )

    async def _validate_document(self, session: AsyncSession, data: dict) -> None:
        if await admission_application_repository.get_by_id(
            session, data["application_id"]
        ) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application must exist",
            )
        if not str(data["document_type"]).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document type cannot be empty",
            )
        if not str(data["file_path"]).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File path cannot be empty",
            )
        if data.get("verified"):
            if not data.get("verified_by") or not data.get("verified_date"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="verified_by and verified_date are required when verified is true",
                )
            if await session.get(User, data["verified_by"]) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verifier user must exist",
                )


admission_application_service = AdmissionApplicationService()
admission_document_service = AdmissionDocumentService()
