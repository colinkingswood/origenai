# import psycopg2
# from django.conf import settings
# # Connect to your postgres DB
# db_name = settings.DATABASES['default'].get('NAME')
# user = settings.DATABASES['default'].get('USER')
# password = settings.DATABASES['default'].get('PASSWORD')
# host = settings.DATABASES['default'].get('HOST')
#
# connection_str = f"dbname={db_name} user={user} password={password} host={host}"
# print(connection_str)
# conn = psycopg2.connect(connection_str)
# conn.autocommit = True
#
# con = connections['default']
# con.ensure_connection()
# # Django is needs a fair few hacks to use the Psygcopy2 module outside of the ORM
# # Async problems if I don't take the connection from django, and now I need to do this to return dictionaries
# cursor= con.connection.cursor(cursor_factory=RealDictCursor)
#
# # cursor.execute("select * from Customer")
# # columns=cursor.fetchall()
# # columns=json.dumps(columns)



