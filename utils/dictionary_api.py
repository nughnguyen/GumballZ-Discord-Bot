"""
Dictionary API Service - Kiểm tra từ hợp lệ qua API
Hỗ trợ nhiều nguồn API và fallback strategy
"""
import aiohttp
import asyncio
import re
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

def clean_html(raw_html: str) -> str:
    """Remove HTML tags from string"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return ' '.join(cleantext.split())


class DictionaryAPI:
    """Base class cho Dictionary API"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def check_word(self, word: str, language: str) -> bool:
        """
        Kiểm tra từ có hợp lệ không
        
        Args:
            word: Từ cần kiểm tra
            language: 'vi' hoặc 'en'
        
        Returns:
            True nếu từ hợp lệ, False nếu không
        """
        raise NotImplementedError


class CambridgeDictionaryAPI(DictionaryAPI):
    """
    Cambridge Dictionary API cho Tiếng Anh
    Sử dụng Cambridge Dictionary web scraping
    Returns: (is_valid, word_info_dict)
    """
    
    BASE_URL = "https://dictionary.cambridge.org/dictionary/english"
    
    async def check_word(self, word: str, language: str) -> bool:
        """Check if English word is valid in Cambridge Dictionary"""
        result = await self.get_word_info(word, language)
        return result is not None
    
    async def get_word_info(self, word: str, language: str) -> dict:
        """
        Get word information from Cambridge Dictionary
        Returns: {
            'word': str,
            'phonetic': str,
            'definition': str,
            'is_advanced': bool (IELTS 7+, academic, etc)
        }
        """
        if language != 'en':
            return None
        
        await self.initialize()
        
        try:
            word_clean = word.lower().strip().replace(' ', '-')
            url = f"{self.BASE_URL}/{word_clean}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    # Check if it's a valid dictionary page
                    if 'class="def ddef_d db"' not in text and 'data-id="cald4"' not in text:
                        logger.info(f"❌ Cambridge: '{word}' not found")
                        return None
                    
                    # Extract information using simple string parsing
                    word_info = {
                        'word': word,
                        'phonetic': '',
                        'definition': '',
                        'level': None
                    }
                    
                    # Extract phonetic (IPA)
                    try:
                        ipa_start = text.find('class="ipa dipa')
                        if ipa_start > 0:
                            ipa_end = text.find('</span>', ipa_start)
                            ipa_section = text[ipa_start:ipa_end]
                            # Get text between > and <
                            ipa_text_start = ipa_section.rfind('>') + 1
                            phonetic = ipa_section[ipa_text_start:].strip()
                            if phonetic:
                                word_info['phonetic'] = f"/{phonetic}/"
                    except:
                        pass
                    
                    # Extract first definition
                    try:
                        def_start = text.find('class="def ddef_d db"')
                        if def_start > 0:
                            def_section = text[def_start:def_start+500]
                            def_text_start = def_section.find('>') + 1
                            def_text_end = def_section.find('</div>')
                            definition = def_section[def_text_start:def_text_end].strip()
                            # Clean HTML tags
                            definition = clean_html(definition)
                            word_info['definition'] = definition[:150]
                    except:
                        pass
                    
                    # Check for proficiency levels
                    text_lower = text.lower()
                    
                    # Regex to find exact level markers between tags
                    # Matches A1-C2, formal, academic, specialized, technical, literary, ielts, toeic
                    level_regex = r'>\s*(a1|a2|b1|b2|c1|c2|academic|formal|specialized|technical|literary|ielts|toeic)\s*<'
                    level_match = re.search(level_regex, text_lower)
                    
                    if level_match:
                        word_info['level'] = level_match.group(1)  # e.g., 'c1'
                    
                    logger.info(f"✅ Cambridge: '{word}' is valid (level: {word_info['level']})")
                    return word_info
                
                elif response.status == 404:
                    logger.info(f"❌ Cambridge: '{word}' - 404 not found")
                    return None
                else:
                    logger.warning(f"Cambridge API returned status {response.status} for word '{word}'")
                    return None
        
            return None
        
        except asyncio.TimeoutError:
            logger.error(f"⏰ Timeout checking Cambridge for word '{word}'")  
            return None
        except Exception as e:
            logger.error(f"❌ Error checking Cambridge for word '{word}': {e}")
            return None

    async def get_vietnamese_meaning(self, word: str) -> Optional[str]:
        """
        Get Vietnamese meaning from Cambridge English-Vietnamese Dictionary
        Returns: meaning string or None
        """
        try:
            word_clean = word.lower().strip().replace(' ', '-')
            url = f"https://dictionary.cambridge.org/dictionary/english-vietnamese/{word_clean}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if not self.session:
                await self.initialize()

            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    # Extract first translation
                    # Search for <span class="trans dtrans" lang="vi">
                    start_marker = 'class="trans dtrans" lang="vi">'
                    start_idx = text.find(start_marker)
                    
                    if start_idx > 0:
                        # Found it
                        content_start = start_idx + len(start_marker)
                        end_idx = text.find('</span>', content_start)
                        if end_idx > content_start:
                            meaning = text[content_start:end_idx].strip()
                            return clean_html(meaning)
                    
                    return None
                else:
                    return None
        except Exception as e:
            logger.error(f"❌ Error getting Vietnamese meaning for '{word}': {e}")
            return None


