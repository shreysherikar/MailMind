"""API routes for contact management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from priority_scoring.models.schemas import Contact, ContactCreate, ContactUpdate, AuthorityType
from shared.database import get_db, ContactDB

router = APIRouter(prefix="/api/v1/contacts", tags=["Contacts"])


@router.get("", response_model=List[Contact])
async def get_contacts(
    authority_type: Optional[AuthorityType] = Query(None, description="Filter by authority type"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all contacts with optional filtering.
    
    Contacts are used to determine sender authority for priority scoring.
    """
    query = db.query(ContactDB)
    
    if authority_type:
        query = query.filter(ContactDB.authority_type == authority_type.value)
    
    query = query.order_by(ContactDB.created_at.desc()).limit(limit)
    
    contacts = query.all()
    
    return [_db_to_contact(c) for c in contacts]


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: str,
    db: Session = Depends(get_db)
):
    """Get a single contact by ID."""
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return _db_to_contact(contact)


@router.get("/by-email/{email}", response_model=Contact)
async def get_contact_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Get a contact by email address."""
    contact = db.query(ContactDB).filter(ContactDB.email == email.lower()).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return _db_to_contact(contact)


@router.post("", response_model=Contact, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new contact with authority level.
    
    Authority types:
    - vip: C-level executives, founders, key stakeholders
    - manager: Direct managers, team leads
    - client: External clients, customers
    - recruiter: Recruiters, HR contacts
    - colleague: Team members, coworkers
    - external: External contacts, vendors
    - unknown: Unclassified contacts
    """
    # Check if contact already exists
    existing = db.query(ContactDB).filter(
        ContactDB.email == contact_data.email.lower()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Contact with this email already exists"
        )
    
    # Extract domain from email
    domain = None
    if "@" in contact_data.email:
        domain = contact_data.email.split("@")[1].lower()
    
    contact = ContactDB(
        id=str(uuid.uuid4()),
        email=contact_data.email.lower(),
        name=contact_data.name,
        authority_type=contact_data.authority_type.value,
        domain=domain,
        custom_priority_boost=contact_data.custom_priority_boost,
        notes=contact_data.notes
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return _db_to_contact(contact)


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: str,
    updates: ContactUpdate,
    db: Session = Depends(get_db)
):
    """Update a contact's properties."""
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_dict = updates.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    # Convert authority_type enum to string if present
    if "authority_type" in update_dict and update_dict["authority_type"]:
        update_dict["authority_type"] = update_dict["authority_type"].value
    
    for key, value in update_dict.items():
        if value is not None:
            setattr(contact, key, value)
    
    db.commit()
    db.refresh(contact)
    
    return _db_to_contact(contact)


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    db: Session = Depends(get_db)
):
    """Delete a contact."""
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Contact deleted successfully"}


@router.post("/bulk", response_model=List[Contact], status_code=201)
async def create_contacts_bulk(
    contacts: List[ContactCreate],
    db: Session = Depends(get_db)
):
    """Create multiple contacts at once."""
    if len(contacts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 contacts per request")
    
    created = []
    
    for contact_data in contacts:
        # Skip if already exists
        existing = db.query(ContactDB).filter(
            ContactDB.email == contact_data.email.lower()
        ).first()
        
        if existing:
            continue
        
        domain = None
        if "@" in contact_data.email:
            domain = contact_data.email.split("@")[1].lower()
        
        contact = ContactDB(
            id=str(uuid.uuid4()),
            email=contact_data.email.lower(),
            name=contact_data.name,
            authority_type=contact_data.authority_type.value,
            domain=domain,
            custom_priority_boost=contact_data.custom_priority_boost,
            notes=contact_data.notes
        )
        
        db.add(contact)
        created.append(contact)
    
    db.commit()
    
    return [_db_to_contact(c) for c in created]


def _db_to_contact(db_contact: ContactDB) -> Contact:
    """Convert database model to Contact schema."""
    return Contact(
        id=db_contact.id,
        email=db_contact.email,
        name=db_contact.name,
        authority_type=AuthorityType(db_contact.authority_type),
        domain=db_contact.domain,
        custom_priority_boost=db_contact.custom_priority_boost,
        notes=db_contact.notes,
        created_at=db_contact.created_at
    )
