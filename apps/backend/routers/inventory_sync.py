from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio
import httpx
from pydantic import BaseModel
import os
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/inventory", tags=["Inventory Sync"])

class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

class InventoryItem(BaseModel):
    id: str
    name: str
    sku: str
    quantity: int
    location: Optional[str] = None
    variant: Optional[str] = None
    last_updated: datetime

class SyncResult(BaseModel):
    status: SyncStatus
    items_processed: int
    items_synced: int
    errors: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None

class BusinessCentralConfig(BaseModel):
    tenant_id: str
    environment: str
    company_id: str
    client_id: str
    client_secret: str
    base_url: str = "https://api.businesscentral.dynamics.com"

class ZohoConfig(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    base_url: str = "https://inventory.zoho.com/api/v1"

# Mock configuration (replace with actual config loading)
BC_CONFIG = BusinessCentralConfig(
    tenant_id=os.getenv("BC_TENANT_ID", "test-tenant"),
    environment=os.getenv("BC_ENVIRONMENT", "sandbox"),
    company_id=os.getenv("BC_COMPANY_ID", "test-company"),
    client_id=os.getenv("BC_CLIENT_ID", "test-client"),
    client_secret=os.getenv("BC_CLIENT_SECRET", "test-secret")
)

ZOHO_CONFIG = ZohoConfig(
    client_id=os.getenv("ZOHO_CLIENT_ID", "test-client"),
    client_secret=os.getenv("ZOHO_CLIENT_SECRET", "test-secret"),
    refresh_token=os.getenv("ZOHO_REFRESH_TOKEN", "test-token")
)

class InventorySyncService:
    def __init__(self):
        self.bc_token = None
        self.zoho_token = None
        self.sync_history = []

    async def get_bc_token(self) -> str:
        """Get OAuth token for Business Central"""
        logger.info("Requesting Business Central OAuth token")
        
        token_url = f"https://login.microsoftonline.com/{BC_CONFIG.tenant_id}/oauth2/v2.0/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": BC_CONFIG.client_id,
            "client_secret": BC_CONFIG.client_secret,
            "scope": "https://api.businesscentral.dynamics.com/.default"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self.bc_token = token_data["access_token"]
                logger.info("Successfully obtained Business Central token")
                return self.bc_token
            except httpx.HTTPError as e:
                logger.error(f"Failed to get BC token: {e}")
                raise HTTPException(status_code=401, detail="Failed to authenticate with Business Central")

    async def get_zoho_token(self) -> str:
        """Get OAuth token for Zoho"""
        logger.info("Requesting Zoho OAuth token")
        
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            "grant_type": "refresh_token",
            "client_id": ZOHO_CONFIG.client_id,
            "client_secret": ZOHO_CONFIG.client_secret,
            "refresh_token": ZOHO_CONFIG.refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self.zoho_token = token_data["access_token"]
                logger.info("Successfully obtained Zoho token")
                return self.zoho_token
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Zoho token: {e}")
                raise HTTPException(status_code=401, detail="Failed to authenticate with Zoho")

    async def fetch_bc_inventory(self) -> List[InventoryItem]:
        """Fetch inventory from Business Central"""
        logger.info("Fetching inventory from Business Central")
        
        if not self.bc_token:
            await self.get_bc_token()
        
        # Try standard API first
        standard_url = f"{BC_CONFIG.base_url}/v2.0/{BC_CONFIG.tenant_id}/{BC_CONFIG.environment}/api/v2.0/companies({BC_CONFIG.company_id})/items"
        
        # Fallback to automation API
        automation_url = f"{BC_CONFIG.base_url}/v2.0/{BC_CONFIG.tenant_id}/{BC_CONFIG.environment}/api/microsoft/automation/v2.0/companies({BC_CONFIG.company_id})/items"
        
        headers = {
            "Authorization": f"Bearer {self.bc_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Try standard API first
                logger.info(f"Trying standard API: {standard_url}")
                response = await client.get(standard_url, headers=headers)
                
                if response.status_code == 403:
                    logger.warning("Standard API returned 403, trying automation API")
                    response = await client.get(automation_url, headers=headers)
                
                response.raise_for_status()
                data = response.json()
                
                items = []
                for item_data in data.get("value", []):
                    items.append(InventoryItem(
                        id=item_data.get("id", ""),
                        name=item_data.get("displayName", ""),
                        sku=item_data.get("number", ""),
                        quantity=item_data.get("inventory", 0),
                        location=item_data.get("location", None),
                        variant=item_data.get("variant", None),
                        last_updated=datetime.now()
                    ))
                
                logger.info(f"Successfully fetched {len(items)} items from Business Central")
                return items
                
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch BC inventory: {e}")
                if hasattr(e, 'response'):
                    logger.error(f"Response status: {e.response.status_code}")
                    logger.error(f"Response body: {e.response.text}")
                raise HTTPException(status_code=500, detail=f"Failed to fetch inventory from Business Central: {str(e)}")

    async def sync_to_zoho(self, items: List[InventoryItem]) -> SyncResult:
        """Sync inventory items to Zoho"""
        logger.info(f"Syncing {len(items)} items to Zoho")
        
        if not self.zoho_token:
            await self.get_zoho_token()
        
        start_time = datetime.now()
        synced_count = 0
        errors = []
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.zoho_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            for item in items:
                try:
                    # Update item in Zoho
                    url = f"{ZOHO_CONFIG.base_url}/items/{item.sku}"
                    
                    payload = {
                        "name": item.name,
                        "sku": item.sku,
                        "stock_on_hand": item.quantity,
                        "location": item.location,
                        "variant": item.variant
                    }
                    
                    response = await client.put(url, json=payload, headers=headers)
                    
                    if response.status_code in [200, 201]:
                        synced_count += 1
                        logger.info(f"Successfully synced item {item.sku}")
                    else:
                        error_msg = f"Failed to sync item {item.sku}: {response.status_code}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        
                except Exception as e:
                    error_msg = f"Error syncing item {item.sku}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Determine status
        if synced_count == len(items):
            status = SyncStatus.SUCCESS
        elif synced_count > 0:
            status = SyncStatus.PARTIAL
        else:
            status = SyncStatus.FAILED
        
        result = SyncResult(
            status=status,
            items_processed=len(items),
            items_synced=synced_count,
            errors=errors,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration
        )
        
        self.sync_history.append(result)
        logger.info(f"Sync completed: {synced_count}/{len(items)} items synced in {duration:.2f}s")
        
        return result

# Service instance
sync_service = InventorySyncService()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "inventory_sync",
        "timestamp": datetime.now(),
        "config": {
            "bc_tenant": BC_CONFIG.tenant_id,
            "bc_environment": BC_CONFIG.environment,
            "zoho_configured": bool(ZOHO_CONFIG.refresh_token)
        }
    }

@router.post("/sync")
async def sync_inventory(background_tasks: BackgroundTasks):
    """Trigger inventory sync from Business Central to Zoho"""
    logger.info("Starting inventory sync process")
    
    try:
        # Fetch inventory from Business Central
        items = await sync_service.fetch_bc_inventory()
        
        if not items:
            logger.warning("No items found in Business Central")
            return SyncResult(
                status=SyncStatus.SUCCESS,
                items_processed=0,
                items_synced=0,
                errors=[],
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0
            )
        
        # Sync to Zoho
        result = await sync_service.sync_to_zoho(items)
        
        return result
        
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        return SyncResult(
            status=SyncStatus.FAILED,
            items_processed=0,
            items_synced=0,
            errors=[str(e)],
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=0
        )

@router.get("/history")
async def get_sync_history():
    """Get sync history"""
    return {
        "history": sync_service.sync_history,
        "total_syncs": len(sync_service.sync_history)
    }

@router.get("/test-bc-connection")
async def test_bc_connection():
    """Test Business Central connection"""
    logger.info("Testing Business Central connection")
    
    try:
        token = await sync_service.get_bc_token()
        
        # Test API call
        test_url = f"{BC_CONFIG.base_url}/v2.0/{BC_CONFIG.tenant_id}/{BC_CONFIG.environment}/api/v2.0/companies"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(test_url, headers=headers)
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_preview": response.text[:200] if response.text else None,
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"BC connection test failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/test-zoho-connection")
async def test_zoho_connection():
    """Test Zoho connection"""
    logger.info("Testing Zoho connection")
    
    try:
        token = await sync_service.get_zoho_token()
        
        # Test API call
        test_url = f"{ZOHO_CONFIG.base_url}/items"
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(test_url, headers=headers)
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_preview": response.text[:200] if response.text else None,
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"Zoho connection test failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/logs")
async def get_logs():
    """Get recent sync logs"""
    # This would typically read from a log file or database
    return {
        "message": "Logs endpoint - check server console for detailed logs",
        "log_level": "INFO",
        "timestamp": datetime.now()
    }