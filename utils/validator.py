"""
Word Validator - Kiểm tra tính hợp lệ của từ
Xử lý cả Tiếng Việt và Tiếng Anh
Sử dụng API để validate từ (với fallback về local list)
"""
import unicodedata
import re
from typing import List, Tuple, Optional
from utils.dictionary_api import dictionary_service

class WordValidator:
    def __init__(self, language: str, word_list: List[str]):
        """
        Initialize validator với ngôn ngữ và danh sách từ
        
        Args:
            language: 'vi' hoặc 'en'
            word_list: Danh sách các từ hợp lệ
        """
        self.language = language
        self.word_list = set(w.lower().strip() for w in word_list)
    
    def normalize_vietnamese(self, text: str) -> str:
        """
        Chuẩn hóa text tiếng Việt (loại bỏ dấu nếu cần)
        """
        # Giữ nguyên dấu cho tiếng Việt
        return text.lower().strip()
    
    def get_last_char(self, word: str) -> str:
        """
        Lấy ký tự cuối cùng của từ
        Với tiếng Việt, lấy âm tiết cuối
        """
        word = word.lower().strip()
        
        if self.language == 'vi':
            # Tách theo khoảng trắng để lấy âm tiết cuối
            syllables = word.split()
            if syllables:
                return syllables[-1][0]  # Chữ cái đầu của âm tiết cuối
        
        # Tiếng Anh: chữ cái cuối
        return word[-1] if word else ''
    
    def get_first_char(self, word: str) -> str:
        """
        Lấy ký tự đầu tiên của từ
        """
        word = word.lower().strip()
        return word[0] if word else ''
    
    async def is_valid_word(self, word: str) -> bool:
        """
        Kiểm tra từ có hợp lệ không
        Sử dụng API nếu có, fallback về local list
        """
        word = word.lower().strip()
        
        # Nếu có dictionary service (API), dùng nó
        if dictionary_service:
            return await dictionary_service.is_valid_word(word, self.language)
        
        # Fallback: check local list
        return word in self.word_list
    
    async def can_chain(self, previous_word: str, new_word: str) -> Tuple[bool, str]:
        """
        Kiểm tra xem new_word có thể nối với previous_word không
        
        Returns:
            Tuple[bool, str]: (có hợp lệ không, lý do nếu không hợp lệ)
        """
        previous_word = previous_word.lower().strip()
        new_word = new_word.lower().strip()
        
        # Kiểm tra từ mới có trong dictionary không
        if not await self.is_valid_word(new_word):
            return False, f"Từ '{new_word}' không có trong từ điển!"
        
        # Lấy ký tự cuối của từ trước và ký tự đầu của từ mới
        last_char = self.get_last_char(previous_word)
        first_char = self.get_first_char(new_word)
        
        # So sánh
        if last_char != first_char:
            return False, f"Từ phải bắt đầu bằng '{last_char.upper()}' (từ trước kết thúc bằng '{last_char.upper()}')"
        
        return True, ""
    
    def is_long_word(self, word: str, threshold: int = 10) -> bool:
        """
        Kiểm tra từ có phải từ dài không (>= threshold ký tự)
        """
        return len(word.strip()) >= threshold
    
    def get_word_length(self, word: str) -> int:
        """
        Trả về độ dài của từ
        """
        return len(word.strip())
    
    def suggest_next_char(self, word: str) -> str:
        """
        Gợi ý ký tự đầu tiên cho từ tiếp theo
        """
        return self.get_last_char(word).upper()
    
    def find_possible_words(self, start_char: str, used_words: set, limit: int = 5) -> List[str]:
        """
        Tìm các từ có thể dùng bắt đầu bằng start_char (chưa dùng)
        
        Args:
            start_char: Ký tự bắt đầu
            used_words: Set các từ đã dùng
            limit: Số lượng từ tối đa trả về
        
        Returns:
            List các từ có thể dùng
        """
        start_char = start_char.lower()
        possible = [
            word for word in self.word_list 
            if word.startswith(start_char) and word not in used_words
        ]
        
        # Sắp xếp theo độ dài (ưu tiên từ dài cho bot challenge)
        possible.sort(key=len, reverse=True)
        
        return possible[:limit]
    
    def get_bot_word(self, start_char: str, used_words: set) -> str:
        """
        Bot chọn từ khó (dài và ít phổ biến) để thách đấu người chơi
        """
        possible = self.find_possible_words(start_char, used_words, limit=10)
        
        # Chọn từ dài nhất
        if possible:
            return possible[0]
        
        return None

    @property
    def cambridge_api(self):
        """Access to Cambridge API through global service"""
        if dictionary_service:
            return dictionary_service.cambridge_api
        return None