class FreeDictionaryAPI(DictionaryAPI):
    """
    Free Dictionary API cho Tiếng Anh (Backup cho Cambridge)
    URL: https://dictionaryapi.dev/
    """
    
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries"
    
    async def check_word(self, word: str, language: str) -> bool:
        """Check if English word is valid"""
        if language != 'en':
            return False
        
        await self.initialize()
        
        try:
            url = f"{self.BASE_URL}/en/{word.lower()}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    return True
                elif response.status == 404:
                    return False
                else:
                    logger.warning(f"Dictionary API returned status {response.status} for word '{word}'")
                    return False
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout checking word '{word}'")
            return False
        except Exception as e:
            logger.error(f"Error checking word '{word}': {e}")
            return False


class VietnameseDictionaryAPI(DictionaryAPI):
    """
    Vietnamese Dictionary API
    Sử dụng multiple sources
    """
    
    # API endpoints (có thể thêm nhiều sources)
    SOURCES = [
        # Tratu API (Vietnamese)
        "https://api.tracau.vn/WBBcwnwQpV89/tratu/api/v2/simple",
    ]
    
    async def check_word(self, word: str, language: str) -> bool:
        """Check if Vietnamese word is valid"""
        if language != 'vi':
            return False
        
        await self.initialize()
        
        # Try Tracau API
        try:
            url = f"https://api.tracau.vn/WBBcwnwQpV89/tratu/api/v2/simple"
            params = {'q': word.lower()}
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    # Kiểm tra có kết quả không
                    if data and 'error' not in data:
                        sentences = data.get('sentences', [])
                        # Nếu có câu ví dụ chứa từ này -> từ hợp lệ
                        if sentences:
                            return True
                    return False
                else:
                    return False
        
        except Exception as e:
            logger.error(f"Error checking Vietnamese word '{word}': {e}")
            return False


