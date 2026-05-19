import pytest
from unittest.mock import patch, MagicMock
from google.api_core import exceptions
import json

# шлях відносно src/interviewer у pytest.ini
from core import get_chat_session, get_feedback # type: ignore

class TestChatSession:

    @patch('core.genai.GenerativeModel')
    def test_get_chat_session_success(self, mock_model_class):
        """Тест успішного створення сесії чату (Звичайний режим)"""
        mock_instance = MagicMock()
        mock_model_class.return_value = mock_instance
        mock_instance.start_chat.return_value = "mock_chat_session"

        session = get_chat_session(role="Python Developer", level="Junior", is_demo=False)
        
        assert session == "mock_chat_session"
        mock_model_class.assert_called_once()
        mock_instance.start_chat.assert_called_once_with(history=[])


    @patch('core.genai.GenerativeModel')
    def test_get_chat_session_invalid_key(self, mock_model_class):
        """Тест обробки помилки невалідного ключа (InvalidArgument)"""
        mock_model_class.side_effect = exceptions.InvalidArgument("Bad API Key")

        with pytest.raises(ValueError, match="Помилка валідації"):
            get_chat_session("DevOps", "Senior")

class TestFeedbackGeneration:
    @patch('core.genai.GenerativeModel')
    def test_get_feedback_success(self, mock_model_class):
        """Тест успішної генерації Scorecard (Structured Output)"""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "technical_score": 8,
            "communication_score": 9,
            "strong_points": ["Знає Python"],
            "areas_for_improvement": ["Слабкий у Docker"],
            "final_verdict": "Наймати"
        })
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_instance

        result = get_feedback("Історія чату...")

        assert result["technical_score"] == 8
        assert len(result["strong_points"]) == 1
        assert result["final_verdict"] == "Наймати"

    @patch('core.genai.GenerativeModel')
    def test_get_feedback_resource_exhausted(self, mock_model_class):
        """Тест обробки перевищення лімітів (ResourceExhausted)"""
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = exceptions.ResourceExhausted("Quota Exceeded")
        mock_model_class.return_value = mock_instance

        with pytest.raises(PermissionError, match="Resource Exhausted"):
            get_feedback("Історія чату...")