import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nicegrass12!",   # ← change this to your MySQL password
        database="job_tracker"
    )


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Execute a SQL query.
      - fetchone=True  → return a single dict row
      - fetchall=True  → return a list of dict rows
      - commit=True    → INSERT/UPDATE/DELETE; returns lastrowid
    """
    connection = None
    cursor = None
    result = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if commit:
            connection.commit()
            result = cursor.lastrowid
        elif fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return result