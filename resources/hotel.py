from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from models.site import SiteModel
from flask_jwt_extended import jwt_required




class Hoteis(Resource):
    query_params = reqparse.RequestParser()
    query_params.add_argument("cidade", type=str, default="", location="args")
    query_params.add_argument("estrelas_min", type=float, default=0, location="args")
    query_params.add_argument("estrelas_max", type=float, default=0, location="args")
    query_params.add_argument("diaria_min", type=float, default=0, location="args")
    query_params.add_argument("diaria_max", type=float, default=0, location="args")
    query_params.add_argument("limit", type=float, default=0, location="args")
    query_params.add_argument("offset", type=float, default=0, location="args")

 
    def get(self):
        filters = Hoteis.query_params.parse_args()
 
        query = HotelModel.query
 
        if filters["cidade"]:
            query = query.filter(HotelModel.cidade == filters["cidade"])
        if filters["estrelas_min"]:
            query = query.filter(HotelModel.estrelas >= filters["estrelas_min"])
        if filters["estrelas_max"]:
            query = query.filter(HotelModel.estrelas <= filters["estrelas_max"])
        if filters["diaria_min"]:
            query = query.filter(HotelModel.diaria >= filters["diaria_min"])
        if filters["diaria_max"]:
            query = query.filter(HotelModel.diaria <= filters["diaria_max"])
        if filters["limit"]:
            query = query.limit(filters["limit"])
        if filters["offset"]:
            query = query.offset(filters["offset"])
 
        return {"hoteis": [hotel.json() for hotel in query]}



class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank.")
    atributos.add_argument('estrelas')
    atributos.add_argument('diaria')
    atributos.add_argument('cidade')
    atributos.add_argument('site_id', type=int, required=True, help="Every hotel needs to be linked to a site")

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found.'}, 404

    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400 #Bad Request

        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados.get('site_id')):
            return {'message': 'The hotel must be associated to a valid site id'}, 400

        try:
            hotel.save_hotel()
        except:
            return {"message": "An error ocurred trying to create hotel."}, 500 #Internal Server Error
        return hotel.json(), 201

    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        hotel.save_hotel()
        return hotel.json(), 201

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            hotel.delete_hotel()
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found.'}, 404

