"""Shopify integration API endpoints.

Handles product sync, order webhooks, and sales tracking.
Requires SHOPIFY_SHOP_URL, SHOPIFY_API_KEY, SHOPIFY_API_SECRET env vars.
"""

import os
import uuid
import hmac
import hashlib
import base64
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.database import get_db
from shared.db.models import Beat, Sale, Genre
from shared.utils.security import decode_access_token

router = APIRouter()

# ─── Config ────────────────────────────────────────────────────────

SHOPIFY_SHOP_URL = os.getenv('SHOPIFY_SHOP_URL', '')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

# License tiers
LICENSE_TIERS = {
    'basic': {
        'name': 'Basic Lease',
        'price': 29.99,
        'description': 'MP3 file, 10,000 streams, non-exclusive, credit required',
        'compare_at_price': 49.99,
    },
    'premium': {
        'name': 'Premium',
        'price': 79.99,
        'description': 'WAV + Stems, 100,000 streams, non-exclusive, radio play allowed',
        'compare_at_price': 129.99,
    },
    'exclusive': {
        'name': 'Exclusive',
        'price': 299.99,
        'description': 'All files + stems, unlimited streams, full ownership, removed from store',
        'compare_at_price': 499.99,
    },
}


def _get_shopify_client():
    """Get Shopify API client if configured."""
    if not all([SHOPIFY_SHOP_URL, SHOPIFY_API_KEY, SHOPIFY_API_SECRET]):
        return None
    try:
        import shopify
        session = shopify.Session(SHOPIFY_SHOP_URL, SHOPIFY_API_VERSION, SHOPIFY_API_KEY)
        shopify.ShopifyResource.activate_session(session)
        return shopify
    except ImportError:
        return None


def _verify_webhook(data: bytes, hmac_header: str) -> bool:
    """Verify Shopify webhook HMAC signature."""
    if not SHOPIFY_API_SECRET:
        return False
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    ).digest()
    computed = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed, hmac_header)


# ─── Product Sync ──────────────────────────────────────────────────

