import re
import threading

from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    ApplicationHandlerStop,
)

from database.user.models import (
    User,
    Team,
    Location,
)

from database.db_functions import (
    reset_all_points,
    get_teams,
    delete_team,
    get_points,
    delete_point,
)

from keyboards.keyboards import (
    query_teams_keyboard,
    query_points_keyboard,
    admin_keyboard,
    back_to_menu,
)

(
    SELECTING_ACTION,
    ENTER_TEAM,
    ENTER_EDITING_TEAM,
    ENTER_TEAM_NEW_DATA,
    ENTER_DELETING_TEAM,
    ENTER_POINT,
    ENTER_POINT_COORDINATES,
    ENTER_DELETING_POINT,
) = map(chr, range(8))

BACK_TO_MENU = map(chr, range(8, 9))

END = ConversationHandler.END


async def admin(update: Update,
                context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    try:
        user = update.message.from_user.id
        admin_status = await User.get_or_none(
            telegram_id=user
        ).values('is_admin')

        try:
            if admin_status['is_admin']:
                admin_text = 'Выбери один из пунктов меню.\n\n' \
                             'Для завершения работы с админ меню ' \
                             'введи команду /stop'
                save_data = await update.message.reply_text(
                    text=admin_text,
                    reply_markup=await admin_keyboard()
                )

                context.user_data['admin_message_id'] = int(save_data.message_id)

                return SELECTING_ACTION

            else:
                no_rights = 'У тебя нет админских прав ¯\_(ツ)_/¯'
                await update.message.reply_text(
                    text=no_rights
                )

                return END

        except TypeError:
            await update.message.reply_text(
                text='Без понятия кто ты, пройди регистрацию, '
                     'введя команду /callsign'
            )

            return END

    except AttributeError:
        admin_text = 'Выбери один из пунктов меню.\n\n' \
                     'Для завершения работы с админ меню ' \
                     'введи команду /stop'

        save_data = await update.callback_query.edit_message_text(
            text=admin_text,
            reply_markup=await admin_keyboard()
        )

        context.user_data['admin_message_id'] = int(save_data.message_id)

        return SELECTING_ACTION


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
    text = re.sub(r'[^а-яА-Яa-zA-ZёЁ]', '', text)
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
            reply_markup=await admin_keyboard()
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
            reply_markup=await query_teams_keyboard(update, context)
        )

        return ENTER_EDITING_TEAM

    else:
        no_teams = 'Нет сторон, чтобы можно было что-то редактировать.'

        await update.callback_query.edit_message_text(
            text=no_teams,
            reply_markup=await query_teams_keyboard(update, context)
        )

        return END


async def commit_editing_team(update: Update,
                              context: CallbackContext.DEFAULT_TYPE) -> \
        ENTER_TEAM_NEW_DATA:
    await update.callback_query.answer()

    callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    context.user_data['callback_data'] = callback_data

    enter_new_titile = f'Вбей в текстовое поле новое название ' \
                       f'для стороны "{callback_data.capitalize()}".\n\n' \
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
    text = re.sub(r'[^а-яА-Яa-zA-ZёЁ]', '', text)
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
            reply_markup=await admin_keyboard()
        )

        context.user_data.clear()
        context.user_data['admin_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(SELECTING_ACTION)


async def deleting_team(update: Update,
                        context: CallbackContext.DEFAULT_TYPE):
    teams = await get_teams()

    if teams:
        edit_teams_text = 'Выбери сторону, которую необходимо удалить:\n\n' \
                          'Нажми на /stop, чтобы остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_teams_text,
            reply_markup=await query_teams_keyboard(update, context)
        )

        return ENTER_DELETING_TEAM

    else:
        no_teams = 'Нет добавленных сторон. Нечего удалять.'
        await update.callback_query.edit_message_text(
            text=no_teams,
            reply_markup=await back_to_menu()
        )

        return BACK_TO_MENU


