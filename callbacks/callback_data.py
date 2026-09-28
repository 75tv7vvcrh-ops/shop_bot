from aiogram.filters.callback_data import CallbackData


class ProductCallback(CallbackData, prefix="product"):
    product_id: int


class AddCartCallback(CallbackData, prefix="add_cart"):
    product_id: int