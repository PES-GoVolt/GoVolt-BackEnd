import warnings
from datetime import datetime

from firebase_admin import db, auth
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from rest_framework import serializers

from goVolt.settings import FIREBASE_DB
from .serializers import MessageSerializer
from .utils import get_timestamp_now


def save_message(message, room_name, sender):
    ref = db.reference("/")

    current_datetime = datetime.now()
    unix_timestamp = int(current_datetime.timestamp() * 1000)

    messagedata = {
        "content": message,
        "room_name": room_name,
        "sender": sender,
        "timestamp": unix_timestamp
    }
    message_node = ref.child(room_name).push()
    message_node.set(messagedata)
def get_all_messages():
    ref = db.reference('/')
    messages_data = ref.get()
    messages = []
    if messages_data:
        for message_id, message_info in messages_data.items():
            content = message_info.get('content')
            room_name = message_info.get('room_name')
            sender = message_info.get('sender')
            timestamp = message_info.get('timestamp')

            if content and room_name and sender and timestamp:
                message = {
                    'content': content,
                    'room_name': room_name,
                    'sender': sender,
                    'timestamp': timestamp
                }
                messages.append(message)
            messages = sorted(messages, key=lambda x: x['timestamp'])
            print(messages)
            serializer = MessageSerializer(data=messages,many=True)
            if serializer.is_valid():
                return serializer.data
            else:
                raise serializers.ValidationError(serializer.errors)
    return messages


def get_room_messages(room_name):
    ref = db.reference('/' + room_name)
    messages_data = ref.get()
    messages = []
    if messages_data:
        for message_id, message_info in messages_data.items():
            if 'content' in message_info:
                message = {
                    'content': message_info['content'],
                    'room_name': message_info['room_name'],
                    'sender': message_info['sender'],
                    'timestamp': message_info['timestamp']
                }
                messages.append(message)
        messages = sorted(messages, key=lambda x: x['timestamp'])
        serializer = MessageSerializer(data=messages, many=True)
        if serializer.is_valid():
            return serializer.data
        else:
            raise serializers.ValidationError(serializer.errors)
    return messages


def modify_timestamp_chat(id_chat):
    collection_name = 'chats'
    chat_ref = FIREBASE_DB.collection(collection_name).document(id_chat)
    chat_info = chat_ref.get().to_dict(),
    chat_info["last_conection"] = get_timestamp_now()
    chat_ref.update({"last_conection": chat_info["last_conection"]})


def save_chat(userUid, room_name, uidCreator, firebase_token):
    collection_name = 'chats'
    collection_ref = FIREBASE_DB.collection(collection_name)

    decoded_token = auth.verify_id_token(firebase_token)
    logged_uid = decoded_token['uid']

    ruta_ref = FIREBASE_DB.collection('rutas').document(room_name)
    res_routes = ruta_ref.get().to_dict()

    participantes = res_routes.get("participantes") or []

    if logged_uid not in participantes:
        if (res_routes.get("num_plazas") > len(participantes)):
            # Realiza la consulta en la colección requests_participants
            query = FIREBASE_DB.collection('requests_participants').where(
                filter=FieldFilter('user_id', '==', logged_uid)).where(filter=FieldFilter('ruta_id', '==', room_name))
            request = query.get()
            # Verifica si hay resultados
            if not request:
                # No hay resultados, inserta un nuevo documento
                new_request = {
                    'user_id': logged_uid,
                    'ruta_id': room_name,
                }
                FIREBASE_DB.collection('requests_participants').add(new_request)
            else:
                # Ya existen documentos con los valores proporcionados
                return "error2"

            user_ref = FIREBASE_DB.collection('users').document(userUid)
            res = user_ref.get()
            creator = False

            user_ref2 = FIREBASE_DB.collection('users').document(logged_uid)
            res2 = user_ref2.get()
            if (userUid == uidCreator):
                creator = True

            collection_ref.add({
                "userUid_sender": userUid,
                "userUid_reciever": logged_uid,
                "room_name": "chats/" + room_name + "/" + logged_uid,
                "last_conection": get_timestamp_now(),
                "creator": creator,
                "email": res2.get('email')
            })

            creator = False
            if (logged_uid == uidCreator):
                creator = True

            collection_ref.add({
                "userUid_sender": logged_uid,
                "userUid_reciever": userUid,
                "room_name": "chats/" + room_name + "/" + logged_uid,
                "last_conection": get_timestamp_now(),
                "creator": creator,
                "email": res.get('email')
            })

            return "chats/"+room_name + "/" + logged_uid
    else:
        return "error1"

def get_chats_user_loged(firebase_token):
    collection_name = 'chats'

    decoded_token = auth.verify_id_token(firebase_token)
    logged_uid = decoded_token['uid']
    chat_ref = FIREBASE_DB.collection(collection_name)
    warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud.firestore_v1.base_collection")
    query = chat_ref.where('userUid_sender', '==', logged_uid).order_by('last_conection',
                                                                        direction=firestore.Query.DESCENDING)
    docs = query.get()
    chats = []
    for doc in docs:
        data = doc.to_dict()
        data['room_name'] = data.get('room_name')
        data['last_conection'] = data.get('last_conection')
        data['userUid_sender'] = data.get('userUid_sender')
        data['userUid-reciever'] = data.get('userUid-reciever')
        data['email'] = data.get('email')
        data['creator'] = data.get('creator')
        data['id_chat'] = doc.id
        chats.append(data)

    return chats

def get_all_chats():
    chats_ref = FIREBASE_DB.collection('chats')
    docs = chats_ref.stream()
    chats = []
    for doc in docs:
        chat = doc.to_dict()
        chats.append(chat)
    return chats
  