@router.post("/sync")
async def sync_to_shopify(
    beat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Sync a single beat to Shopify store."""
    # Get beat from DB
    result = await db.execute(select(Beat).where(Beat.id == uuid.UUID(beat_id)))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    if beat.status not in ['approved', 'published']:
        raise HTTPException(status_code=400, detail="Beat must be approved before syncing")
    
    # Build product data
    genre_result = await db.execute(select(Genre).where(Genre.id == beat.genre_id))
    genre = genre_result.scalar_one_or_none()
    genre_name = genre.name if genre else 'Instrumental'
    
    product_data = {
        'title': beat.title or f'{genre_name} Beat — {beat.bpm} BPM',
        'body_html': _build_product_description(beat, genre_name),
        'vendor': 'The Producer',
        'product_type': 'Beat',
        'tags': [genre_name.lower(), str(beat.bpm) + 'bpm', beat.mood or ''] + (beat.tags or []),
        'variants': [
            {
                'title': tier['name'],
                'price': str(tier['price']),
                'compare_at_price': str(tier['compare_at_price']),
                'inventory_quantity': 999999 if key != 'exclusive' else 1,
                'inventory_management': 'shopify' if key == 'exclusive' else None,
                'sku': f"BEAT-{beat.id.hex[:8].upper()}-{key.upper()}",
                'requires_shipping': False,
                'taxable': True,
            }
            for key, tier in LICENSE_TIERS.items()
        ],
        'options': [{'name': 'License'}],
    }
    
    # Try to sync to Shopify
    shopify_client = _get_shopify_client()
    if shopify_client:
        try:
            product = shopify_client.Product()
            for key, value in product_data.items():
                setattr(product, key, value)
            product.save()
            
            beat.shopify_product_id = str(product.id)
            beat.shopify_status = 'synced'
            await db.commit()
            
            return {
                'beat_id': beat_id,
                'shopify_product_id': str(product.id),
                'status': 'synced',
                'url': f'https://{SHOPIFY_SHOP_URL}/products/{product.handle}',
            }
        except Exception as e:
            beat.shopify_status = 'failed'
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Shopify sync failed: {str(e)}")
    else:
        # Shopify not configured — store locally
        beat.shopify_status = 'pending'
        await db.commit()
        return {
            'beat_id': beat_id,
            'status': 'pending',
            'message': 'Shopify not configured. Set SHOPIFY_SHOP_URL, SHOPIFY_API_KEY, SHOPIFY_API_SECRET env vars.',
            'product_data': product_data,
        }


@router.post("/batch-sync")
async def batch_sync_to_shopify(
    status: str = "approved",
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Batch sync approved beats to Shopify."""
    result = await db.execute(
        select(Beat)
        .where(Beat.status == status)
        .where(Beat.shopify_status.is_(None))
        .limit(limit)
    )
    beats = result.scalars().all()
    
    synced = 0
    failed = 0
    
    for beat in beats:
        try:
            # Mark as pending (actual sync happens async via Celery)
            beat.shopify_status = 'pending'
            synced += 1
        except Exception:
            failed += 1
    
    await db.commit()
    
    return {
        'synced': synced,
        'failed': failed,
        'total': len(beats),
    }


@router.get("/products")
async def list_shopify_products(
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List beats synced to Shopify."""
    offset = (page - 1) * limit
    
    result = await db.execute(
        select(Beat)
        .where(Beat.shopify_product_id.isnot(None))
        .offset(offset)
        .limit(limit)
    )
    beats = result.scalars().all()
    
    return [
        {
            'id': str(b.id),
            'title': b.title,
            'shopify_product_id': b.shopify_product_id,
            'shopify_status': b.shopify_status,
            'genre': b.genre_id,
            'bpm': b.bpm,
            'price_basic': LICENSE_TIERS['basic']['price'],
            'price_premium': LICENSE_TIERS['premium']['price'],
            'price_exclusive': LICENSE_TIERS['exclusive']['price'],
        }
        for b in beats
    ]


# ─── Orders ────────────────────────────────────────────────────────

@router.get("/orders")
async def list_orders(
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List sales/orders from the database."""
    offset = (page - 1) * limit
    
    result = await db.execute(
        select(Sale)
        .order_by(Sale.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    sales = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(select(func.count(Sale.id)))
    total = count_result.scalar()
    
    return {
        'items': [
            {
                'id': str(s.id),
                'beat_id': str(s.beat_id),
                'license_type': s.license_type,
                'price': float(s.price),
                'customer_email': s.customer_email,
                'customer_name': s.customer_name,
                'shopify_order_id': s.shopify_order_id,
                'download_count': s.download_count,
                'created_at': s.created_at.isoformat() if s.created_at else None,
            }
            for s in sales
        ],
        'total': total,
        'page': page,
        'limit': limit,
    }


# ─── Webhooks ──────────────────────────────────────────────────────

@router.post("/webhook/order")
async def handle_order_webhook(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle Shopify order webhook for purchase fulfillment."""
    body = await request.body()
    
    # Verify webhook signature
    if x_shopify_hmac_sha256 and not _verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        import json
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Extract order info
    order_id = str(data.get('id', ''))
    customer_email = data.get('customer', {}).get('email', '')
    customer_name = data.get('customer', {}).get('first_name', '') + ' ' + data.get('customer', {}).get('last_name', '')
    line_items = data.get('line_items', [])
    
    sales_created = []
    
    for item in line_items:
        sku = item.get('sku', '')
        if not sku.startswith('BEAT-'):
            continue
        
        # Parse SKU: BEAT-{BEAT_ID}-{LICENSE}
        parts = sku.split('-')
        if len(parts) < 3:
            continue
        
        beat_id_hex = parts[1]
        license_type = parts[-1].lower()
        
        try:
            beat_id = uuid.UUID(beat_id_hex)
        except ValueError:
            continue
        
        # Find beat
        result = await db.execute(select(Beat).where(Beat.id == beat_id))
        beat = result.scalar_one_or_none()
        
        if not beat:
            continue
        
        # Create sale record
        price = float(item.get('price', 0))
        
        sale = Sale(
            beat_id=beat_id,
            license_type=license_type,
            price=price,
            customer_email=customer_email,
            customer_name=customer_name.strip(),
            shopify_order_id=order_id,
            shopify_line_item_id=str(item.get('id', '')),
        )
        
        db.add(sale)
        
        # Update beat sales count
        beat.sales_count = (beat.sales_count or 0) + 1
        beat.revenue = (beat.revenue or 0) + price
        
        # If exclusive, mark as sold
        if license_type == 'exclusive':
            beat.status = 'sold'
            beat.shopify_status = 'sold'
        
        sales_created.append({
            'beat_id': str(beat_id),
            'license_type': license_type,
            'price': price,
        })
    
    await db.commit()
    
    return {
        'status': 'processed',
        'order_id': order_id,
        'sales_created': len(sales_created),
        'items': sales_created,
    }


# ─── Helpers ───────────────────────────────────────────────────────

def _build_product_description(beat: Beat, genre_name: str) -> str:
    """Build HTML product description for Shopify."""
    return f"""
    <h2>{beat.title or f'{genre_name} Beat'}</h2>
    <p><strong>Genre:</strong> {genre_name}</p>
    <p><strong>BPM:</strong> {beat.bpm}</p>
    <p><strong>Key:</strong> {beat.key_signature or 'Unknown'}</p>
    <p><strong>Mood:</strong> {beat.mood or 'Various'}</p>
    <p><strong>Duration:</strong> {beat.duration_seconds // 60}:{beat.duration_seconds % 60:02d}</p>
    
    <h3>License Options</h3>
    <ul>
        <li><strong>Basic Lease (£29.99):</strong> MP3, 10K streams, non-exclusive</li>
        <li><strong>Premium (£79.99):</strong> WAV + Stems, 100K streams, radio play</li>
        <li><strong>Exclusive (£299.99):</strong> Full rights, unlimited, removed from store</li>
    </ul>
    
    <p>All beats are produced with professional-grade AI composition and mastering.</p>
    """
