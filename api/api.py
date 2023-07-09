from flask import Flask, json, request
from waitress import serve
import psycopg2
import os
from datetime import datetime

#.env
from dotenv import load_dotenv
load_dotenv('.env')

##Class

class Log:
    def __init__(self, content):
        self.content = content
        self.datetime = datetime.now()
    def save_db(self):
        try:
            mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)            
            cursor=mydb.cursor()
            sql = "INSERT INTO log(content, datetime) VALUES(%s,%s)"
            cursor.execute(sql, (str(self.content), self.datetime))
            mydb.commit()
            mydb.close()
        except Exception as e:
            print("Error en insert " + repr(e))

#Database

database = os.environ.get('NAME_DB')
host_db = os.environ.get('HOST_DB')
user = os.environ.get('USER_DB')
password = os.environ.get('PW_DB')
port_db = os.environ.get('PORT_DB')
mydb = psycopg2.connect(database=os.environ.get('NAME_DB'),
                        host=os.environ.get('HOST_DB'),
                        user=os.environ.get('USER_DB'),
                        password=os.environ.get('PW_DB'),
                        port=os.environ.get('PORT_DB'))
cursor=mydb.cursor()

#Server 
api = Flask(__name__)

@api.route('/new_message', methods=['POST'])
def new_message():
    try:
        contenido = request.json
        log = Log("REQ: "+json.dumps(contenido))
        log.save_db()
        if 'recipients' in contenido and 'body' in contenido:
            body = contenido['body']
            for recipient in contenido['recipients']:
                sql = "SELECT id FROM contact where identifier=%s LIMIT 1"
                cursor.execute(sql, (str(recipient['handle']),))
                try:
                    result = cursor.fetchone()
                    mydb.commit()
                    if result:
                        sql = "INSERT INTO message(contact_id, content, type, datetime, sended) VALUES(%s, %s, %s, %s,%s)"
                        cursor.execute(sql, (result[0], body, 'Output', datetime.now(), False))
                        mydb.commit()
                except:
                    mydb.commit()
            return json.dumps({
               "type": 'success',
               "message": 'success'
            })
        else:
            log = Log("RES: Information incomplete")
            log.save_db()            
            return json.dumps({
                "type": 'error',
                "message": 'Information incomplete'
            })
        
    except Exception as e:
        log = Log("RES: " + repr(e))
        log.save_db()                    
        return json.dumps({
            "type": 'error',
            "message": repr(e)
        })    
    


serve(api, host=os.environ.get('HOST'), port=os.environ.get('PORT'))