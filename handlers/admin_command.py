import re

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, ApplicationHandlerStop

from database.user.models import User, Team

from database.db_functions import (
    reset_all_points,
    get_teams,
    delete_team,
)

from keyboards.keyboards import (
    query_team_keyboard,
    admin_keyboad,
)

(
    SELECTING_ACTION,
    ENTER_TEAM,
    ENTER_EDITING_TEAM,
    ENTER_TEAM_NEW_DATA,
    ENTER_DELETING_TEAM,
) = map(chr, range(5))

STOPPING = map(chr, range(5, 6))

END = ConversationHandler.END


async def admin(update: Update,
                context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    user = update.message.from_user.id
    admin_status = await User.get_or_none(
        telegram_id=user
    ).values('is_admin')

    try:
        if admin_status['is_admin']:
            save_data = await update.message.reply_text(
                text='Выбери один из пунктов меню.\n\n'
                     'Для завершения работы с админ меню '
                     'введи команду /stop',
                reply_markup=await admin_keyboad()
            )

            context.user_data['admin_message_id'] = int(save_data.message_id)

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


async def adding_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        ENTER_TEAM:
    text = 'Введи название стороны. Например: желтые.\n\n' \
           'Помни, что название должно быть уникальным.\n' \
           'Команда /stop отменит создание сотороны.'

    await update.callback_query.answer()

    await update.callback_query.edit_message_text(
        text=text
    )

    return ENTER_TEAM


async def commit_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    teams = await get_teams()

    text = update.message.text
    text = re.sub(r'[^а-яА-Яa-zA-Z]', '', text)
    text = text.lower().replace('ё', 'е')

    if text in teams:

        team_already_exists = 'Такая сторона уже существует.\n' \
                              'Введи другое название.\n\n' \
                              'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=team_already_exists)

        raise ApplicationHandlerStop(ENTER_TEAM)

    else:
        team_created = f'{text.capitalize()}, ' \
                       f'принято и записано в базу данных.'

        await Team.get_or_create(title=text)
        save_data = await context.bot.send_message(
            text=team_created,
            chat_id=update.effective_chat.id,
            reply_markup=await admin_keyboad()
        )

        context.user_data['admin_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(SELECTING_ACTION)


async def editing_team(update: Update,
                       context: CallbackContext.DEFAULT_TYPE) -> \
        ENTER_EDITING_TEAM:
    teams = await get_teams()

    if teams:
        edit_team_text = 'Выбери сторону, название которой хочешь изменить:\n\n' \
                         'Нажми на /stop, чтобы остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_team_text,
            reply_markup=await query_team_keyboard(update, context)
        )

        return ENTER_EDITING_TEAM

    else:
        no_teams = 'Нет команд, чтобы можно было что-то редактировать.'

        await update.callback_query.edit_message_text(
            text=no_teams,
            reply_markup=await query_team_keyboard(update, context)
        )

        return END


async def commit_editing_team(update: Update,
                              context: CallbackContext.DEFAULT_TYPE) -> \
        ENTER_TEAM_NEW_DATA:
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

    return ENTER_TEAM_NEW_DATA


async def update_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    saved_data = context.user_data['callback_data']

    teams = await get_teams()

    text = update.message.text
    text = re.sub(r'[^а-яА-Яa-zA-Z]', '', text)
    text = text.lower().replace('ё', 'е')

    if text in teams:
        team_already_exists = 'Такая сторона уже существует.\n' \
                              'Введи другое название.\n\n' \
                              'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=team_already_exists)

        return ENTER_TEAM_NEW_DATA

    else:
        await Team.filter(title=saved_data).update(title=text)

        update_success = f'{saved_data.capitalize()} - название ' \
                         f'изменено на {text.capitalize()}'

        save_data = await context.bot.send_message(
            text=update_success,
            chat_id=update.effective_chat.id,
            reply_markup=await admin_keyboad()
        )

        context.user_data.clear()
        context.user_data['admin_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(SELECTING_ACTION)


async def deleting_team(update: Update,
                        context: CallbackContext.DEFAULT_TYPE):
    teams = await get_teams()

    if teams:
        edit_team_text = 'Выбери сторону, которую необходимо удалить:\n\n' \
                         'Нажми на /stop, чтобы остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_team_text,
            reply_markup=await query_team_keyboard(update, context)
        )

        return ENTER_DELETING_TEAM

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

    save_data = await update.callback_query.edit_message_text(
        text=delete_success,
        reply_markup=await admin_keyboad()
    )

    context.user_data['admin_message_id'] = int(save_data.message_id)

    return SELECTING_ACTION


async def stop_admin_handler(update: Update,
                             context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    admin_stop_edit_message = 'Выполнение админских команд остановлено.'

    admin_stop_reply_text = 'Админ-меню было закрыто.\n' \
                            'Выполнение админских команд остановлено.\n' \
                            'Для повторного вызова вбей команду /admin.'

    await context.bot.edit_message_text(
        text=admin_stop_edit_message,
        chat_id=update.effective_chat.id,
        message_id=context.user_data.get('admin_message_id')
    )

    await update.effective_message.reply_text(
        text=admin_stop_reply_text
    )
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

    await update.callback_query.edit_message_text(
        text=text
    )

    return END
