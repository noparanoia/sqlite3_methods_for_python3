# -*- coding: utf-8 -*-
import sqlite3


def base_connect():
    """
    Точка входа подключение к базе
    """
    connection = sqlite3.connect('database/db.sqlite3')
    return connection


def dict_maker(rows, response):
    tmp_list = []
    count = 0
    if response:
        for r in rows:
            tmp_list.append({r: response[count]})
            count += 1
        tmp_dict = {}
        for t in tmp_list:
            tmp_dict.update(t)
    else:
        tmp_dict = []
    return tmp_dict


def to_dict(rows, response, fetch):
    d = []
    if fetch != 'all':
        d.append(dict_maker(rows, response))
    else:
        for value in response:
            d.append(dict_maker(rows, value))
    return d


def sql_maker(rows='', table='', sql_query='', upd_arg='', argument=''):
    """
    Принимает ["список", ] rows (колонки), таблица, тип запроса
    ("insert", "select", "update", "delete"), аргументы ("arg = ?")
    запроса если есть возвращает строку с собранным запросом SQL
    """
    sql = ''
    str_rows = ''
    values = '?, '
    cval = 0
    for row in rows:
        str_rows = str_rows + row + ', '
        cval += 1
    values = values * cval
    str_rows = str_rows[:-2]
    values = values[:-2]
    if sql_query == 'insert':
        sql = 'INSERT INTO {table} ({str_rows}) VALUES ({values})'.format(
            table=table,
            str_rows=str_rows,
            values=values
        )
    if sql_query == 'select':
        if argument:
            sql = 'SELECT {str_rows} FROM {table} WHERE {argument}'.format(
                str_rows=str_rows,
                table=table,
                argument=argument
            )
        else:
            sql = 'SELECT {str_rows} FROM {table}'.format(
                str_rows=str_rows,
                table=table
            )
    if sql_query == 'update':
        sql = "UPDATE {table} SET {upd_arg} WHERE {argument}".format(
            table=table,
            upd_arg=upd_arg,
            argument=argument
        )
    if sql_query == 'delete':
        sql = 'DELETE FROM {table} WHERE {argument}'.format(
            table=table,
            argument=argument
        )
    return sql


def sql_insert(query_dict):
    """
    принимает словарь с обязательным значением 'table'
    далее в словаре необзодимо указать колонки с данными которые надо вставить
    пример:
    sql_insert({'table': 'table_name', 'id': 1, 'username': 'Username'})
    """
    table = query_dict.get('table')
    rows = []
    values = []
    for row in query_dict:
        if row != 'table':
            rows.append(row)
            values.append(query_dict.get(row))
    sql = sql_maker(rows=rows, table=table, sql_query='insert')
    connection = base_connect()
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql, (values))
        connection.commit()
    connection.close()


def sql_select(query_dict, fetch, argument='', arg_val='', str_argument=''):
    """
    Принимает словарь с обязательным значением 'table': 'table_name'
    далее идет обязательное значение 'rows' со списком из колонок
    таблицы которые надо получить 'rows': ['id', 'username']
    обязательный параметр fetch равный или 'all' или 'one'
    параметр argument принимает значение 'row_name'
    arg_val принимает значение выборки
    например argument='user_id', arg_val=1
    так же можно передать сложное условие выборки через параметр str_argument
    например str_argument='user_id = 1 AND username = "Username"'
    Этот метод возвращает список со словарем или слварями внутри
    которые имеют значения ключей переданные в словаре
    query_dict в списке по ключу 'rows'
    пример: sql_select(
        {'table': 'users', 'rows': ['user_id', 'username']},
        fetch='one',
        argument='user_id',
        arg_val=1)
    """
    table = query_dict.get('table')
    rows = query_dict.get('rows')
    if argument:
        if type(arg_val) is str:
            argument = argument + " = '" + arg_val + "'"
        else:
            argument = argument + ' = ' + str(arg_val)
        sql = sql_maker(
            rows=rows,
            table=table,
            sql_query='select',
            argument=argument)
    elif str_argument:
        sql = sql_maker(
            rows=rows,
            table=table,
            sql_query='select',
            argument=str_argument)
    else:
        sql = sql_maker(
            rows=rows,
            table=table,
            sql_query='select')
    connection = base_connect()
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        if fetch == 'all':
            response = cursor.fetchall()
        else:
            response = cursor.fetchone()
    connection.close()
    ret_list = to_dict(rows, response, fetch)
    return ret_list


def sql_update(query_dict, argument='', arg_val='', str_args=''):
    """
    Принимает словарь с обязательным ключом 'table': 'table_name',
    потом в словаре перечисляются колонки и значения для их обновления
    далее для WHERE argument='row_name', значение arg_val='row_value'
    так же можно передать для WHERE str_argument со сложным запросом
    sql_update(
        {'table': 'users', 'username': 'new_username'},
        argument='user_id', arg_val=1)
    """
    table = query_dict.get('table')
    upd_arg = ''
    for u in query_dict:
        if u != 'table':
            val = query_dict.get(u)
            if type(val) is str:
                upd_arg = upd_arg + u + " = '" + val + "', "
            else:
                upd_arg = upd_arg + u + " = " + str(val) + ", "
    upd_arg = upd_arg[:-2]
    if argument and arg_val:
        if arg_val is str:
            argument_upd = argument + " = '" + arg_val + "'"
        else:
            argument_upd = argument + " = " + str(arg_val)
        sql = sql_maker(
            table=table,
            sql_query='update',
            upd_arg=upd_arg,
            argument=argument_upd)
    elif str_args:
        sql = sql_maker(
            table=table,
            sql_query='update',
            upd_arg=upd_arg,
            argument=str_args
        )
    else:
        sql = ''
    connection = base_connect()
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    connection.close()


def sql_delete(table, argument='', arg_val='', str_argument=''):
    """
    принимает строковое имя таблицы, аргументы для
    WHERE argument='row_name', arg_val='row_value'
    и при необходимости можно передать сложный запрос для WHERE
    через str_argument
    пример: sql_delete('users', argument='user_id', arg_val=1)
    """
    if argument and arg_val:
        if arg_val is str:
            argument = argument + " = '" + arg_val + "'"
        else:
            argument = argument + " = " + str(arg_val)
        sql = sql_maker(table=table, sql_query='delete', argument=argument)
    elif str_argument:
        sql = sql_maker(table=table, sql_query='delete', argument=str_argument)
    else:
        sql = ''
    connection = base_connect()
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    connection.close()
