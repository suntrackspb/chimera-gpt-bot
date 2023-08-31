from aiogram import types


async def setup_bot_commands(bot):
    bot_commands = [
        types.BotCommand(command="/start", description="Запуск бота"),
        types.BotCommand(command="/help", description="Описание команд и функций"),
        types.BotCommand(command="/img", description="Генерация изображения"),
        types.BotCommand(command="/profile", description="Профиль пользователя"),
        types.BotCommand(command="/new", description="Очистить роль и контекст диалога"),
        types.BotCommand(command="/add", description="Установить роль для чат бота"),
        types.BotCommand(command="/role", description="Показать текущую роль"),
    ]
    await bot.set_my_commands(bot_commands)
