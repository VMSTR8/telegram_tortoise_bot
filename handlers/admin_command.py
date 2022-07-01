import re
import threading

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    ApplicationHandlerStop,
)
from tortoise.exceptions import ValidationError

from database.user.models import (
    User,
    Team,
    Location,
)

from database.db_functions import (
    reset_all_points,
    reset_all_users,
    get_teams,
    delete_team,
    get_points,
    delete_point,
    get_point_info,
)

from keyboards.keyboards import (
    BACK,
    END,
    STOPPING,
    query_teams_keyboard,
    query_points_keyboard,
    query_points_data_keyboard,
    admin_keyboard,
    back,
)

(
    SELECTING_ACTION,
    SELECTING_POINT,
    SELECTING_DATA_TO_CHANGE,
    ENTER_TEAM,
    ENTER_EDITING_TEAM,
    ENTER_TEAM_NEW_DATA,
    ENTER_DELETING_TEAM,
    ENTER_POINT,
    ENTER_POINT_COORDINATES,
    ENTER_DELETING_POINT,
    ENTER_EDITING_POINT_NAME,
    ENTER_EDITING_POINT_COORDINATE,
    ENTER_EDITING_POINT_TIME,
    ENTER_EDITING_POINT_RADIUS,
) = map(chr, range(14))


def moderate_users_text(text: str) -> str:
    """
    Edits a text string, replacing all the letters "ё" with "e",
    removing all line breaks and all tabs. The regular expression
    skips only Cyrillic letters, the "-" symbol, as well as single spaces.

    :param text: String that contains text
    :return: String with edited text
    """

    text = ' '.join(
        text.lower().replace(
            'ё', 'е'
        ).replace(
            '\n', ''
        ).replace(
            '\t', ''
        ).split()
    )
    text = re.sub(r'[^а-яА-Яa-zA-Z-\s]', '', text)

    return text


async def point_message(point_name: str) -> str:
    """
    Sends a message with information about the point.

    :param point_name: Name of the existing team.
    :return: String with information about the point.
    """
    data = await get_point_info(point_name)

    if data['in_game']:
        point_status = 'В игре'
    else:
        point_status = 'Выведина из игры'

    point_data_message = f'Выбери, какие данные точки нужно ' \
                         f'отредактировать:\n\n' \
                         f'Название: {data["point"].capitalize()}\n' \
                         f'Статус точки: {point_status}\n' \
                         f'Широта: {data["latitude"]}\n' \
                         f'Долгота: {data["longitude"]}\n' \
                         f'Время подрыва: {int(data["time"]) // 60} мин.\n' \
                         f'Радиус активации (в метрах): {data["radius"]}\n\n' \
                         f'Нажми на /stop, чтобы остановить выполнение ' \
                         f'админских команд.'

    return point_data_message


