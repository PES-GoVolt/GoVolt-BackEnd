from firebase_admin import firestore
import pandas as pd
from sodapy import Socrata
from rest_framework import serializers
from goVolt.settings import AUTH_DB
from goVolt.settings import FIREBASE_DB
from firebase_admin import auth, exceptions
from .serializers import RutaViajeSerializer
import json
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from api.users.models import CustomUser

def store_ruta(data):

    try:   

        creador_id = AUTH_DB.current_user["localId"]
        #creador_id = "cNtxKjlvPTM6TE6aaTC6mjl1hj12"

        data['creador'] = creador_id
        data['participantes'] = None

        serializer = RutaViajeSerializer(data=data)

        if serializer.is_valid():
            collection_ref = FIREBASE_DB.collection('rutas')
            new_ruta = collection_ref.add(serializer.data)

            return Response({'message': new_ruta[1].id},status=200)
        else:
            raise ValidationError(serializer.errors)
        
    except Exception as e:
        return Response({'message': str(e)},status=400)

def get_mis_rutas():
    creador_id = AUTH_DB.current_user["localId"]
    #creador_id = "cNtxKjlvPTM6TE6aaTC6mjl1hj12"

    rutas_ref = FIREBASE_DB.collection('rutas')
    rutas = rutas_ref.where('creador', '==', creador_id).get()

    # Itera sobre los resultados para obtener los datos de las rutas encontradas
    rutas_encontradas = []
    for resultado in rutas:
        datos_ruta = resultado.to_dict()
        # Agrega el identificador del documento a los datos de la ruta
        datos_ruta['id'] = resultado.id
        rutas_encontradas.append(datos_ruta)
    
    return rutas_encontradas

def get_all_rutas():

    rutas_ref = FIREBASE_DB.collection('rutas')
    rutas = rutas_ref.get()

    # Itera sobre los resultados para obtener los datos de las rutas encontradas
    rutas_encontradas = []
    for resultado in rutas:
        datos_ruta = resultado.to_dict()
        # Agrega el identificador del documento a los datos de la ruta
        datos_ruta['id'] = resultado.id
        rutas_encontradas.append(datos_ruta)
    
    return rutas_encontradas

def get_ruta_by_id(id):

    doc_ref = FIREBASE_DB.collection('rutas').document(id)

    res = doc_ref.get()

    data = {}
    data['id'] = id
    data['ubicacion_inicial'] =  res.get('ubicacion_inicial')
    data['ubicacion_final'] =  res.get('ubicacion_final')
    data['precio']= res.get('precio')
    data['num_plazas']= res.get('num_plazas')
    data['fecha']= res.get('fecha')
    data['creador']= res.get('creador')
    #data['participantes']= res.get('participantes')

    serializer = RutaViajeSerializer(data=data)
    if serializer.is_valid():
        return serializer.data
    else:
        raise serializers.ValidationError(serializer.errors)

def edit_ruta(id, ubicacion_inicial, ubicacion_final, precio, num_plazas, fecha, creador):

    try:

        # Obten el usuario autentificado
        firebase_uid = AUTH_DB.current_user["localId"]
        #firebase_uid = "cNtxKjlvPTM6TE6aaTC6mjl1hj12"

        ruta_ref = FIREBASE_DB.collection('rutas').document(id)
        
        #comprueba que el usuario que edita la ruta sea el creador
        if (firebase_uid == creador):
            ruta_ref.update({
                'ubicacion_inicial': ubicacion_inicial,
                'ubicacion_final': ubicacion_final,
                'precio': precio,
                'num_plazas': num_plazas,
                'fecha': fecha
            })

            return Response({'message': "OK"},status=200)
        else:
            return Response({'message': "USER UNAUTHORIZED"}, status=401)
        
    except Exception as e:
        error_message = e.args[1]
        error_data = json.loads(error_message)

        code = error_data['error']['code']
        msg = error_data['error']['message']

        return Response({'message': msg},status=code)

def add_participant(ruta_id, participant_id):
    try:

        # Obten el usuario autentificado
        logged_user = AUTH_DB.current_user["localId"]
        #logged_user = "cNtxKjlvPTM6TE6aaTC6mjl1hj12"

        ruta_ref = FIREBASE_DB.collection('rutas').document(ruta_id)
        res = ruta_ref.get()

        creador_ruta = res.get("creador")
        participante = participant_id

        # si el que añade no es el creador ni el participante => error
        if(logged_user == creador_ruta or logged_user == participante):
            # comprobar que num_plazas > count(participantes)
            participantes = res.get("participantes")

            if (participantes == None):
                participantes = []

            if participant_id not in participantes:
                if (res.get("num_plazas") > len(participantes)):
                    participantes.append(participant_id)
                    ruta_ref.update({"participantes": participantes})

                    return Response({'message': "OK"},status=200)

                else:
                    return Response({'message': "TOO MANY PARTICIPANTS"}, status=500)
            else:
                return Response({'message': "PARTICIPANT ALREADY EXIST"}, status=500)
        else:
            return Response({'message': "USER UNAUTHORIZED"}, status=401)

    except Exception as e:
        error_message = e.args[1]
        error_data = json.loads(error_message)

        code = error_data['error']['code']
        msg = error_data['error']['message']

        return Response({'message': msg},status=code)

def get_routes_participadas():
    try:
        participant_id = AUTH_DB.current_user["localId"]
        #participant_id = "cNtxKjlvPTM6TE6aaTC6mjl1hj120"
        # Query Firestore for routes where the participant is in the participantes array
        routes_ref = FIREBASE_DB.collection('rutas')
        query = routes_ref.where('participantes', 'array_contains', participant_id)
        routes = query.stream()

        # Iterate over the results to get the data of the routes found
        routes_found = []
        for route in routes:
            route_data = route.to_dict()
            route_data['id'] = route.id  # Add the document ID to the data
            routes_found.append(route_data)

        return routes_found

    except Exception as e:
        print(str(e))
        # Handle other exceptions if necessary
        return []