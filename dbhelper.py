# Ensemble de fonctions pour gerer la BD de mes expenses.

import sqlite3


class DBHelper:
    def __init__(self, dbname='expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (amount float (2), date_expense date, reason text, status text, wbs text, receipt longblob)"
        self.conn.execute(stmt)
        self.conn.commit

    def add_item(self, data_tuple):
        stmt = "INSERT INTO items VALUES (?,?,?,?,?,?)"
        self.conn.execute(stmt, data_tuple)
        self.conn.commit()

    #def delete_item(self, item_text):
    #    stmt = "DELETE FROM items WHERE description = (?)"
    #    #args = (item_text, )
    #    self.conn.execute(stmt, item_text)
    #    self.conn.commit()

    #def get_items(self):
    #    stmt = "SELECT description FROM items"
    #    return [x[0] for x in self.conn.execute(stmt)]
