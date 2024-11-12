import psycopg2
from users import users

class Backup():
    def __init__(self):
        self.users_list=[]
        try:
            connection = psycopg2.connect(
                host="localhost",      # The host (use "localhost" for local connection)
                database="dd",    # The database name
                user="postgres",      # The username
                password="123456",  # The password for the user
                port="5432"            # PostgreSQL runs on port 5432 by default
            )
            
            cursor = connection.cursor()
            query="SELECT count(*) from users;"
            cursor.execute(query)
            records=cursor.fetchone()[0]

            if(records!=0):

                query="SELECT * from users;"

                cursor.execute(query)
                records=cursor.fetchall()
                for row in records:
                    obj=users(row[0],row[1],row[2])
                    (self.users_list).append(obj)

            # Commit the transaction to save the changes
            connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if connection:
                # Close the cursor and connection to the database
                cursor.close()
                connection.close()
                print("PostgreSQL connection closed.")
    
    def show(self):
        return self.users_list