class HybridDictionaryService:
    """
    Hybrid service: sử dụng API trước, fallback về local files nếu API fail
    """
    
    def __init__(self, use_api: bool = True, fallback_words: Dict[str, set] = None):
        """
        Args:
            use_api: Có sử dụng API không
            fallback_words: Dictionary chứa local word lists {'vi': set(), 'en': set()}
        """
        self.use_api = use_api
        self.fallback_words = fallback_words or {'vi': set(), 'en': set()}
        
        # Initialize API services
        self.cambridge_api = CambridgeDictionaryAPI()  # PRIMARY for English
        self.free_dict_api = FreeDictionaryAPI()       # BACKUP for English
        self.vi_api = VietnameseDictionaryAPI()        # For Vietnamese
        
        # Cache để tránh gọi API nhiều lần cho cùng 1 từ
        self.cache: Dict[str, bool] = {}
        self.cache_size_limit = 1000
    
    async def initialize(self):
        """Initialize all API services"""
        if self.use_api:
            await self.cambridge_api.initialize()
            await self.free_dict_api.initialize()
            await self.vi_api.initialize()
    
    async def close(self):
        """Close all API sessions"""
        await self.cambridge_api.close()
        await self.free_dict_api.close()
        await self.vi_api.close()
    
    async def is_valid_word(self, word: str, language: str) -> bool:
        """
        Kiểm tra từ hợp lệ - Chiến lược:
        1. Check cache
        2. English: Cambridge Dictionary (primary) → Free Dictionary (backup) → Local
        3. Vietnamese: Tracau API → Local
        
        Args:
            word: Từ cần kiểm tra
            language: 'vi' hoặc 'en'
        
        Returns:
            True nếu từ hợp lệ
        """
        word_lower = word.lower().strip()
        cache_key = f"{language}:{word_lower}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = False
        
        # Try API first
        if self.use_api:
            try:
                if language == 'en':
                    # Try Cambridge first (most authoritative)
                    logger.info(f"🔍 Checking Cambridge for '{word}'...")
                    result = await self.cambridge_api.check_word(word_lower, language)
                    
                    # If Cambridge fails or not found, try Free Dictionary as backup
                    if not result:
                        logger.info(f"🔄 Cambridge not found, trying Free Dictionary...")
                        result = await self.free_dict_api.check_word(word_lower, language)
                    
                elif language == 'vi':
                    result = await self.vi_api.check_word(word_lower, language)
                
                # Nếu API thành công, cache và return
                if result:
                    self._add_to_cache(cache_key, result)
                    logger.info(f"✅ API confirmed '{word}' is valid")
                    return result
                else:
                    # API says word is invalid - this is definitive
                    logger.info(f"❌ API confirmed '{word}' is INVALID")
                    self._add_to_cache(cache_key, False)
                    return False
            
            except Exception as e:
                logger.warning(f"⚠️ API check failed for '{word}': {e}, falling back to local")
        
        # Fallback to local word list (chỉ khi API không available)
        if language in self.fallback_words:
            result = word_lower in self.fallback_words[language]
            logger.info(f"📚 Local fallback: '{word}' = {result}")
        
        # Cache result
        self._add_to_cache(cache_key, result)
        
        return result
    
    def _add_to_cache(self, key: str, value: bool):
        """Add to cache with size limit"""
        if len(self.cache) >= self.cache_size_limit:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = value
    
    def add_fallback_words(self, language: str, words: List[str]):
        """Add words to fallback list"""
        if language not in self.fallback_words:
            self.fallback_words[language] = set()
        
        self.fallback_words[language].update(w.lower().strip() for w in words)
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'limit': self.cache_size_limit,
            'hit_rate': 'N/A'  # Could implement hit rate tracking
        }


# Global instance (will be initialized in bot)
dictionary_service: Optional[HybridDictionaryService] = None


async def init_dictionary_service(use_api: bool = True, fallback_words: Dict[str, set] = None) -> HybridDictionaryService:
    """Initialize global dictionary service"""
    global dictionary_service
    
    dictionary_service = HybridDictionaryService(use_api=use_api, fallback_words=fallback_words)
    await dictionary_service.initialize()
    
    logger.info(f"Dictionary service initialized (API: {use_api})")
    
    return dictionary_service


async def close_dictionary_service():
    """Close global dictionary service"""
    global dictionary_service
    
    if dictionary_service:
        await dictionary_service.close()
        dictionary_service = None
