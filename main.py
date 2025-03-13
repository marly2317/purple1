import api_key
from helper import _print_event
from datetime import datetime
import uuid
import os
import time
from httpx import HTTPStatusError
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import (
    recommend_capsule_wardrobe,
    recommend_style,
    fetch_product_by_title,
    fetch_product_by_category,
    fetch_product_by_brand,
    initialize_fetch,
    fetch_all_categories,
    fetch_recommendations,
    add_to_cart,
    remove_from_cart,
    view_checkout_info,
    get_delivery_estimate,
    get_payment_options,
)
from graph import ShoppingGraph
from db_init import init_database

def validate_message_order(messages):
    """Валидация порядка сообщений в цепочке"""
    last_role = None
    for msg in messages:
        if isinstance(msg, HumanMessage):
            if last_role == "tool":
                raise ValueError("Human message after tool message")
            last_role = "user"
        elif isinstance(msg, AIMessage):
            last_role = "assistant"
        elif isinstance(msg, ToolMessage):
            last_role = "tool"

def main():
    # Инициализация базы данных
    init_database()
    
    # Инициализация модели Mistral
    llm = init_chat_model("mistral-large-latest", model_provider="mistralai")

    # Шаблон для ассистента с MessagesPlaceholder
    primary_assistant_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """Вы строгий AI-стилист, работающий ТОЛЬКО по правилам:

1. На запросы со словами 'гардероб', 'капсул', 'комплект' → ТОЛЬКО инструмент recommend_capsule_wardrobe
2. Обязательные параметры:
   - gender: male/female (определять из контекста)
   - max_price: число (обязательно запрашивать если не указано)
   - situation: ВСЕГДА 'business meeting'
3. Запрещено использовать другие инструменты для этих запросов

Пример корректного вызова:
{{"tool": "recommend_capsule_wardrobe", "args": {{"situation": "business meeting", "gender": "male", "max_price": 10000}}}}
"""
        ),
        MessagesPlaceholder(variable_name="messages"),  # Используем MessagesPlaceholder для обработки сообщений
    ])

    # Привязка инструментов
    tools_no_confirmation = [
        recommend_capsule_wardrobe,
        recommend_style,
        fetch_product_by_title,
        fetch_product_by_category,
        fetch_product_by_brand,
        initialize_fetch,
        fetch_all_categories,
        fetch_recommendations,
        view_checkout_info,
        get_delivery_estimate,
        get_payment_options,
    ]
    tools_need_confirmation = [add_to_cart, remove_from_cart]

    assistant_runnable = primary_assistant_prompt | llm.bind_tools(
        tools_no_confirmation + tools_need_confirmation
    )

    # Создание ShoppingGraph
    shopping_graph = ShoppingGraph(assistant_runnable, tools_no_confirmation, tools_need_confirmation)

    # Уникальный ID сессии
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "user_id": thread_id,
            "thread_id": thread_id,
        }
    }

    print("Please wait for initialization...")
    
    # Инициализация с обработкой rate limit
    initial_query = "Please welcome me and show available products and categories."
    max_attempts = 5
    attempt = 0
    initial_events = None

    while attempt < max_attempts:
        try:
            # Передаем сообщения как список HumanMessage
            initial_events = shopping_graph.stream_responses({"messages": [HumanMessage(content=initial_query)]}, config)
            break
        except HTTPStatusError as err:
            if err.response.status_code == 429:
                retry_after = int(err.response.headers.get("Retry-After", 30))
                print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                attempt += 1
            else:
                print(f"HTTP Error: {err}")
                break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            break

    if initial_events is None:
        print("Failed to initialize after multiple attempts.")
        return

    # Вывод начальных данных
    for event in initial_events:
        try:
            validate_message_order(event["messages"])
            _print_event(event, set())
        except ValueError as ve:
            print(f"Validation error: {str(ve)}")
            break

    print("\nType your question below (or type 'exit' to end):\n")

    # Основной цикл
    while True:
        question = input("\nYou: ")
        if question.lower() == 'exit':
            print("Ending session. Thank you for using the shopping assistant!")
            break

        attempt = 0
        success = False
        while attempt < max_attempts and not success:
            try:
                # Передаем сообщения как список HumanMessage
                events = shopping_graph.stream_responses({"messages": [HumanMessage(content=question)]}, config)
                _printed = set()
                for event in events:
                    try:
                        validate_message_order(event["messages"])
                        _print_event(event, _printed)
                    except ValueError as ve:
                        print(f"Validation error: {str(ve)}")
                        break
                success = True
            except HTTPStatusError as err:
                if err.response.status_code == 429:
                    retry_after = int(err.response.headers.get("Retry-After", 30))
                    print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    attempt += 1
                else:
                    print(f"HTTP Error: {err}")
                    break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break

        if not success:
            print("Failed to process your request after multiple attempts.")

if __name__ == "__main__":
    main()