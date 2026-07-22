from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.hostel_schema import HostelAllocationCreate, HostelAllocationResponse, HostelBedCreate, HostelBedResponse, HostelBedUpdate, HostelBlockCreate, HostelBlockResponse, HostelBlockUpdate, HostelRoomCreate, HostelRoomResponse, HostelRoomUpdate, HostelTransferRequest
from app.services.hostel_service import hostel_allocation_service, hostel_bed_service, hostel_block_service, hostel_room_service

block_router = APIRouter()
@block_router.post("", response_model=HostelBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block(payload: HostelBlockCreate, session: AsyncSession = Depends(get_db)): return await hostel_block_service.create_block(session, payload.model_dump())
@block_router.get("", response_model=list[HostelBlockResponse])
async def get_blocks(session: AsyncSession = Depends(get_db)): return await hostel_block_service.get_blocks(session)
@block_router.get("/{item_id}", response_model=HostelBlockResponse)
async def get_block(item_id: UUID, session: AsyncSession = Depends(get_db)): return await hostel_block_service.get_block(session, item_id)
@block_router.put("/{item_id}", response_model=HostelBlockResponse)
async def update_block(item_id: UUID, payload: HostelBlockUpdate, session: AsyncSession = Depends(get_db)): return await hostel_block_service.update_block(session, item_id, payload.model_dump(exclude_unset=True))
@block_router.delete("/{item_id}")
async def delete_block(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await hostel_block_service.delete_block(session, item_id)
    return {"message": "Deleted successfully"}

room_router = APIRouter()
@room_router.post("", response_model=HostelRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(payload: HostelRoomCreate, session: AsyncSession = Depends(get_db)): return await hostel_room_service.create_room(session, payload.model_dump())
@room_router.get("", response_model=list[HostelRoomResponse])
async def get_rooms(session: AsyncSession = Depends(get_db)): return await hostel_room_service.get_rooms(session)
@room_router.get("/{item_id}", response_model=HostelRoomResponse)
async def get_room(item_id: UUID, session: AsyncSession = Depends(get_db)): return await hostel_room_service.get_room(session, item_id)
@room_router.put("/{item_id}", response_model=HostelRoomResponse)
async def update_room(item_id: UUID, payload: HostelRoomUpdate, session: AsyncSession = Depends(get_db)): return await hostel_room_service.update_room(session, item_id, payload.model_dump(exclude_unset=True))
@room_router.delete("/{item_id}")
async def delete_room(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await hostel_room_service.delete_room(session, item_id)
    return {"message": "Deleted successfully"}

bed_router = APIRouter()
@bed_router.post("", response_model=HostelBedResponse, status_code=status.HTTP_201_CREATED)
async def create_bed(payload: HostelBedCreate, session: AsyncSession = Depends(get_db)): return await hostel_bed_service.create_bed(session, payload.model_dump())
@bed_router.get("/available", response_model=list[HostelBedResponse])
async def get_available_beds(session: AsyncSession = Depends(get_db)): return await hostel_bed_service.get_available_beds(session)
@bed_router.get("", response_model=list[HostelBedResponse])
async def get_beds(session: AsyncSession = Depends(get_db)): return await hostel_bed_service.get_beds(session)
@bed_router.get("/{item_id}", response_model=HostelBedResponse)
async def get_bed(item_id: UUID, session: AsyncSession = Depends(get_db)): return await hostel_bed_service.get_bed(session, item_id)
@bed_router.put("/{item_id}", response_model=HostelBedResponse)
async def update_bed(item_id: UUID, payload: HostelBedUpdate, session: AsyncSession = Depends(get_db)): return await hostel_bed_service.update_bed(session, item_id, payload.model_dump(exclude_unset=True))
@bed_router.delete("/{item_id}")
async def delete_bed(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await hostel_bed_service.delete_bed(session, item_id)
    return {"message": "Deleted successfully"}

allocation_router = APIRouter()
@allocation_router.post("/allocate", response_model=HostelAllocationResponse, status_code=status.HTTP_201_CREATED)
async def allocate_student(payload: HostelAllocationCreate, session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.allocate(session, payload.model_dump())
@allocation_router.post("", response_model=HostelAllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_allocation(payload: HostelAllocationCreate, session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.allocate(session, payload.model_dump())
@allocation_router.get("", response_model=list[HostelAllocationResponse])
async def get_allocations(session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.get_allocations(session)
@allocation_router.get("/{item_id}", response_model=HostelAllocationResponse)
async def get_allocation(item_id: UUID, session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.get_allocation(session, item_id)
@allocation_router.post("/{allocation_id}/checkout", response_model=HostelAllocationResponse)
async def checkout_student(allocation_id: UUID, checkout_date: date, session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.checkout(session, allocation_id, checkout_date)
@allocation_router.post("/{allocation_id}/transfer", response_model=HostelAllocationResponse)
async def transfer_student(allocation_id: UUID, payload: HostelTransferRequest, session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.transfer(session, allocation_id, payload.model_dump())

student_hostel_router = APIRouter()
@student_hostel_router.get("/{student_id}/hostel", response_model=HostelAllocationResponse)
async def get_student_hostel(student_id: UUID, session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.get_student_allocation(session, student_id)

hostel_router = APIRouter()
@hostel_router.get("/dashboard")
async def hostel_dashboard(session: AsyncSession = Depends(get_db)): return await hostel_allocation_service.dashboard(session)
