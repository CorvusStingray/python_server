#!/usr/bin/env python

import sqlite3 as sql

def main() -> None:
    with sql.connect('./users.db') as db:
        db.cursor().execute("DROP TABLE IF EXISTS users").execute(
            f"""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(64),
                    username VARCHAR(64),
                    password VARCHAR(64),
                    privileges VARCHAR(64) DEFAULT 'user'
                )
            """
        ).execute(
            f"""
                INSERT INTO users (email, username, password, privileges)
                VALUES (\'admin@admin.admin\', \'admin\', \'letmein\', \'admin\')
            """
        )

if __name__ == '__main__':
    main()