async def admin(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_ACTION:
    """
    Sends the keyboard with the admin menu
    to the chat with the user, if the user has admin rights.
    """

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

                context.user_data['admin_message_id'] = int(
                    save_data.message_id
                )

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


async def adding_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_TEAM:
    """
    Initiates the addition of the game side.
    """

    text = 'Введи название стороны. Например: желтые.\n\n' \
           'Помни, что название должно быть уникальным.\n' \
           'Команда /stop отменит создание сотороны.'

    await update.callback_query.answer()

    await update.callback_query.edit_message_text(
        text=text
    )

    return ENTER_TEAM


async def commit_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_ACTION:
    """
    If the name of the game side passes validation,
    then the name is recorded in the database.
    """

    teams = await get_teams()

    team_name = moderate_users_text(text=update.message.text)

    try:
        if team_name in teams:

            team_already_exists = 'Такая сторона уже существует.\n' \
                                  'Введи другое название.\n\n' \
                                  'Команда /stop остановит админ-меню.'

            await update.message.reply_text(text=team_already_exists)

            raise ApplicationHandlerStop(ENTER_TEAM)

        else:

            team_created = f'{team_name.capitalize()}, ' \
                           f'принято и записано в базу данных.\n\n' \
                           f'Нажми на /stop, чтобы остановить ' \
                           f'выполнение админских команд.'

            await Team.get_or_create(title=team_name)
            save_data = await context.bot.send_message(
                text=team_created,
                chat_id=update.effective_chat.id,
                reply_markup=await admin_keyboard()
            )

            context.user_data['admin_message_id'] = int(save_data.message_id)

            raise ApplicationHandlerStop(SELECTING_ACTION)

    except ValidationError:

        empty_text = 'Либо ты ввел недопустимые символы ' \
                     'в названии стороны, либо ' \
                     'превысил допустимую длину названия ' \
                     '(25 символов).\n\n' \
                     'Введи другое название для стороны.\n\n' \
                     'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=empty_text)

        raise ApplicationHandlerStop(ENTER_TEAM)


async def editing_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_EDITING_TEAM:
    """
    Sends a keyboard with game
    sides that the user can change.
    """

    teams = await get_teams()

    if teams:
        edit_team_text = 'Выбери сторону, название которой ' \
                         'хочешь изменить:\n\n' \
                         'Нажми на /stop, чтобы остановить ' \
                         'выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_team_text,
            reply_markup=await query_teams_keyboard(update, context)
        )

        return ENTER_EDITING_TEAM

    else:
        no_teams = 'Нет сторон, чтобы можно было что-то редактировать.'

        await update.callback_query.edit_message_text(
            text=no_teams,
            reply_markup=await back()
        )

        return BACK


async def commit_editing_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_TEAM_NEW_DATA:
    """
    Initializes the name change for the game side.
    """

    await update.callback_query.answer()

    callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    context.user_data['callback_data'] = callback_data

    enter_new_titile = f'Вбей в текстовое поле новое название ' \
                       f'для стороны "{callback_data.capitalize()}".\n\n' \
                       f'Команда /stop остановит обновление ' \
                       f'названия стороны и остановит выполнение ' \
                       f'адимнских команд.'

    await update.callback_query.edit_message_text(
        text=enter_new_titile
    )

    return ENTER_TEAM_NEW_DATA


async def commit_update_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> END:
    """
    If the new name of the game side passes validation,
    the name will be recorded in the database.
    """

    saved_data = context.user_data['callback_data']

    teams = await get_teams()

    new_team_name = moderate_users_text(text=update.message.text)

    try:
        if new_team_name in teams:
            team_already_exists = 'Такая сторона уже существует.\n' \
                                  'Введи другое название.\n\n' \
                                  'Команда /stop остановит админ-меню.'

            await update.message.reply_text(text=team_already_exists)

            raise ApplicationHandlerStop(ENTER_TEAM_NEW_DATA)

        else:
            await Team.filter(title=saved_data).update(title=new_team_name)

            update_success = f'{saved_data.capitalize()} - название ' \
                             f'изменено на ' \
                             f'{new_team_name.capitalize()}.\n\n' \
                             f'Нажми на /stop, чтобы остановить ' \
                             f'выполнение админских команд.'

            save_data = await context.bot.send_message(
                text=update_success,
                chat_id=update.effective_chat.id,
                reply_markup=await admin_keyboard()
            )

            context.user_data['admin_message_id'] = int(save_data.message_id)

            raise ApplicationHandlerStop(END)

    except ValidationError:

        empty_text = 'Либо ты ввел недопустимые символы ' \
                     'в названии стороны, либо ' \
                     'превысил допустимую длину названия ' \
                     '(25 символов).\n\n' \
                     'Введи другое название для стороны.\n\n' \
                     'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=empty_text)

        raise ApplicationHandlerStop(ENTER_TEAM_NEW_DATA)


