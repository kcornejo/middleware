##Imports
from websockets.server import serve
from datetime import datetime, timedelta
from interval_timer import IntervalTimer
from dotenv import load_dotenv

import asyncio
import threading
import psycopg2
import os
import requests
import json
import re
##Vars
id = ''
#.env

load_dotenv('.env')

#Database
database = os.environ.get('NAME_DB')
host_db = os.environ.get('HOST_DB')
user = os.environ.get('USER_DB')
password = os.environ.get('PW_DB')
port_db = os.environ.get('PORT_DB')
#Class
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
            cursor.execute(sql, (str(self.content[:250]), self.datetime))
            mydb.commit()
            mydb.close()
        except Exception as e:
            print("Error en insert " + repr(e))
class Contact:
    def __init__(self, identifier, name, blocked, id_api):
        self.identifier = identifier
        self.name = name
        self.blocked = blocked
        self.id = 0
        self.id_api = id_api
    def update_db(self):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()
        sql = "UPDATE contact SET identifier = %s, name = %s, blocked = %s, id_api=%s WHERE id = %s"
        val = (self.identifier,self.name, self.blocked, self.id_api, self.id)
        cursor.execute(sql, val)
        mydb.commit()
        mydb.close()        
    def save_db(self):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()        
        sql = 'INSERT INTO contact(identifier, name, blocked,id_api) VALUES(%s,%s,%s,%s) RETURNING id'
        cursor.execute(sql, (self.identifier,self.name, self.blocked, self.id_api))
        mydb.commit()
        self.id = int(cursor.fetchone()[0])
        mydb.close()
    def save(self):
        self.call_api_contact()
        if self.id:
            self.update_db()
        else:
            self.save_db()
    def search(self,identifier):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()
        sql = "SELECT id, identifier, blocked,id_api, name FROM contact where identifier=%s LIMIT 1"
        cursor.execute(sql, (identifier,))
        try:
            result = cursor.fetchone()
            mydb.commit()
            mydb.close()
            if result:
                self.id = result[0]
                self.identifier = result[1]
                self.blocked = result[2]
                self.id_api = result[3]
                self.name = result[4]
                return self
            return result
        except:
             mydb.commit()
             mydb.close()
             return False
    def call_api_contact(self):
        try:
            url = "https://api2.frontapp.com/contacts/alt:phone:"+self.identifier
            headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+os.environ.get('BEARER')
            }

            res = requests.request("GET", url, headers=headers)
            res_json = res.json()
            if('_error' in res_json and res_json['_error']['status'] == 404):
                self.call_api_new()
            else:
                if 'id' in res_json:
                    self.id_api = res_json['id']
                else:
                    log = Log('Error en consumo ' + res.text)
                    log.save_db()
        except Exception as e:
            log = Log('Error en obtener contacto '+ repr(e))
            log.save_db()
            self.call_api_new()

    def call_api_new(self):
        
        try:

            url = "https://api2.frontapp.com/contacts"
            payload = json.dumps({
            "name": self.name,
            "handles": [
                {
                "source": "phone",
                "handle": self.identifier
                }
            ]
            })
            headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+os.environ.get('BEARER')
            }

            res = requests.request("POST", url, headers=headers, data=payload)
            res_json = res.json()
            self.id_api = res_json['id']
        except Exception as e:
            log = Log(json.dumps(res_json))
            log.save_db()
            log = Log('Error en crear contacto '+ repr(e))
            log.save_db()
#Class
class Message:
    def __init__(self, contact_id, content, type, datetime, sended, id, contact_id_api,contact_identifier, error, error_count, contact_name):
        self.contact_id = contact_id
        self.content = content
        self.type = type
        self.datetime = datetime
        self.sended = sended
        self.id = id
        self.contact_id_api = contact_id_api
        self.contact_identifier = contact_identifier
        self.error = error
        self.error_count = error_count
        self.contact_name = contact_name
    def update_db(self):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()        
        sql = "UPDATE message SET contact_id = %s, content = %s, type= %s, datetime = %s, sended = %s, error = %s, error_count = %s WHERE id = %s "
        val = (self.contact_id, self.content, self.type, self.datetime,self.sended,self.error, self.error_count, self.id )
        cursor.execute(sql, val)
        mydb.commit()
        mydb.close()
        
    def save_db(self):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()           
        sql = "INSERT INTO message(contact_id, content, type, datetime, sended, error, error_count) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (self.contact_id, self.content, self.type, self.datetime, self.sended, self.error, self.error_count))
        mydb.commit()
        mydb.close()
        self.id = cursor.lastrowid
        
    def save(self):
        if self.id:
            self.update_db()
        else:
            self.save_db()
        
    def search(self, id):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()              
        sql = "SELECT id,contact_id, content, type, datetime, sended FROM contact where id=%s LIMIT 1"
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        mydb.commit()
        mydb.close()
        if result:
            self.id = result[0]
            self.identifier = result[1]
            self.blocked = result[2]
            return self
        return result
    def search_awaiting_send():
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()              
        cursor.execute("SELECT message.id,contact_id, content, type, datetime, sended, contact.id_api,contact.identifier, message.error, message.error_count, contact.name  FROM message INNER JOIN contact on message.contact_id = contact.id where sended = False and type = 'Input' order by message.id asc FOR UPDATE")
        result = cursor.fetchall()
        mydb.commit()
        mydb.close()
        if len(result) > 0:
            list_message = []
            for obj in result:
                list_message.append(Message(obj[1], obj[2], obj[3], obj[4], obj[5], obj[0], obj[6], obj[7], obj[8], obj[9], obj[10]))
            return list_message
        else:
            return False
    def search_awaiting(websocket, id):
        mydb = psycopg2.connect(database=database,
                        host=host_db,
                        user=user,
                        password=password,
                        port=port_db)
        cursor=mydb.cursor()              
        sql = "SELECT message.id,contact_id, content, type, datetime, sended,  contact.id_api,contact.identifier,message.error, message.error_count, contact.name   FROM message INNER JOIN contact on message.contact_id = contact.id where sended = False and type = 'Output' and contact.identifier=%s order by message.id asc"
        cursor.execute(sql, (id, ))
        result = cursor.fetchall()
        mydb.commit()
        mydb.close()
        if len(result) > 0:
            list_message = []
            for obj in result:
                list_message.append(Message(obj[1], obj[2], obj[3], obj[4], obj[5], obj[0], obj[6], obj[7], obj[8], obj[9], obj[10]))
            return list_message
        else:
            return False              
