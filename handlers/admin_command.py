import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database.user.models import User, Team, Location

from database.db_functions import (
    reset_all_points,
    get_teams,
    delete_team
)

SELECTING_ACTION, ADD_TEAM, EDIT_TEAM, \
    DELETE_TEAM, ENTERING_TEAM, \
    ENTERING_EDITING_TEAM, UPDATE_TEAM = map(chr, range(7))

ADD_POINT, EDIT_POINT, DELETE_POINT = map(chr, range(7, 10))

RESET_POINTS = map(chr, range(10, 11))

SHOW_ALL_USERS = map(chr, range(11, 12))

STOPPING = map(chr, range(12, 13))

END = ConversationHandler.END


async def admin(update: Update,
                context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    user = update.message.from_user.id
    admin_status = await User.get_or_none(
        telegram_id=user
    ).values('is_admin')

    buttons = [
        [
            InlineKeyboardButton("Add Team",
                                 callback_data=str(ADD_TEAM)),
            InlineKeyboardButton("Edit Team",
                                 callback_data=str(EDIT_TEAM)),
            InlineKeyboardButton("Del Team",
                                 callback_data=str(DELETE_TEAM))
        ],
        [
            InlineKeyboardButton("Add Point",
                                 callback_data=str(ADD_POINT)),
            InlineKeyboardButton("Edit Point",
                                 callback_data=str(EDIT_POINT)),
            InlineKeyboardButton("Del Point",
                                 callback_data=str(DELETE_POINT))
        ],
        [
            InlineKeyboardButton("Restart all points",
                                 callback_data=str(RESET_POINTS)),
        ],
        [
            InlineKeyboardButton("Show all users",
                                 callback_data=str(SHOW_ALL_USERS)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        if admin_status['is_admin']:
            await update.message.reply_text(
                text='Выбери один из пунктов меню.\n\n'
                     'Для завершения работы с админ меню '
                     'введи команду /stop',
                reply_markup=keyboard
            )

            return SELECTING_ACTION

        else:
            await update.message.reply_text(
                text='У тебя нет админских прав ¯\_(ツ)_/¯'
            )

            return END

    except TypeError:
        await update.message.reply_text(
            text='Без понятия кто ты, пройди регистрацию, '
                 'введя команду /callsign'
        )

        return END


async def list_of_teams_keyboard(update: Update,
                                 context: CallbackContext.DEFAULT_TYPE) -> \
        InlineKeyboardMarkup:
    await update.callback_query.answer()

    buttons = []
    teams = await get_teams()

    for team_title in teams:
        buttons.append(
            [
                InlineKeyboardButton(team_title.capitalize(),
                                     callback_data=str(
                                         f'TEAM_COLOR_{team_title.upper()}')
                                     )
            ]
        )

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


async def adding_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        ENTERING_TEAM:
    text = 'Введи название стороны. Например: желтые.\n\n' \
           'Помни, что название должно быть уникальным.\n' \
           'Команда /stop отменит создание сотороны.'

    await update.callback_query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

    return ENTERING_TEAM


async def commit_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    teams = await get_teams()

    text = update.message.text
    text = re.sub(r'[.\W.\d]', '', text)
    text = text.lower().replace('ё', 'е')

    if text in teams:

        team_already_exists = 'Такая сторона уже существует.\n' \
                              'Введи другое название.\n\n' \
                              'Команда /admin заново вызовет админ-меню.\n' \
                              'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=team_already_exists)

        return ENTERING_TEAM

    else:
        tean_created = f'{text.capitalize()}, ' \
                       f'принято и записано в базу данных.'

        await Team.get_or_create(title=text)
        await update.message.reply_text(text=tean_created)

        return SELECTING_ACTION


async def editing_team(update: Update,
                       context: CallbackContext.DEFAULT_TYPE) -> \
        ENTERING_EDITING_TEAM:
    teams = await get_teams()

    if teams:
        edit_team_text = 'Выбери сторону, название которой хочешь изменить:\n\n' \
                         'Нажми на /stop, чтобы остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_team_text,
            reply_markup=await list_of_teams_keyboard(update, context)
        )

        return ENTERING_EDITING_TEAM

    else:
        no_teams = 'Нет команд, чтобы можно было что-то редактировать.'

        await update.callback_query.edit_message_text(
            text=no_teams,
            reply_markup=await list_of_teams_keyboard(update, context)
        )

        return END


async def commit_editing_team(update: Update,
                              context: CallbackContext.DEFAULT_TYPE) -> \
        UPDATE_TEAM:
    await update.callback_query.answer()

    callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    context.user_data['callback_data'] = callback_data

    enter_new_titile = f'Вбей в текстовое поле название ' \
                       f'для команды "{callback_data.capitalize()}".\n\n' \
                       f'Для остановки обновления названия стороны и ' \
                       f'остановки админских команд используй команду:\n' \
                       f'/stop'

    await update.callback_query.edit_message_text(
        text=enter_new_titile
    )

    return UPDATE_TEAM


async def update_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    saved_data = context.user_data['callback_data']

    teams = await get_teams()

    text = update.message.text
    text = re.sub(r'[.\W.\d]', '', text)
    text = text.lower().replace('ё', 'е')

    if text in teams:
        team_already_exists = 'Такая сторона уже существует.\n' \
                              'Введи другое название.\n\n' \
                              'Команда /admin заново вызовет админ-меню.\n' \
                              'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=team_already_exists)

        return UPDATE_TEAM

    else:
        await Team.filter(title=saved_data).update(title=text)

        update_success = f'{saved_data.capitalize()} - название ' \
                         f'изменено на {text.capitalize()}'

        await update.message.reply_text(
            text=update_success
        )

        return END


async def deleting_team(update: Update,
                        context: CallbackContext.DEFAULT_TYPE):
    teams = await get_teams()

    if teams:
        edit_team_text = 'Выбери сторону, которую необходимо удалить:\n\n' \
                         'Нажми на /stop, чтобы остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_team_text,
            reply_markup=await list_of_teams_keyboard(update, context)
        )

        return DELETE_TEAM

    else:
        no_teams = 'Нет добавленных команд. Нечего удалять.'
        await update.callback_query.edit_message_text(
            text=no_teams
        )

        return END


async def commit_deleting_team(update: Update,
                               context: CallbackContext.DEFAULT_TYPE):
    await update.callback_query.answer()

    callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    await delete_team(callback_data)

    delete_success = f'{callback_data.capitalize()} - сторона удалена.\n' \
                     f'Предупредите участников этой стороны, что им требуется ' \
                     f'выбрать сторону заново. Ничего страшного не произойдет, ' \
                     f'если не предупредить, но вот будет неожиданость, когда ' \
                     f'бот при активации точки скажет игроку "ты не выбрал сторону!"'

    await update.callback_query.edit_message_text(
        text=delete_success
    )

    return END


async def stop_admin_handler(update: Update,
                             context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    text = 'Выполнение админских команд остановлено.'
    await update.message.reply_text(text=text)

    return END


async def end(update: Update,
              context: CallbackContext.DEFAULT_TYPE) -> END:
    await update.callback_query.answer()

    text = 'Выполнение админских команд остановлено.'
    await update.callback_query.edit_message_text(text=text)

    return END


async def restart_points(update: Update,
                         context: CallbackContext.DEFAULT_TYPE):
    await update.callback_query.answer()

    await reset_all_points()

    text = 'Значения точек восстановлены по умолчанию.\n\n' \
           'Все точки введены в игру.\n' \
           'Таймер установлен на 20 минут.\n' \
           'Точки не находятся под чьим-то контролем.'

    await update.callback_query.edit_message_text(text=text)

    return END
