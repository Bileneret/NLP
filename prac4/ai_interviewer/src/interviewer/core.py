import google.generativeai as genai
from google.api_core import exceptions
import json
import os
from schemas import FeedbackScorecard
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

SYSTEM_INSTRUCTION = """
Ти - Senior Software Engineer та досвідчений технічний інтерв'юер у топовій IT-компанії.
Твоя мета: провести співбесіду з кандидатом на вказану посаду.
Правила:
1. Задавай по ОДНОМУ питанню за раз. Чекай на відповідь.
2. Питання мають бути технічними, практичними та відповідати рівню.
3. Anалізуй відповідь. Якщо неповна - задай уточнююче питання. Якщо повна - переходь до наступної теми.
4. Коли кандидат скаже "Завершити", попрощайся.
"""

def get_chat_session(role: str, level: str, is_demo: bool = False):
    try:
        current_instruction = SYSTEM_INSTRUCTION + f"\nПосада кандидата: {level} {role}."
        
        if is_demo:
            current_instruction += """
            \nУВАГА: ЦЕ ДЕМОНСТРАЦІЙНИЙ РЕЖИМ.
            Жорсткі правила для тебе:
            1. Задавай елементарні питання початкового рівня.
            2. Питання можуть бути у форматі тесту: саме питання і варіанти відповідей (А, Б, В, Г) або текстові питання з однією правильною відповіддю або поясненям.
            3. Питання мають бути у форматі текст-тест, текст-тест. Не змішуй формати. Почергово: одне текстове, одне тестове, і так далі.
            4. Не ігноруй вибраний рівень (Junior/Middle/Senior), але питання завжди мають бути найпростішими для цього рівня.
            5. Якщо кандидат написав правильну літеру - похвали його, коротко поясни чому це правильно і давай наступне питання.
            6. Якщо кандидат написав неправильну літеру - вкажи на помилку, коротко поясни правильну відповідь і дай наступний питання.
            """

        model = genai.GenerativeModel(
            model_name='gemini-3.1-flash-lite',
            system_instruction=current_instruction,
            generation_config=genai.types.GenerationConfig(
                
                temperature=0.4, # Низька температура для послідовних питань
                max_output_tokens=1000, # Обмеження на довжину відповіді, щоб уникнути надмірного тексту + економія токенів
                top_p=0.8, # Високий top_p для більш різноманітних запитань, але не надто хаотичних
            )
        )
        return model.start_chat(history=[])
    except exceptions.InvalidArgument as e:
        raise ValueError(f"Помилка валідації (InvalidArgument). Перевірте API ключ: {e}")
    except Exception as e:
        raise RuntimeError(f"Неочікувана помилка: {e}")

def get_feedback(chat_history: str) -> dict:
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        prompt = f"Проаналізуй цю історію співбесіди та згенеруй фідбек-скоркард:\n\n{chat_history}"
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=FeedbackScorecard,
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except exceptions.ResourceExhausted:
        raise PermissionError("Resource Exhausted: Перевищено ліміти Free Tier. Спробуйте пізніше.")
    except Exception as e:
        raise RuntimeError(f"Помилка генерації фідбеку: {e}")