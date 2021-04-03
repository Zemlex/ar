import sqlite3
from sqlite3 import Error

DB_FILE = "AgesAndResources.db"

def create_connection():
    # create a db connection to the SQLite db
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
  # create a table from the create_table_sql statement
  try:
    c = conn.cursor()
    c.execute(create_table_sql)
  except Error as e:
    print(e)

def main():
  sql_create_highscores_table = """ CREATE TABLE IF NOT EXISTS highscores (
                                      id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                      score INTEGER NOT NULL,
                                      age TEXT NOT NULL
                                    );"""

  # create db connection
  conn = create_connection()
  # create the tables if the connection was made
  if conn is not None:
    create_table(conn, sql_create_highscores_table)
  else:
    print("Cannot create the database connection.")

# INSERT FUNCTIONS
####################################################
def create_highscore(highscore_data):
  # highscore_data: (score, age)
  conn = create_connection()
  sql = """ INSERT INTO highscores(score, age) 
            VALUES(?,?) """
  cur = conn.cursor()
  cur.execute(sql, highscore_data)
  conn.commit()
  return


# MODIFY FUNCTIONS
#####################################################
def modify_highscore(updated_highscore_data):
  # updated_highscore_data: (new score, new age)
  conn = create_connection()
  sql = """ UPDATE highscores
            SET score = ?
                age = ?
            WHERE score = ? """
  cur = conn.cursor()
  cur.execute(sql, updated_highscore_data)
  conn.commit()
  return


# DELETE FUNCTIONS
#####################################################
def delete_highscore(score):
  conn = create_connection()
  sql = """ DELETE FROM highscores
            WHERE score = ? """
  cur = conn.cursor()
  cur.execute(sql, (score,))
  conn.commit()
  return


# QUERY FUNCTIONS
#####################################################
def get_highscores():
  conn = create_connection()
  cur = conn.cursor()
  sql = """ SELECT score, age
            FROM highscores """
  cur.execute(sql)
  rows = cur.fetchall() # rows[i] = (score, age)
  return rows

def get_lowest_highscore():
  conn = create_connection()
  cur = conn.cursor()
  sql = """ SELECT MIN(score)
            FROM highscores """
  cur.execute(sql)
  val = cur.fetchall() # val = score
  return val[0][0]

def get_num_highscores():
  return len(get_highscores())


# INITIALIZE THE DATABASE 
#####################################################
main()