async def deleting_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> BACK:
    """
    Sends a keyboard to a chat with the user
    with a list of sides that the admin can delete.
    """

    teams = await get_teams()

    if teams:
        edit_teams_text = 'Выбери сторону, которую ' \
                          'необходимо удалить:\n\n' \
                          'Нажми на /stop, чтобы ' \
                          'остановить выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_teams_text,
            reply_markup=await query_teams_keyboard(update, context)
        )

        return ENTER_DELETING_TEAM

    else:
        no_teams = 'Нет добавленных сторон. Нечего удалять.'
        await update.callback_query.edit_message_text(
            text=no_teams,
            reply_markup=await back()
        )

        return BACK


async def commit_deleting_team(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> END:
    """
    Deletes the command from the database.
    """

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
                     f'Предупредите участников этой стороны, ' \
                     f'что им требуется ' \
                     f'выбрать сторону заново. Ничего страшного ' \
                     f'не произойдет, ' \
                     f'если не предупредить, но вот будет ' \
                     f'неожиданость, когда ' \
                     f'бот при активации точки скажет игроку ' \
                     f'"ты не выбрал ' \
                     f'сторону!"\n\n' \
                     f'Нажми на /stop, чтобы остановить ' \
                     f'выполнение админских команд.'

    save_data = await update.callback_query.edit_message_text(
        text=delete_success,
        reply_markup=await admin_keyboard()
    )

    context.user_data['admin_message_id'] = int(save_data.message_id)

    return END


async def adding_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_POINT:
    """
    Initiates adding a point to the database.
    """

    await update.callback_query.answer()

    adding_point_message = 'Введи название новой точки. Например: Альфа\n\n' \
                           'Помни, название должно быть уникальным.\n' \
                           'Команда /stop остановит админ-меню и ' \
                           'добавление точки.'

    await update.callback_query.edit_message_text(
        text=adding_point_message
    )

    return ENTER_POINT


async def commit_point_name(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_POINT_COORDINATES:
    """
    If the point name passes validation,
    the bot proceeds to the next iteration of the dialog.
    """
    points = [point.get('point') for point in await get_points()]

    point_name = moderate_users_text(text=update.message.text)

    if point_name.replace(' ', '') != '' and len(point_name) <= 25:
        if point_name in points:
            point_already_exist = 'Такая точка уже существует.\n' \
                                  'Введи другое название.\n\n' \
                                  'Команда /stop остановит админ-меню и ' \
                                  'добавление точки.'

            await update.message.reply_text(
                text=point_already_exist
            )

            raise ApplicationHandlerStop(ENTER_POINT)

        else:
            context.user_data['point_name'] = str(point_name)
            point_name_confirm = f'{point_name.capitalize()} - ' \
                                 f'название принято.\n\n' \
                                 f'Переходим к добавлению координат.\n' \
                                 f'Введи координаты в чат через ' \
                                 f'запятую, например:\n' \
                                 f'12.345678, 87.654321\n\n' \
                                 f'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", ' \
                                 f'эта кнопка ' \
                                 f'в данный момент времени перешлет ' \
                                 f'боту координаты ' \
                                 f'и запишет их в базу.\n\n' \
                                 f'P.S. Помни, если вводишь данные ' \
                                 f'вручную, то ' \
                                 f'широта и долгота должны быть меньше ' \
                                 f'-90.000000 и больше 90.000000.\n\n' \
                                 f'Команда /stop остановит ' \
                                 f'добавление точки и админ-меню.'

            await update.message.reply_text(
                text=point_name_confirm,
            )

            raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)
    else:

        empty_text = 'Либо ты ввел недопустимые символы ' \
                     'в названии точки, либо ' \
                     'превысил допустимую длину названия ' \
                     '(25 символов).\n\n' \
                     'Введи другое название для точки.\n\n' \
                     'Команда /stop остановит админ-меню.'

        await update.message.reply_text(
            text=empty_text
        )

        raise ApplicationHandlerStop(ENTER_POINT)


async def commit_point_coordinates(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_ACTION:
    """
    Accepts coordinates from the user and writes
    the point to the database. Handles both manual
    input of coordinates and a message with
    coordinates that can be sent via Telegram.
    """

    if update.message.location:

        await Location.get_or_create(
            point=context.user_data.get('point_name'),
            latitude=update.message.location.latitude,
            longitude=update.message.location.longitude
        )
        point_name = context.user_data.get("point_name").capitalize()
        point_confirm = f'Точка создана.\n\n' \
                        f'Название: ' \
                        f'{point_name}\n' \
                        f'Широта: {update.message.location.latitude}\n' \
                        f'Долгота: {update.message.location.longitude}\n\n' \
                        f'Нажми на /stop, чтобы остановить выполнение ' \
                        f'админских команд.'

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
            try:
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

            except ValidationError:

                error_message = 'Переданные данные не являются ' \
                                'координатами.\n\n' \
                                'Введи координаты в чат ' \
                                'через запятую, например:\n' \
                                '12.345678, 87.654321\n\n' \
                                'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", ' \
                                'эта кнопка ' \
                                'в данный момент времени ' \
                                'перешлет боту координаты ' \
                                'и запишет их в базу.\n\n' \
                                'P.S. Помни, если вводишь данные ' \
                                'вручную, то ' \
                                'широта и долгота должны быть меньше ' \
                                '-90.000000 и больше 90.000000.\n\n' \
                                'Команда /stop остановит добавление ' \
                                'точки и админ-меню.'

                await update.message.reply_text(
                    text=error_message,
                )

                raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)

        except ValueError:

            error_message = 'Это похоже на координаты? Прочитай внимательно ' \
                            'инструкцию ниже и попробуй еще раз.\n\n' \
                            'Введи координаты в чат через запятую, ' \
                            'например:\n' \
                            '12.345678, 87.654321\n\n' \
                            'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", эта кнопка ' \
                            'в данный момент времени перешлет ' \
                            'боту координаты ' \
                            'и запишет их в базу.\n\n' \
                            'P.S. Помни, если вводишь данные вручную, то ' \
                            'широта и долгота должны быть меньше ' \
                            '-90.000000 и больше 90.000000.\n\n' \
                            'Команда /stop остановит добавление точки ' \
                            'и админ-меню.'

            await update.message.reply_text(
                text=error_message,
            )

            raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)

        except IndexError:

            error_message = 'Ты вводишь одну координату, а нужно две!\n\n' \
                            'Введи координаты в чат через запятую, ' \
                            'например:\n' \
                            '12.345678, 87.654321\n\n' \
                            'Или нажми "АКТИВИРОВАТЬ ТОЧКУ", эта кнопка ' \
                            'в данный момент времени перешлет ' \
                            'боту координаты ' \
                            'и запишет их в базу.\n\n' \
                            'P.S. Помни, если вводишь данные вручную, то ' \
                            'широта и долгота должны быть меньше ' \
                            '-90.000000 и больше 90.000000.\n\n' \
                            'Команда /stop остановит добавление точки ' \
                            'и админ-меню.'

            await update.message.reply_text(
                text=error_message,
            )

            raise ApplicationHandlerStop(ENTER_POINT_COORDINATES)


