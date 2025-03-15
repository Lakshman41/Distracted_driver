import secrets
import string
import uuid
import time
import hashlib
import base64
import psycopg2
from datetime import datetime, date, timedelta
import threading
from dotenv import load_dotenv
import os

load_dotenv()

class TokenService:
    def __init__(self):
        self.salt = secrets.token_hex(16)
        self.token = None
        self.cred = {
            "host": os.getenv("psql_host"),      # The host (use "localhost" for local connection)
            "database": os.getenv("psql_database"),  # The database name
            "user": os.getenv("psql_user"),      # The username
            "password": os.getenv("psql_password"),  # The password for the user
            "port": os.getenv("psql_port")       # Port
        }
        self.connection = None

    def terminate(self, id, timet):
        """
        Method to terminate session after 2 minutes
        """
        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(**self.cred)
            cursor = connection.cursor()
            current_datetime = datetime.now()
            target_time = (datetime.combine(date.today(), timet) + timedelta(minutes=10)).time()
            
            if datetime.now().time() < target_time:
                query = "SELECT * FROM current WHERE id = %s"
                cursor.execute(query, (id,))
                res = cursor.fetchone()
                if res is None:
                    return
        
            query = "DELETE FROM current WHERE id = %s"
            cursor.execute(query, (id,))
            connection.commit()
        except Exception as error:
            print(f"Error in terminating session: {error}")
            return {'message': f'Error: {str(error)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def generate_tokens(self, id, length: int = 64) -> dict:
        """
        Generate a cryptographically secure token and manage session.
        
        Args:
            id: User ID
            length: Desired length of the token (default: 64)
            
        Returns:
            dict: Response containing message and token if successful
        """
        connection = None
        cursor = None
        
        try:
            # Generate token
            random_components = [
                secrets.token_urlsafe(length),
                str(uuid.uuid4()),
                str(time.time_ns()),
                secrets.token_hex(length),
            ]
            
            combined = f"{self.salt}{''.join(random_components)}"
            
            hasher = hashlib.sha3_512()
            hasher.update(combined.encode('utf-8'))
            hashed = hasher.digest()
            
            tokens = base64.urlsafe_b64encode(hashed).decode('utf-8')
            tokens = ''.join(c for c in tokens if c.isalnum())
            
            if len(tokens) < length:
                padding = ''.join(secrets.choice(string.ascii_letters + string.digits)
                                for _ in range(length - len(tokens)))
                tokens += padding
            else:
                tokens = tokens[:length]

            # Database operations
            connection = psycopg2.connect(**self.cred)
            cursor = connection.cursor()
            
            # Check for existing session
            query = "SELECT id FROM current WHERE id = %s"
            cursor.execute(query, (id,))
            idt = cursor.fetchone()
            
            if idt is not None:
                return {'message': 'Logout from previous session'}
            
            # Create new session
            current_datetime = datetime.now()
            current_time = current_datetime.time()
            today = date.today()
            
            query = """
                INSERT INTO current (id, token, time, date) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (id, tokens, current_time, today))
            connection.commit()
            
            # Start termination thread
            # thread = threading.Thread(
            #     target=self.terminate,
            #     args=(id, current_time)
            # thread.daemon = True  # Make thread daemon so it exits when main program exits
            # thread.start()
            
            return {'message': 'session created', 'token': tokens}
            
        except Exception as error:
            print(f"Error in generate_tokens: {error}")
            return {'message': f'Error: {str(error)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def termination(self, tokens):
        """
        Terminate a session based on the token.
        """
        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(**self.cred)
            cursor = connection.cursor()
            query = "SELECT * FROM current WHERE token = %s"
            cursor.execute(query, (tokens,))
            res = cursor.fetchall()
            print(res)
            if res:
                query = "DELETE FROM current WHERE token = %s"
                cursor.execute(query, (tokens,))
            connection.commit()
        except Exception as error:
            print(f"Error in termination: {error}")
            return {'message': f'Error: {str(error)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def validation(self, tokens):
        """
        Validate a session based on the token.
        """
        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(**self.cred)
            cursor = connection.cursor()
            query = "SELECT * FROM current WHERE token = %s"
            cursor.execute(query, (tokens,))
            res = cursor.fetchall()
            if not res:
                return {'message': 'Session not available'}
            
            self.terminate(res[0][1], res[0][3])
            cursor.execute(query, (tokens,))
            res = cursor.fetchall()
            if not res:
                return {'message': 'Session not available'}
            
            data = {'id': res[0][0], 'file_id': res[0][1]}
            connection.commit()
            return {'message': 'session found', 'data': data}
        except Exception as error:
            print(f"Error in validation: {error}")
            return {'message': f'Error: {str(error)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def set_file_id(self, tokens, file_id):
        """
        Set the file_id for a session based on the token.
        """
        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(**self.cred)
            cursor = connection.cursor()
            query = "SELECT * FROM current WHERE token = %s"
            cursor.execute(query, (tokens,))
            res = cursor.fetchall()
            if not res:
                return {'message': 'Session not available'}
            
            query = "UPDATE current SET file_id = %s WHERE token = %s"
            cursor.execute(query, (file_id, tokens))
            connection.commit()
            return {'message': 'session found'}
        except Exception as error:
            print(f"Error in set_file_id: {error}")
            return {'message': f'Error: {str(error)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Usage
if __name__ == "__main__":
    tokens_generator = TokenService()
    secure_tokens = tokens_generator.generate_tokens(1)
    print(f"Generated token: {secure_tokens}")
    tokens_generator.termination(secure_tokens['token'])