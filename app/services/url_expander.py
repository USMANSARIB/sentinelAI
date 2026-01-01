import httpx
import redis
import json
import time
from urllib.parse import urlparse
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class URLExpander:
    def __init__(self):
        # Redis Connection for Caching
        self.redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
        self.suspicious_domains = set(['bit.ly', 'tinyurl.com']) # Initial seed

    async def expand_url(self, short_url, timeout=5):
        # 1. Check Cache
        cache_key = f"url:{short_url}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # 2. Expand
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, verify=False) as client:
                response = await client.head(short_url)
                final_url = str(response.url)
                domain = urlparse(final_url).netloc
                
                result = {
                    'final_url': final_url,
                    'domain': domain,
                    'status': response.status_code,
                    'is_suspicious': self.is_suspicious_domain(domain),
                    'expanded_at': time.time()
                }
                
                # 3. Store Cache (7 days)
                self.redis.setex(cache_key, 604800, json.dumps(result))
                return result
                
        except Exception as e:
            # Return error state but cache it briefly to avoid retry storms
            domain = urlparse(short_url).netloc
            error_result = {
                'final_url': short_url,
                'domain': domain,
                'is_suspicious': self.is_suspicious_domain(domain),
                'error': str(e)
            }
            self.redis.setex(cache_key, 3600, json.dumps(error_result))
            return error_result

    def is_suspicious_domain(self, domain):
        # Check local blacklist
        if domain in self.suspicious_domains:
            return True
        
        # Heuristics
        suspicious_patterns = ['.tk', '.ml', '.ga', '.cf', '.gq'] # Free TLDs
        if any(domain.endswith(p) for p in suspicious_patterns):
            return True
            
        return False

    async def process_batch(self, urls):
        tasks = [self.expand_url(u) for u in urls]
        return await asyncio.gather(*tasks)

# Helper wrapper for sync usage if needed
def expand_urls_sync(urls):
    expander = URLExpander()
    return asyncio.run(expander.process_batch(urls))
