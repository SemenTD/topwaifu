from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import waifu

from callbaks.waifu_callbacks import WaifuTypeCallbackData, WaifuCategoryCallbackData
from keyboards.inline import sfw_categories_inline_keyboard, nsfw_categories_inline_keyboard
from states.waifu_states import WaifuTypeStatesGroup

waifu_router = Router()


@waifu_router.callback_query(WaifuTypeCallbackData.filter())
async def handle_waifu_type(query: CallbackQuery, callback_data: WaifuTypeCallbackData, state: FSMContext):
    if callback_data.type == 'sfw':
        await state.set_state(WaifuTypeStatesGroup.sfw)
        await query.message.answer('Вы выбрали обычные картинки:|. Выберите категорию',
                                   reply_markup=sfw_categories_inline_keyboard)
    else:
        await state.set_state(WaifuTypeStatesGroup.nsfw)
        await query.message.answer('Отличный выбор!. Выбирайте категорию',
                                   reply_markup=nsfw_categories_inline_keyboard)


@waifu_router.callback_query(WaifuCategoryCallbackData.filter(), StateFilter(WaifuTypeStatesGroup.sfw))
async def handle_sfw_category(query: CallbackQuery, callback_data: WaifuCategoryCallbackData, state: FSMContext):
    category = callback_data.category
    async with waifu.WaifuAioClient() as session:
        image = await session.sfw(category)

        if image.endswith(".gif"):
            await query.message.answer_animation(image, reply_markup=sfw_categories_inline_keyboard)
        else:
            await query.message.answer_photo(image, reply_markup=sfw_categories_inline_keyboard)


@waifu_router.callback_query(WaifuCategoryCallbackData.filter(), StateFilter(WaifuTypeStatesGroup.nsfw))
async def handle_nsfw_category(query: CallbackQuery, callback_data: WaifuCategoryCallbackData, state: FSMContext):
    category = callback_data.category
    async with waifu.WaifuAioClient() as session:
        image = await session.nsfw(category)
    await query.message.answer_photo(image, reply_markup=nsfw_categories_inline_keyboard)


@waifu_router.message(Command("waifu"))
async def get_waifu_command(message: Message):
    words = message.text.split()[1:]
    if len(words) == 2:
        waifu_type = words[0]
        waifu_category = words[1]
        if words[0] in ("sfw", "nsfw") and words[1] in waifu.ImageCategories[words[0]]:
            async with waifu.WaifuAioClient() as session:
                if waifu_type == "sfw":
                    image = await session.sfw(waifu_category)
                else:
                    image = await session.nsfw(waifu_category)
            await message.answer_photo(image)
        else:
            await message.answer("Возможно,вы ввели не правильную категорию.Попробуйте снова")
