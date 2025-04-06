import asyncio
import config
from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(
    folder_id=config.YANDEX_FOLDER_ID, auth=config.YANDEX_GPT_API_KEY,
)

model = sdk.models.completions("yandexgpt-lite", model_version="latest")
model = model.configure(temperature=0.3)


async def ask_yandex_gpt(question: str, context: [str]) -> str:
    """
    Асинхронно отправляет запрос к YandexGPT с заданным вопросом
    и возвращает сгенерированный ответ.
    """

    try:
        # Формируем список сообщений: сначала основной вопрос, затем контекст
        messages = [{"role": "system", "text": question}]
        messages += [{"role": "user", "text": item} for item in context]

        # Оборачиваем вызов model.run в asyncio.to_thread, чтобы не блокировать event loop
        result = await asyncio.to_thread(model.run, messages)

        answer = result.alternatives[0].text
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# Пример использования:
if __name__ == '__main__':
    async def main():
        question = "Напиши 5 названий для нового смартфона от производителя Тolk. Объясни свои идеи."
        answer = await ask_yandex_gpt(question, ["Это пример контекста.", "Вот ещё один пример.", "И ещё один."])
        print("Ответ YandexGPT:\n", answer)


    asyncio.run(main())