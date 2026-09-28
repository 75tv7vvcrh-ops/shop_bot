from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot import router
from services.database import products


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    query = inline_query.query
    results = []
    for product in products:
        if query.lower() in product["name"].lower():
            res = InlineQueryResultArticle(
                id=str(product["id"]),
                title=product["name"],
                input_message_content=InputTextMessageContent(
                    message_text=f"{product['name']} — {product['price']}₽"
                )
            )
            results.append(res)
    await inline_query.answer(results)