#Functions
def  manage_messages_send():
    for interval in IntervalTimer(1):
            #DB to Api
            messages = Message.search_awaiting_send()
            if(messages):
                for message in messages:
                    if message.contact_id_api == '':
                        continue
                    try:
                        url = "https://api2.frontapp.com/channels/"+os.environ.get('CHANNEL')+"/incoming_messages"
                        payload = json.dumps({
                            "sender": {
                                "contact_id": message.contact_id_api,
                                "name": message.contact_name,
                                "handle": message.contact_identifier,
                            },
                            "body_format": "markdown",
                            "body": message.content
                        })
                        headers = {
                        'Authorization': 'Bearer '+os.environ.get('BEARER'),
                        'Content-Type': 'application/json'
                        }

                        response = requests.request("POST", url, headers=headers, data=payload)
                        response_json = response.json()
                        if('status' in response_json and response_json['status'] == 'accepted'):
                            message.sended= True
                            message.save()
                    except Exception as e:
                        log = Log('Error en envio de mensaje '+ repr(e))
                        log.save_db()  
def manage_messages_bt(websocket, id):                        
    asyncio.run(manage_messages(websocket, id))
    
async def manage_messages(websocket, id):
    for interval in IntervalTimer(1):
            #DB to Client
            messages = Message.search_awaiting(websocket, id)
            if(messages):
                for message in messages:
                    try:
                        await websocket.send(message.content)
                        message.sended= True
                        message.save()      
                    except Exception as e:
                        print(repr(e))
                        log = Log(repr(e))
                        log.save_db() 
                        message.error = repr(e)
                        result = message.datetime + timedelta(minutes=120)
                        if(result <= datetime.now()):
                            message.sended = True
                    message.save() 
##Server            
async def echo(websocket):
    if not ("Secret_Key" in websocket.request_headers and os.environ.get('SECRET_KEY') == websocket.request_headers['SECRET_KEY']):
       await websocket.close()
    counter = False
    contact = False
    async for message in websocket:
        if counter == False:
            id = message
            counter = True
            pattern = r"^[A-Za-z\s]{1,50}\|\+[0-9]{1,3}\s?[0-9]{6,12}$"
            log = Log(f"New Client: {id}")
            log.save_db()
            if re.fullmatch(pattern, id):
                id_complete = id.split("|")
                await websocket.send(f"Welcome {id_complete[1]}")
                contact = Contact(id_complete[1], id_complete[0], False, '')
                contact.search(id_complete[1])
                contact.save()
                manage_messages_th = threading.Thread(target=manage_messages_bt, args=(websocket, id_complete[1]))
                manage_messages_th.start()
            else:
                await websocket.send(f"Id denied {id}")
                await websocket.close()
        else:
            if contact:
                    error_msg = False
                    try:
                        url = "https://api2.frontapp.com/channels/"+os.environ.get('CHANNEL')+"/incoming_messages"
                        payload = json.dumps({
                            "sender": {
                                "contact_id": contact.id_api,
                                "name": contact.name,
                                "handle": contact.identifier,
                            },
                            "body_format": "markdown",
                            "body": message
                        })
                        headers = {
                        'Authorization': 'Bearer '+os.environ.get('BEARER'),
                        'Content-Type': 'application/json'
                        }

                        response = requests.request("POST", url, headers=headers, data=payload)
                        response_json = response.json()
                        if('status' in response_json and response_json['status'] == 'accepted'):
                            error_msg = True
                        else:
                            log = Log('Error en envio de mensaje '+ json.dumps(response_json))
                            log.save_db()    
                    except Exception as e:
                        log = Log('Error en envio de mensaje '+ repr(e))
                        log.save_db()                  
                    objMessage = Message(contact.id, message, 'Input', datetime.now(), error_msg, 0, contact.id_api, contact.identifier, '', 0, contact.name)
                    objMessage.save()

async def main():
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT'))
    msg = f"Server started {host}:{port}"
    log = Log(msg)
    log.save_db()    
    print(msg)
    async with serve(echo, host, port):
        await asyncio.Future() 

#manage_messages_send_th = threading.Thread(target=manage_messages_send) 
#manage_messages_send_th.start()
asyncio.run(main())