async def commit_deleting_team(update: Update,
                               context: CallbackContext.DEFAULT_TYPE):
    await update.callback_query.answer()

    points = [point.get('point') for point in await get_points()]

    callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    for thread in threading.enumerate():
        if thread.__dict__.get('_name') in points:
            thread.cancel()

    await delete_team(callback_data)

    delete_success = f'{callback_data.capitalize()} - сторона удалена.\n' \
                     f'Все таймеры подрыва точек сброшены.\n\n' \
                     f'Предупредите участников этой стороны, что им требуется ' \
                     f'выбрать сторону заново. Ничего страшного не произойдет, ' \
                     f'если не предупредить, но вот будет неожиданость, когда ' \
                     f'бот при активации точки скажет игроку "ты не выбрал сторону!"'

    save_data = await update.callback_query.edit_message_text(
        text=delete_success,
        reply_markup=await admin_keyboard()
    )

    context.user_data['admin_message_id'] = int(save_data.message_id)

    return SELECTING_ACTION


async def adding_point(update: Update,
                       context: CallbackContext.DEFAULT_TYPE) -> \
        ENTER_POINT:
    await update.callback_query.answer()

    adding_point_message = 'Введи название новой точки. Например: Альфа\n\n' \
                           'Помни, название должно быть уникальным.\n' \
                           'Команда /stop остановит админ-меню и добавление точки.'

    await update.callback_query.edit_message_text(
        text=adding_point_message
    )

    return ENTER_POINT


async def commit_point_name(update: Update,
                            context: CallbackContext.DEFAULT_TYPE) -> \
        ENTER_POINT_COORDINATES:
    points = [point.get('point') for point in await get_points()]

    text = update.message.text
    text = re.sub(r'[^а-яА-Яa-zA-ZёЁ]', '', text)
    text = text.lower().replace('ё', 'е')

    if text in points:
        point_already_exist = 'Такая точка уже существует.\n' \
                              'Введи другое название.\n\n' \
                              'Команда /stop остановит админ-меню.'

        await update.message.reply_text(
            text=point_already_exist
        )

        raise ApplicationHandlerStop(ENTER_POINT)

    else:
        context.user_data['point_name'] = str(text)
        point_name_confirm = f'{text.capitalize()} - навзание принято.\n\n' \
                             f'Переходим к добавлению координат.\n' \
                             f'Введи координаты в чат через запятую, например:\n' \
                             f'12.345678, 87.654321\n\n' \
                             f'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", эта кнопка ' \
                             f'в данный момент времени перешлет боту координаты ' \
                             f'и запишет их в базу.\n\n' \
                             f'P.S. Помни, если вводишь данные вручную, то ' \
                             f'широта и долгота должны быть больше ' \
                             f'-90.000000 и меньше 90.000000.'

        await update.message.reply_text(
            text=point_name_confirm,
        )

        raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)


