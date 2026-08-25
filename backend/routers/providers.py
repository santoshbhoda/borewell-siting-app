"""
Providers Router: Verified Drilling Contractors & VES Geophysicists Directory
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ServiceProvider
from backend.schemas import ProviderResponse

router = APIRouter(prefix="/providers", tags=["Contractor & VES Directory"])


@router.get("", response_model=List[ProviderResponse])
def list_providers(
    provider_type: Optional[str] = Query(None, description="Filter by 'VES_GEOPHYSICIST' or 'DRILLING_CONTRACTOR'"),
    db: Session = Depends(get_db)
):
    """Lists verified local drilling rig contractors and hydrogeological survey providers."""
    query = db.query(ServiceProvider).filter(ServiceProvider.is_verified == True)
    if provider_type:
        query = query.filter(ServiceProvider.provider_type == provider_type)
    
    return query.order_by(ServiceProvider.rating.desc()).all()
