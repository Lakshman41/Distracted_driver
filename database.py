import psycopg2
from dotenv import load_dotenv
import json
import os

load_dotenv()

class database:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                host=os.getenv("psql_host"),      # The host (use "localhost" for local connection)
                database=os.getenv("psql_database"),  # The database name
                user=os.getenv("psql_user"),      # The username
                password=os.getenv("psql_password"),  # The password for the user
                port=os.getenv("psql_port")       # Port
            )
        except Exception as error:
            print(f"Error in terminating session: {error}")
            return {'message': f'Error: {str(error)}'}
    
    def insert(self,username,email_id):
        try:
            # connection = psycopg2.connect(
            #     host=os.getenv("psql_host"),      # The host (use "localhost" for local connection)
            #     database=os.getenv("psql_database"),  # The database name
            #     user=os.getenv("psql_user"),      # The username
            #     password=os.getenv("psql_password"),  # The password for the user
            #     port=os.getenv("psql_port")       # Port
            # )
            cursor = self.connection.cursor()
            query="SELECT MAX(user_id) FROM users;"

            cursor.execute(query)
            count=cursor.fetchone()[0]
            if(count==None):
                count=0
            count=int(count)
            count+=1
            #print(username)
            #print(email_id)
            query = "INSERT INTO users (user_id, username, email_id) VALUES (%s, %s, %s);"
            cursor.execute(query, (str(count),str(username), str(email_id)))
            self.connection.commit()

            return count

            # Commit the transaction to save the changes
            #connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")

    def delete(self,username):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"DELETE FROM users WHERE username='{username}';"

            cursor.execute(query)

            # Commit the transaction to save the changes
            self.connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")

    def data_email_id(self,email_id):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"SELECT * FROM users WHERE email_id='{email_id}';"

            cursor.execute(query)
            records=cursor.fetchall()
            data=None
            flag=1
            for row in records:
                data={'message':'Data Found','id':int(row[2]),'username':row[0],'email_id':row[1]}
                flag=0

            self.connection.commit()
            # print(flag,data)
            if flag==1:
                data={'message':'Data not found'}
            return data
            # Commit the transaction to save the changes

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")
                return data
            
    def data_user_id(self,user_id):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"SELECT * FROM users WHERE user_id='{user_id}';"

            cursor.execute(query)
            records=cursor.fetchall()
            for row in records:
                data={'id':int(row[2]),'username':row[0],'email_id':row[1],'password':row[2]}

            # Commit the transaction to save the changes
            self.connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")
                return data
            
    def data_username(self,username):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"SELECT * FROM users WHERE username='{username}';"

            cursor.execute(query)
            records=cursor.fetchall()
            data=None
            flag=1
            for row in records:
                data={'message':'Data Found','id':int(row[2]),'username':row[0],'email_id':row[1]}
                flag=0

            # Commit the transaction to save the changes
            self.connection.commit()

            if flag==1:
                data={'message':'Data not found'}
            return data

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")
                return data
    def alter_username(self,email_id,new_username):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"UPDATE users SET username='{new_username}' WHERE email_id='{email_id}';"

            cursor.execute(query)

            # Commit the transaction to save the changes
            self.connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")

    def file_insert(self,user_id,file_type,file_name,file_path):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"SELECT COUNT(*) FROM files;"
            cursor.execute(query)
            count=cursor.fetchone()[0]
            if count!=0:
                query=f"SELECT file_id FROM files ORDER BY file_id DESC LIMIT 1;"
                cursor.execute(query)
                count=cursor.fetchone()[0]

            count=int(count)
            count+=1
            query = "INSERT INTO files (file_id, user_id, file_type, file_name, file_path) VALUES (%s, %s, %s, %s, %s);"
            cursor.execute(query, (str(count),str(user_id), str(file_type), str(file_name), str(file_path)))

            # Commit the transaction to save the changes
            self.connection.commit()
            return count

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")

    def result_insert(self,file_id,result_name,result_path,result,category):
            try:
                # connection = psycopg2.connect(
                #     host="localhost",      # The host (use "localhost" for local connection)
                #     database="dd",    # The database name
                #     user="postgres",      # The username
                #     password="123456",  # The password for the user
                #     port="5432"            # PostgreSQL runs on port 5432 by default
                # )
                cursor = self.connection.cursor()
                query=f"SELECT COUNT(*) FROM results;"
                cursor.execute(query)
                count=cursor.fetchone()[0]
                if count!=0:
                    query=f"SELECT result_id FROM results ORDER BY result_id DESC LIMIT 1;"
                    cursor.execute(query)
                    count=cursor.fetchone()[0]

                count=int(count)
                count+=1
                query = "INSERT INTO results (result_id, file_id, result_name, result_path, result,category) VALUES (%s, %s, %s, %s, %s, %s);"
                cursor.execute(query, (str(count),str(file_id), str(result_name), str(result_path), str(result), str(category)))

                # Commit the transaction to save the changes
                self.connection.commit()
                return count

            except (Exception, psycopg2.DatabaseError) as error:
                print(f"Error connecting to PostgreSQL: {error}")

            finally:
                if self.connection:
                    # Close the cursor and connection to the database
                    cursor.close()
                    self.connection.close()
                    print("PostgreSQL connection closed.")

    def result_get(self,file_id):
            try:
                # connection = psycopg2.connect(
                #     host="localhost",      # The host (use "localhost" for local connection)
                #     database="dd",    # The database name
                #     user="postgres",      # The username
                #     password="123456",  # The password for the user
                #     port="5432"            # PostgreSQL runs on port 5432 by default
                # )
                count=0
                cursor = self.connection.cursor()
                query = f"SELECT * FROM results WHERE file_id='{file_id}';"
                cursor.execute(query)

                results=cursor.fetchall()
                result_list=[]
                temp=None
                for row in results:
                    data={'name':row[2],'path':row[3],'result':row[4],'category':row[5]}
                    temp=data
                    if(row[4]=="Distracted"):
                        result_list.append(data)
                    #print(result_list[count])
                    count+=1
                #result_list.append[{"count":count}]
                # Commit the transaction to save the changes
                if count==1:
                    result_list.append(temp)
                print(result_list)
                self.connection.commit()
                return result_list

            except (Exception, psycopg2.DatabaseError) as error:
                print(f"Error connecting to PostgreSQL: {error}")

            finally:
                if self.connection:
                    # Close the cursor and connection to the database
                    cursor.close()
                    self.connection.close()
                    print("PostgreSQL connection closed.")

    def frame_insert(self,file_id,frame_name,frame_path):
        try:
            # connection = psycopg2.connect(
            #     host="localhost",      # The host (use "localhost" for local connection)
            #     database="dd",    # The database name
            #     user="postgres",      # The username
            #     password="123456",  # The password for the user
            #     port="5432"            # PostgreSQL runs on port 5432 by default
            # )
            cursor = self.connection.cursor()
            query=f"SELECT COUNT(*) FROM frames;"
            cursor.execute(query)
            count=cursor.fetchone()[0]
            if count!=0:
                query=f"SELECT frame_id FROM frames ORDER BY frame_id DESC LIMIT 1;"
                cursor.execute(query)
                count=cursor.fetchone()[0]

            count=int(count)
            count+=1
            query = "INSERT INTO frames (frame_id, file_id, frame_name, frame_path) VALUES (%s, %s, %s, %s);"
            cursor.execute(query, (str(count),str(file_id), str(frame_name), str(frame_path)))

            # Commit the transaction to save the changes
            self.connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error connecting to PostgreSQL: {error}")

        finally:
            if self.connection:
                # Close the cursor and connection to the database
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection closed.")
        
#obj = database()
#obj.insert('Lalo','lalo@fatass.com','123456')
#print(t_data['password'])