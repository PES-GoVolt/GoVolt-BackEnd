from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.chargers.services import get_all_chargers,read_data,store_charge_points_fb,get_charger_by_id
from api.chargers.utils import nearest_point

class ChargerLocationApiView(APIView):
    def get(self,request):
        response_data = get_all_chargers()
        return Response(response_data,status=status.HTTP_200_OK)

class NearestChargerApiView(APIView):
    def post(self, request):
        try:
            longitud = request.data['longitud']
            latitud = request.data['latitud']
            nearest_charger = get_charger_by_id(nearest_point((longitud, latitud)))
            return Response(nearest_charger, status=status.HTTP_200_OK)
        except KeyError:
            return Response({"error": "Missing 'longitud' or 'latitud' in request body."}, status=status.HTTP_400_BAD_REQUEST)

class ChargerApiView(APIView):
    def get(self, request, id):
        charger = get_charger_by_id(id)
        if charger is not None:
            return Response(charger, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Charger not found"}, status=status.HTTP_404_NOT_FOUND)
    
class ChargerDataBaseApiView(APIView):
    def post(self,request):
        chargers = read_data()
        store_charge_points_fb(chargers)
        return Response({'message':'The chargers database was updated'},status=status.HTTP_201_CREATED)