async def commit_point_coordinates(update: Update,
                                   context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:

    if update.message.location:

        await Location.get_or_create(
            point=context.user_data.get('point_name'),
            latitude=update.message.location.latitude,
            longitude=update.message.location.longitude
        )

        point_confirm = f'Точка создана.\n\n' \
                        f'Название: ' \
                        f'{context.user_data.get("point_name").capitalize()}\n' \
                        f'Широта: {update.message.location.latitude}\n' \
                        f'Долгота: {update.message.location.longitude}'

        save_data = await context.bot.send_message(
            text=point_confirm,
            chat_id=update.effective_chat.id,
            reply_markup=await admin_keyboard()
        )

        context.user_data['admin_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(SELECTING_ACTION)

    else:

        try:
            text = update.message.text
            coordinates = [
                float(coordinate) for coordinate in text.replace(
                    ' ', ''
                ).split(',')
            ]

            if len(coordinates) == 2 \
                    and -90 < coordinates[0] < 90 \
                    and -90 < coordinates[1] < 90:

                await Location.get_or_create(
                    point=context.user_data.get('point_name'),
                    latitude=coordinates[0],
                    longitude=coordinates[1]
                )

                point_name = context.user_data.get(
                    "point_name"
                ).capitalize()

                point_confirm = f'Точка создана.\n\n' \
                                f'Название: ' \
                                f'{point_name}\n' \
                                f'Широта: {coordinates[0]}\n' \
                                f'Долгота: {coordinates[1]}'

                save_data = await context.bot.send_message(
                    text=point_confirm,
                    chat_id=update.effective_chat.id,
                    reply_markup=await admin_keyboard()
                )

                context.user_data['admin_message_id'] = int(
                    save_data.message_id
                )

                raise ApplicationHandlerStop(SELECTING_ACTION)

            else:

                error_message = f'{text} не очень похоже на координаты.\n\n' \
                                f'Введи координаты в чат через запятую, например:\n' \
                                f'12.345678, 87.654321\n\n' \
                                f'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", эта кнопка ' \
                                f'в данный момент времени перешлет боту координаты ' \
                                f'и запишет их в базу.\n\n' \
                                f'P.S. Помни, если вводишь данные вручную, то ' \
                                f'широта и долгота должны быть больше ' \
                                f'-90.000000 и меньше 90.000000.'

                await update.message.reply_text(
                    text=error_message,
                )

                raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)

        except ValueError:

            error_message = f'Это не очень похоже на координаты.\n\n' \
                            f'Введи координаты в чат через запятую, например:\n' \
                            f'12.345678, 87.654321\n\n' \
                            f'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", эта кнопка ' \
                            f'в данный момент времени перешлет боту координаты ' \
                            f'и запишет их в базу.\n\n' \
                            f'P.S. Помни, если вводишь данные вручную, то ' \
                            f'широта и долгота должны быть больше ' \
                            f'-90.000000 и меньше 90.000000.'

            await update.message.reply_text(
                text=error_message,
            )

            raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)


async def deleting_point(update: Update,
                         context: CallbackContext.DEFAULT_TYPE):
    points = [point.get('point') for point in await get_points()]

    if points:
        edit_points_text = 'Выбери точку, которую необходимо удалить:\n\n' \
                           'Нажми на /stop, чтобы остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_points_text,
            reply_markup=await query_points_keyboard(update, context)
        )

        return ENTER_DELETING_POINT
    
    else:
        no_points = 'Нет добавленных точек. Нечего удалять.'
        await update.callback_query.edit_message_text(
            text=no_points,
            reply_markup=await back_to_menu()
        )

        return BACK_TO_MENU
    
    
async def commit_deleting_point(update: Update,
                                context: CallbackContext.DEFAULT_TYPE):
    await update.callback_query.answer()

    points = [point.get('point') for point in await get_points()]

    callback_data = re.sub(r'^POINT_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    for thread in threading.enumerate():
        if thread.__dict__.get('_name') in points:
            thread.cancel()

    await delete_point(callback_data)

    delete_success = f'{callback_data.capitalize()} - точка удалена.\n' \
                     f'Все таймеры подрыва точек сброшены.'

    save_data = await update.callback_query.edit_message_text(
        text=delete_success,
        reply_markup=await admin_keyboard()
    )

    context.user_data['admin_message_id'] = int(save_data.message_id)

    return SELECTING_ACTION


async def stop_admin_handler(update: Update,
                             context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    admin_stop_edit_message = 'Выполнение админских команд остановлено.'

    admin_stop_reply_text = 'Админ-меню было закрыто.\n' \
                            'Выполнение админских команд остановлено.\n' \
                            'Для повторного вызова введи команду:\n/admin.'

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

    points = [point.get('point') for point in await get_points()]

    for thread in threading.enumerate():
        if thread.__dict__.get('_name') in points:
            thread.cancel()

    await reset_all_points()

    text = 'Значения точек восстановлены по умолчанию.\n\n' \
           'Таймеры активации точек сброшены.\n' \
           'Все точки введены в игру.\n' \
           'Таймер установлен на 20 минут.\n' \
           'Точки не находятся под чьим-то контролем.'

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=await back_to_menu()
    )

    return BACK_TO_MENU
