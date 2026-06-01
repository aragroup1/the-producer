"""Celery tasks for Shopify integration."""

import os
from typing import Dict, Any, Optional

from celery import Celery
import structlog

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery('shopify')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')


LICENSE_TIERS = {
    'non_exclusive': {
        'price': 29.99,
        'description': 'Non-exclusive license. Beat remains available for others.',
        'includes': ['MP3', 'WAV'],
        'usage': 'Up to 10,000 streams, 1 music video, non-profit live performances'
    },
    'premium': {
        'price': 79.99,
        'description': 'Premium non-exclusive license with higher limits.',
        'includes': ['MP3', 'WAV', 'STEMS'],
        'usage': 'Up to 100,000 streams, unlimited videos, paid live performances'
    },
    'exclusive': {
        'price': 299.99,
        'description': 'Exclusive rights. Beat removed from store after purchase.',
        'includes': ['MP3', 'WAV', 'STEMS', 'MIDI'],
        'usage': 'Unlimited commercial use, full ownership transfer'
    }
}


class ShopifyIntegration:
    """Shopify store integration for beat sales."""
    
    def __init__(self):
        self.api_key = os.getenv('SHOPIFY_API_KEY')
        self.api_secret = os.getenv('SHOPIFY_API_SECRET')
        self.store_url = os.getenv('SHOPIFY_STORE_URL')
        self.access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.enabled = all([self.api_key, self.store_url, self.access_token])
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
    
    def _get_base_url(self) -> str:
        """Get Shopify API base URL."""
        return f"https://{self.store_url}/admin/api/2024-01"
    
    def create_product(self, beat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a Shopify product for a beat."""
        if not self.enabled:
            logger.warning("shopify_not_configured")
            return None
        
        try:
            import requests
            
            # Build product data
            title = beat_data.get('seo_title') or beat_data.get('title', 'Untitled Beat')
            description = self._build_description(beat_data)
            
            variants = []
            for tier_name, tier in LICENSE_TIERS.items():
                variants.append({
                    'title': tier_name.replace('_', ' ').title(),
                    'price': str(tier['price']),
                    'sku': f"{beat_data.get('slug', 'beat')}-{tier_name}",
                    'inventory_quantity': 1 if tier_name == 'exclusive' else 999,
                    'inventory_management': None,
                    'requires_shipping': False
                })
            
            product_data = {
                'product': {
                    'title': title,
                    'body_html': description,
                    'vendor': 'AI Producer',
                    'product_type': beat_data.get('genre', 'Beats'),
                    'tags': beat_data.get('tags', []),
                    'variants': variants,
                    'options': [{
                        'name': 'License',
                        'values': [v['title'] for v in variants]
                    }],
                    'metafields': [
                        {
                            'namespace': 'beat',
                            'key': 'bpm',
                            'value': str(beat_data.get('bpm', '')),
                            'type': 'number_integer'
                        },
                        {
                            'namespace': 'beat',
                            'key': 'key',
                            'value': beat_data.get('key_signature', ''),
                            'type': 'single_line_text_field'
                        },
                        {
                            'namespace': 'beat',
                            'key': 'duration',
                            'value': str(beat_data.get('duration_seconds', '')),
                            'type': 'number_integer'
                        }
                    ]
                }
            }
            
            url = f"{self._get_base_url()}/products.json"
            response = requests.post(url, json=product_data, headers=self._get_headers())
            
            if response.status_code == 201:
                product = response.json()['product']
                logger.info("shopify_product_created", product_id=product['id'])
                return product
            else:
                logger.error("shopify_product_create_failed", 
                           status=response.status_code, error=response.text)
                return None
        
        except Exception as e:
            logger.error("shopify_product_create_error", error=str(e))
            return None
    
    def _build_description(self, beat_data: Dict[str, Any]) -> str:
        """Build HTML product description."""
        genre = beat_data.get('genre', 'Instrumental')
        bpm = beat_data.get('bpm', '')
        key = beat_data.get('key_signature', '')
        duration = beat_data.get('duration_seconds', 0)
        
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
        
        html = f"""
        <h2>{beat_data.get('title', 'Untitled Beat')}</h2>
        <p>{beat_data.get('description', f'Premium {genre} beat produced by AI.')}</p>
        
        <h3>Track Details</h3>
        <ul>
            <li><strong>Genre:</strong> {genre}</li>
            <li><strong>BPM:</strong> {bpm}</li>
            <li><strong>Key:</strong> {key}</li>
            <li><strong>Duration:</strong> {duration_str}</li>
        </ul>
        
        <h3>License Options</h3>
        <table>
            <tr><th>License</th><th>Price</th><th>Includes</th></tr>
        """
        
        for tier_name, tier in LICENSE_TIERS.items():
            html += f"""
            <tr>
                <td>{tier_name.replace('_', ' ').title()}</td>
                <td>${tier['price']}</td>
                <td>{', '.join(tier['includes'])}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <p><strong>Instant download after purchase.</strong> All files delivered in high quality.</p>
        """
        
        return html
    
    def upload_digital_asset(self, beat_id: str, file_path: str,
                             file_name: str) -> Optional[str]:
        """Upload a digital file to Shopify."""
        # Shopify doesn't have a direct file upload API for digital products
        # This would typically use a digital downloads app or external CDN
        logger.info("digital_asset_upload", beat_id=beat_id, file=file_name)
        return None
    
    def update_inventory(self, product_id: str, variant_id: str,
                         quantity: int) -> bool:
        """Update product inventory."""
        if not self.enabled:
            return False
        
        try:
            import requests
            
            url = f"{self._get_base_url()}/variants/{variant_id}.json"
            data = {
                'variant': {
                    'id': variant_id,
                    'inventory_quantity': quantity
                }
            }
            
            response = requests.put(url, json=data, headers=self._get_headers())
            return response.status_code == 200
        
        except Exception as e:
            logger.error("inventory_update_failed", error=str(e))
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product from Shopify."""
        if not self.enabled:
            return False
        
        try:
            import requests
            
            url = f"{self._get_base_url()}/products/{product_id}.json"
            response = requests.delete(url, headers=self._get_headers())
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error("product_delete_failed", error=str(e))
            return False


# Initialize integration
shopify_integration = ShopifyIntegration()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def upload_beat_to_shopify(self, beat_id: str, beat_data: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a beat to Shopify store."""
    logger.info("shopify_upload_started", beat_id=beat_id)
    
    try:
        product = shopify_integration.create_product(beat_data)
        
        if product:
            logger.info("shopify_upload_completed", 
                       beat_id=beat_id, product_id=product['id'])
            
            return {
                "beat_id": beat_id,
                "status": "completed",
                "shopify_product_id": product['id'],
                "shopify_url": f"https://{shopify_integration.store_url}/products/{product['handle']}"
            }
        else:
            return {
                "beat_id": beat_id,
                "status": "failed",
                "error": "Failed to create Shopify product"
            }
    
    except Exception as e:
        logger.error("shopify_upload_failed", beat_id=beat_id, error=str(e))
        self.retry(exc=e)


@celery_app.task
def remove_beat_from_shopify(beat_id: str, product_id: str) -> Dict[str, Any]:
    """Remove a beat from Shopify (e.g., after exclusive sale)."""
    logger.info("shopify_removal_started", beat_id=beat_id, product_id=product_id)
    
    success = shopify_integration.delete_product(product_id)
    
    return {
        "beat_id": beat_id,
        "product_id": product_id,
        "removed": success
    }
