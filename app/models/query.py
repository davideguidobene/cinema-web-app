"""Contiene semplici query riutilizzabili."""

from sqlalchemy.sql import select

from app.models.db import connect_as, Role, get_table_names, get_table_dictionary


def select_all(table_name):
    """Seleziona tutte le tuple della tabella 'table_name'

    Args:
        table_name (str): nome della tabella

    Returns:
        result_set (RowProxy): iteratore sulle tuple selezionate
    """

    # verifica che sia una tabella valida
    if table_name not in get_table_names():
        raise ValueError(f'{table_name} is not a valid table name')

    table = get_table_dictionary()[table_name]

    # seleziona tutte le tuple della tabella dal database
    with connect_as(Role.WEBAPP) as conn:
        sel_stmt = select([table])
        result_set = conn.execute(sel_stmt)

    return result_set
