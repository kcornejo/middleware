#imports
import socket
import threading
import os
import requests
import json
from datetime import datetime
from threading import Timer
from interval_timer import IntervalTimer
import psycopg2

#.env
from dotenv import load_dotenv
load_dotenv('.env')

#Database
mydb = psycopg2.connect(database=os.environ.get('NAME_DB'),
                        host=os.environ.get('HOST_DB'),
                        user=os.environ.get('USER_DB'),
                        password=os.environ.get('PW_DB'),
                        port=os.environ.get('PORT_DB'))
cursor=mydb.cursor()


#Class
class Contact:
    def __init__(self, identifier, blocked, id_api):
        self.identifier = identifier
        self.blocked = blocked
        self.id = 0
        self.id_api = id_api
    def update_db(self):
        sql = "UPDATE contact SET identifier = %s, blocked = %s, id_api=%s WHERE id = %s"
        val = (self.identifier, self.blocked, self.id_api, self.id)
        cursor.execute(sql, val)
        mydb.commit()
        
    def save_db(self):
        sql = 'INSERT INTO contact(identifier, blocked,id_api) VALUES(\'{identifier}\',{blocked},\'{id_api}\') RETURNING id'.format(identifier=self.identifier, blocked=self.blocked, id_api=self.id_api)
        cursor.execute(sql)
        mydb.commit()
        self.id = cursor.fetchone()[0]
    def save(self):
        self.call_api_contact()
        if self.id:
            self.update_db()
        else:
            self.save_db()
    def search(self,identifier):
        sql = "SELECT id, identifier, blocked,id_api FROM contact where identifier='{identifier}' LIMIT 1".format(identifier=identifier)
        cursor.execute(sql)
        try:
            result = cursor.fetchone()
            mydb.commit()
            if result:
                self.id = result[0]
                self.identifier = result[1]
                self.blocked = result[2]
                self.id_api = result[3]
                return self
            return result
        except:
             mydb.commit()
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
                self.id_api = res_json['id']
        except:
            self.call_api_new()

    def call_api_new(self):
        
        try:

            url = "https://api2.frontapp.com/contacts"
            payload = json.dumps({
            "name": self.identifier,
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
        except:
            print("Error en call")

#Class
class Message:
    def __init__(self, contact_id, content, type, datetime, sended, id, contact_id_api,contact_identifier):
        self.contact_id = contact_id
        self.content = content
        self.type = type
        self.datetime = datetime
        self.sended = sended
        self.id = id
        self.contact_id_api = contact_id_api
        self.contact_identifier = contact_identifier
    def update_db(self):
        sql = "UPDATE message SET contact_id = %s, content = %s, type= %s, datetime = %s, sended = %s WHERE id = %s "
        val = (self.contact_id, self.content, self.type, self.datetime,self.sended, self.id)
        cursor.execute(sql, val)
        mydb.commit()
        
    def save_db(self):
        sql = 'INSERT INTO message(contact_id, content, type, datetime, sended) VALUES(\'{contact_id}\',\'{content}\',\'{type}\',\'{datetime}\',{sended})'.format(contact_id=self.contact_id, content=self.content, type=self.type, datetime=self.datetime, sended=self.sended)
        cursor.execute(sql)
        mydb.commit()
        self.id = cursor.lastrowid
        
    def save(self):
        if self.id:
            self.update_db()
        else:
            self.save_db()
        
    def search(self, id):
        cursor.execute("SELECT id,contact_id, content, type, datetime, sended FROM contact where id='{id}' LIMIT 1".format(id=id))
        result = cursor.fetchone()
        mydb.commit()
        if result:
            self.id = result[0]
            self.identifier = result[1]
            self.blocked = result[2]
            return self
        return result
    def search_awaiting_send():
        cursor.execute("SELECT message.id,contact_id, content, type, datetime, sended, contact.id_api,contact.identifier  FROM message INNER JOIN contact on message.contact_id = contact.id where sended = False and type = 'Input' order by message.id asc")
        result = cursor.fetchall()
        mydb.commit()
        if len(result) > 0:
            list_message = []
            for obj in result:
                list_message.append(Message(obj[1], obj[2], obj[3], obj[4], obj[5], obj[0], obj[6], obj[7]))
            return list_message
        else:
            return False
    def search_awaiting():
        cursor.execute("SELECT message.id,contact_id, content, type, datetime, sended,  contact.id_api,contact.identifier  FROM message INNER JOIN contact on message.contact_id = contact.id where sended = False and type = 'Output' order by message.id asc")
        result = cursor.fetchall()
        mydb.commit()
        if len(result) > 0:
            list_message = []
            for obj in result:
                list_message.append(Message(obj[1], obj[2], obj[3], obj[4], obj[5], obj[0], obj[6], obj[7]))
            return list_message
        else:
            return False    

#Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = os.environ.get('HOST')
port = int(os.environ.get('PORT'))
server.bind((host, port))
server.listen()
print(f"Server running on {host}:{port}")

#Methods
clients = []
identifiers = []  

def connect_api(message, client_sended):
    print(f"{message}")

def handle_message(client, id):
    contact = Contact(id, False, '')
    contact.search(id)
    contact.save()
    while True:
        try:
            #Limit 1024
            message = client.recv(1024).decode('utf-8')
            if message != "":
                objMessage = Message(contact.id, message, 'Input', datetime.now(), False, 0, '', '')
                objMessage.save()
            else:
                client.close()
        except:
            index = clients.index(client)
            identify = identifiers[index]
            clients.remove(client)
            identifiers.remove(identify)
            print(f"Client disconnected {identify}")
            client.close()
            break

def manage_messages():
    for interval in IntervalTimer(1):
        if len(clients) > 0:
            #DB to Client
            messages = Message.search_awaiting()
            if(messages):
                for message in messages:
                    try:
                        identifier_client = identifiers.index(message.identifier)
                        clients[identifier_client].send(message.content.encode('utf-8'))
                    except:
                        identifier_client=False
                    message.sended= True
                    message.save()
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
                                "name": message.contact_identifier,
                                "handle": message.contact_identifier,
                            },
                            "body_format": "markdown",
                            "body": message.content
                        })
                        headers = {
                        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJvdmlzaW9uaW5nIiwicHJpdmF0ZToqIiwic2hhcmVkOioiXSwiaWF0IjoxNjg3ODIxNjk1LCJpc3MiOiJmcm9udCIsInN1YiI6IjMxZWIwY2E4MzdmNjFlMjA5NzI2IiwianRpIjoiNzM5NjZlYzhmMjY5YTRkNyJ9.2QBm0jYHpRk-P_o_M9z94Gqx3kWx15YP6eEl4v3Foho',
                        'Content-Type': 'application/json'
                        }

                        response = requests.request("POST", url, headers=headers, data=payload)
                        response_json = response.json()
                        if('status' in response_json and response_json['status'] == 'accepted'):
                            message.sended= True
                            message.save()
                    except:
                        print('error')
                                         
def manage_connection():
    manage_messages_th = threading.Thread(target=manage_messages)
    manage_messages_th.start()
    while True:
        client, address = server.accept()
        client.send("@id".encode("utf-8"))
        id = client.recv(1024).decode('utf-8')
        clients.append(client)
        identifiers.append(id)
        thread = threading.Thread(target=handle_message , args=(client,id))
        thread.start()


#Demon
manage_connection()