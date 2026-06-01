"""Shopify integration API endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/sync")
async def sync_to_shopify(beat_id: uuid.UUID):
    """Sync a beat to Shopify store."""
    # TODO: Implement
    return {"beat_id": beat_id, "status": "syncing"}


@router.post("/batch-sync")
async def batch_sync_to_shopify(
    status: str = "approved",
    limit: int = 50
):
    """Batch sync beats to Shopify."""
    # TODO: Implement
    return {"synced": 0, "failed": 0}


@router.get("/products")
async def list_shopify_products(
    page: int = 1,
    limit: int = 50
):
    """List products in Shopify store."""
    # TODO: Implement
    return []


@router.get("/orders")
async def list_orders(
    page: int = 1,
    limit: int = 50
):
    """List Shopify orders."""
    # TODO: Implement
    return []


@router.post("/webhook/order")
async def handle_order_webhook():
    """Handle Shopify order webhook."""
    # TODO: Implement
    return {"status": "received"}