async def editing_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_POINT:
    """
    Sends a keyboard with a list of points that the admin can change.
    """

    await update.callback_query.answer()

    points = [point.get('point') for point in await get_points()]

    if points:
        editing_point_message = 'Выбери точку, которую хочешь ' \
                                'отредактировать:\n\n' \
                                'Нажми на /stop, чтобы ' \
                                'остановить выполнение ' \
                                'админских команд.'

        await update.callback_query.edit_message_text(
            text=editing_point_message,
            reply_markup=await query_points_keyboard(update, context)
        )

        return SELECTING_POINT

    else:
        no_points = 'Нет добавленных точек. Нечего редактировать.'
        await update.callback_query.edit_message_text(
            text=no_points,
            reply_markup=await back()
        )

        return BACK


async def entering_editing_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_DATA_TO_CHANGE:
    """
    Sends data to the point selected by the admin.
    It also sends a keyboard with buttons to change the point data.
    """

    await update.callback_query.answer()

    callback_data = re.sub(r'^POINT_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    point_data = await point_message(callback_data)

    context.user_data['callback_data'] = callback_data

    await update.callback_query.edit_message_text(
        text=point_data,
        reply_markup=await query_points_data_keyboard()
    )

    return SELECTING_DATA_TO_CHANGE


async def editing_point_name(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_EDITING_POINT_NAME:
    """
    Initiates a change in the name of the game point.
    """

    await update.callback_query.answer()

    point_name = context.user_data.get("callback_data")

    enter_new_point_name = f'Вбей в текстовое поле новое название ' \
                           f'для точки "{point_name.capitalize()}".\n\n' \
                           f'Команда /stop остановит обновление ' \
                           f'названия стороны и остановит выполнение ' \
                           f'адимнских команд.'

    await update.callback_query.edit_message_text(
        text=enter_new_point_name
    )
    return ENTER_EDITING_POINT_NAME


async def commit_new_point_name(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_DATA_TO_CHANGE:
    """
    If the new point name passes validation,
    then the new name is written to the database.
    """

    points = [point.get('point') for point in await get_points()]

    point_name = context.user_data.get("callback_data")
    new_point_name = moderate_users_text(text=update.message.text)

    try:
        if new_point_name in points:
            point_already_exists = 'Такая точка уже существует.\n' \
                                   'Введи другое название.' \
                                   'Команда /stop остановит админ-меню.'

            await update.message.reply_text(text=point_already_exists)

            raise ApplicationHandlerStop(ENTER_EDITING_POINT_NAME)

        else:
            await Location.filter(
                point=point_name
            ).update(
                point=new_point_name
            )

            point_data = await point_message(new_point_name)

            update_success = f'{point_name.capitalize()} - название ' \
                             f'изменено на ' \
                             f'{new_point_name.capitalize()}.\n' \
                             f'{point_data}'

            save_data = await context.bot.send_message(
                text=update_success,
                chat_id=update.effective_chat.id,
                reply_markup=await query_points_data_keyboard()
            )

            context.user_data['callback_data'] = str(new_point_name)
            context.user_data['admin_message_id'] = int(save_data.message_id)

            raise ApplicationHandlerStop(SELECTING_DATA_TO_CHANGE)

    except ValidationError:

        empty_text = 'Либо ты ввел недопустимые символы ' \
                     'в названии точки, либо ' \
                     'превысил допустимую длину названия ' \
                     '(25 символов).\n\n' \
                     'Введи другое название для точки.\n\n' \
                     'Команда /stop остановит админ-меню.'

        await update.message.reply_text(text=empty_text)

        raise ApplicationHandlerStop(ENTER_EDITING_POINT_NAME)


async def editing_in_game_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_DATA_TO_CHANGE:
    """
    Changes the status of a point to
    "In game" or "Out of game".
    """

    await update.callback_query.answer()

    point_name = context.user_data.get("callback_data")
    point = await get_point_info(point_name)

    if point['in_game']:
        await Location.filter(point=point_name).update(in_game=False)
        point_status = 'Выведина из игры'
    else:
        await Location.filter(point=point_name).update(in_game=True)
        point_status = 'В игре'

    point_data = await point_message(point_name)

    point_data_message = f'Новый статус точки: {point_status.upper()}.\n' \
                         f'{point_data}'

    await update.callback_query.edit_message_text(
        text=point_data_message,
        reply_markup=await query_points_data_keyboard()
    )

    return SELECTING_DATA_TO_CHANGE


async def editing_point_latitude(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_EDITING_POINT_COORDINATE:
    """
    Initiates the latitude update.
    """

    await update.callback_query.answer()

    point_name = context.user_data.get("callback_data")

    enter_new_point_latitude = f'Введи новую широту для точки ' \
                               f'{point_name.capitalize()}.\n\n' \
                               f'Например:\n' \
                               f'12.345678\n\n' \
                               f'Помни, что широта не должна быть ' \
                               f'меньше -90.000000 и больше 90.000000.\n\n' \
                               f'Команда /stop остановит добавление ' \
                               f'точки и админ-меню.'

    await update.callback_query.edit_message_text(
        text=enter_new_point_latitude,
    )

    context.user_data['coordinate_type'] = 'latitude'

    return ENTER_EDITING_POINT_COORDINATE


async def editing_point_longitude(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_EDITING_POINT_COORDINATE:
    """
    Initiates the longitude update.
    """

    await update.callback_query.answer()

    point_name = context.user_data.get("callback_data")

    enter_new_point_longitude = f'Введи новую долготу для точки ' \
                                f'{point_name.capitalize()}.\n\n' \
                                f'Например:\n' \
                                f'12.345678\n\n' \
                                f'Помни, что долгота не должна быть ' \
                                f'меньше -90.000000 и больше 90.000000.\n\n' \
                                f'Команда /stop остановит добавление ' \
                                f'точки и админ-меню.'

    await update.callback_query.edit_message_text(
        text=enter_new_point_longitude,
    )

    context.user_data['coordinate_type'] = 'longitude'

    return ENTER_EDITING_POINT_COORDINATE


async def commit_new_point_coordinate(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_DATA_TO_CHANGE:
    """
    If the coordinates are validated, then
    the latitude or longitude is updated for the point.
    """

    point_name = context.user_data.get("callback_data")
    coordinate_type = context.user_data.get('coordinate_type')
    try:
        text = update.message.text
        text = float(text)

        try:
            if coordinate_type == 'latitude':
                await Location.filter(
                    point=point_name
                ).update(latitude=text)

                point_data = await point_message(point_name=point_name)

                new_longitude_confirm = f'Широта была обновлена.\n' \
                                        f'{point_data}'

                save_data = await context.bot.send_message(
                    text=new_longitude_confirm,
                    chat_id=update.effective_chat.id,
                    reply_markup=await query_points_data_keyboard()
                )

            else:
                await Location.filter(
                    point=point_name
                ).update(longitude=text)

                point_data = await point_message(point_name=point_name)

                new_longitude_confirm = f'Долгота была обновлена.\n' \
                                        f'{point_data}'

                save_data = await context.bot.send_message(
                    text=new_longitude_confirm,
                    chat_id=update.effective_chat.id,
                    reply_markup=await query_points_data_keyboard()
                )

            context.user_data['admin_message_id'] = int(
                save_data.message_id
            )

            raise ApplicationHandlerStop(SELECTING_DATA_TO_CHANGE)

        except ValidationError:

            error_message = 'Переданные данные не являются координатой.\n\n' \
                            'Еще раз повторяю, что координата может быть ' \
                            'не меньше -90.000000 и не больше 90,000000.' \
                            'Команда /stop остановит добавление ' \
                            'точки и админ-меню.'

            await update.message.reply_text(
                text=error_message,
            )

            raise ApplicationHandlerStop(ENTER_EDITING_POINT_COORDINATE)

    except ValueError:

        error_message = f'Это не похоже на координату от слова совсем. ' \
                        f'Прочитай внимательно инструкцию и ' \
                        f'попробуй еще раз.\n\n' \
                        f'Введи новую координату для точки ' \
                        f'{point_name.capitalize()}.\n\n' \
                        f'Помни, что широта не должна быть ' \
                        f'меньше -90.000000 и больше 90.000000.\n\n' \
                        f'Команда /stop остановит добавление ' \
                        f'точки и админ-меню.'

        await update.message.reply_text(
            text=error_message,
        )

        raise ApplicationHandlerStop(ENTER_EDITING_POINT_COORDINATE)


async def editing_point_time(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_EDITING_POINT_TIME:
    """
    Initiates the point time update.
    """

    await update.callback_query.answer()

    point_name = context.user_data.get("callback_data")

    enter_new_time = f'Вбей в текстовое поле новое время подрыва ' \
                     f'для точки "{point_name.capitalize()}" в минутах.\n' \
                     f'Учти, нельзя устанавливать таймер меньше ' \
                     f'1 минуты и больше 10080 минут.\n\n' \
                     f'Нажми на /stop, чтобы остановить выполнение ' \
                     f'админских команд.'

    await update.callback_query.edit_message_text(
        text=enter_new_time
    )

    return ENTER_EDITING_POINT_TIME


async def commit_new_point_time(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_DATA_TO_CHANGE:
    """
    If the new time passes validation, then
    the time is updated for the point in the database.
    """

    time = update.message.text
    point_name = context.user_data.get("callback_data")

    try:
        new_point_time = float(time) * 60

        await Location.filter(point=point_name).update(time=new_point_time)

        point_data = await point_message(point_name=point_name)

        new_time_confirm = f'Время для точки {point_name.capitalize()} ' \
                           f'обновлено, установлено ' \
                           f'{int(new_point_time) // 60} мин.\n' \
                           f'{point_data}'

        save_data = await context.bot.send_message(
            text=new_time_confirm,
            chat_id=update.effective_chat.id,
            reply_markup=await query_points_data_keyboard()
        )

        context.user_data['admin_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(SELECTING_DATA_TO_CHANGE)

    except ValueError:
        error_message = 'Было отправлено не целое число. ' \
                        'Я же минуты обновляю для точки, а ' \
                        'ты присылаешь мне непонятно что.\n\n' \
                        'Попробуй еще раз.\n' \
                        'Нажми на /stop, чтобы остановить выполнение ' \
                        'админских команд.'

        await update.message.reply_text(
            text=error_message,
        )

        raise ApplicationHandlerStop(ENTER_EDITING_POINT_TIME)

    except ValidationError:
        error_message = 'Время для точки не может быть меньше 1 минуты ' \
                        'и больше 10080 минут.' \
                        'Попробуй еще раз.\n' \
                        'Нажми на /stop, чтобы остановить выполнение ' \
                        'админских команд.'

        await update.message.reply_text(
            text=error_message,
        )

        raise ApplicationHandlerStop(ENTER_EDITING_POINT_TIME)


async def editing_point_radius(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_EDITING_POINT_RADIUS:
    """
    Initiates updating the point radius.
    """

    await update.callback_query.answer()

    point_name = context.user_data.get("callback_data")

    enter_new_radius = f'Вбей в текстовое поле новый радиус ' \
                       f'для точки "{point_name.capitalize()}" в метрах.\n' \
                       f'Учти, нельзя устанавливать радиус меньше ' \
                       f'1 метра и больше 1000 метров.\n\n' \
                       f'Нажми на /stop, чтобы остановить выполнение ' \
                       f'админских команд.'

    await update.callback_query.edit_message_text(
        text=enter_new_radius
    )

    return ENTER_EDITING_POINT_RADIUS


async def commit_new_point_radius(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_DATA_TO_CHANGE:
    """
    If the new radius passes validation, then
    the radius is updated for the point in the database.
    """

    radius = update.message.text
    point_name = context.user_data.get("callback_data")

    try:
        new_radius = int(radius)

        await Location.filter(point=point_name).update(radius=new_radius)

        point_data = await point_message(point_name=point_name)

        new_time_confirm = f'Радиус для точки {point_name.capitalize()} ' \
                           f'обновлен, установлено расстояние:\n' \
                           f'{int(new_radius)} м.\n' \
                           f'{point_data}'

        save_data = await context.bot.send_message(
            text=new_time_confirm,
            chat_id=update.effective_chat.id,
            reply_markup=await query_points_data_keyboard()
        )

        context.user_data['admin_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(SELECTING_DATA_TO_CHANGE)

    except ValueError:
        error_message = 'Было отправлено не целое число. ' \
                        'Я же метры обновляю для точки, а ' \
                        'ты присылаешь мне непонятно что, ' \
                        'просто пришли цифру, и все.\n\n' \
                        'Попробуй еще раз.\n' \
                        'Нажми на /stop, чтобы остановить выполнение ' \
                        'админских команд.'

        await update.message.reply_text(
            text=error_message,
        )

        raise ApplicationHandlerStop(ENTER_EDITING_POINT_RADIUS)

    except ValidationError:
        error_message = 'Радиус не может быть меньше 1 метра и ' \
                        'больше 1000 метров.' \
                        'Попробуй еще раз.\n' \
                        'Нажми на /stop, чтобы остановить выполнение ' \
                        'админских команд.'

        await update.message.reply_text(
            text=error_message,
        )

        raise ApplicationHandlerStop(ENTER_EDITING_POINT_RADIUS)


async def deleting_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> ENTER_DELETING_POINT:
    """
    Initiates deleting a point from the database.
    """

    await update.callback_query.answer()

    points = [point.get('point') for point in await get_points()]

    if points:
        edit_points_text = 'Выбери точку, которую необходимо удалить:\n\n' \
                           'Нажми на /stop, чтобы остановить ' \
                           'выполнение админских команд.'

        await update.callback_query.edit_message_text(
            text=edit_points_text,
            reply_markup=await query_points_keyboard(update, context)
        )

        return ENTER_DELETING_POINT

    else:
        no_points = 'Нет добавленных точек. Нечего удалять.'
        await update.callback_query.edit_message_text(
            text=no_points,
            reply_markup=await back()
        )

        return BACK


async def commit_deleting_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> SELECTING_ACTION:
    """
    Deletes the selected point from the database.
    """

    await update.callback_query.answer()

    points = [point.get('point') for point in await get_points()]

    callback_data = re.sub(r'^POINT_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    for thread in threading.enumerate():
        if thread.__dict__.get('_name') in points:
            thread.cancel()

    await delete_point(callback_data)

    delete_success = f'{callback_data.capitalize()} - точка удалена.\n' \
                     f'Все таймеры подрыва точек сброшены.\n\n' \
                     f'Нажми на /stop, чтобы остановить ' \
                     f'выполнение админских команд.'

    save_data = await update.callback_query.edit_message_text(
        text=delete_success,
        reply_markup=await admin_keyboard()
    )

    context.user_data['admin_message_id'] = int(save_data.message_id)

    return END


async def close_and_stop(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> None:
    """
    Stops the execution of admin commands,
    deletes the admin keyboard and informs the user about it.
    """

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


async def stop_admin_handler(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> END:
    """
    Stops the execution of admin commands,
    deletes the admin keyboard and informs the user about it.
    """

    try:
        await close_and_stop(update, context)
        return END

    except BadRequest:

        return END


async def stop_nested_admin_handler(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> END:
    """
    Stops the execution of admin commands,
    deletes the admin keyboard and informs the user about it.
    """

    try:
        await close_and_stop(update, context)
        return STOPPING

    except BadRequest:

        return STOPPING


async def end_editing_point(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> END:
    """
    Exits point editing and returns to the previous menu.
    """

    await editing_point(update, context)

    return END


async def end_second_level_conv(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> END:
    """
    Exits the second level of the dialog and returns
    the user to the initial admin menu.
    """

    await admin(update, context)

    return END


async def restart_points(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> BACK:
    """
    Stops the timer for all points,
    resets control over points,
    removes players from the game and restores
    the standard activation timer of all points.
    """

    await update.callback_query.answer()

    points = [point.get('point') for point in await get_points()]

    for thread in threading.enumerate():
        if thread.__dict__.get('_name') in points:
            thread.cancel()

    await reset_all_points()
    await reset_all_users()

    text = 'Значения точек восстановлены по умолчанию.\n\n' \
           'Таймеры активации точек сброшены.\n\n' \
           'Все точки введены в игру.\n\n' \
           'Таймер на точках установлен на 20 минут.\n\n' \
           'Точки не находятся под чьим-то контролем.\n\n' \
           'Всем пользователям удалена сторона (нужно выбрать ' \
           'сторону заново), а так же сброшен статус In Game.'

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=await back()
    )

    return BACK
