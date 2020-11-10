from flask_restx import Resource, Namespace, fields

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.search import search
from simvestr.models import db, Stock
from simvestr.helpers.api_models import watchlist_item_model

authorizations = {
    "TOKEN-BASED": {
        "name": "API-TOKEN",
        "in": "header",
        "type": "apiKey"
    }
}
api = Namespace(
    'watchlist',
    authorizations=authorizations,
    security="TOKEN-BASED",
    description="Query , add and remove stocks from a users watch list."
)

api.models[watchlist_item_model.name] = watchlist_item_model

watchlist_query_model = api.inherit(
    'WatchlistQueryItem',
    watchlist_item_model,
    dict(
        quote=fields.Float(
            required=True,
            description="Quote price per share of stock",
            example=1200
        ),
    )
)

watchlist_model = api.model(
    'Watchlist',
    dict(
        watchlist=fields.List(fields.Nested(watchlist_query_model)),
    )
)

@api.route('/')
class WatchlistAll(Resource):
    # @api.param('watchlist_id', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def get(self):
        user = get_user()
        watchlist_list = []
        for stock in user.watchlist.stocks:
            watchlist_list.append(
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "quote": search(query="quote", arg=stock.symbol)
                }
            )

        return watchlist_list, 200


def in_watchlist(symbol, user) -> bool:
    stock = [s.symbol for s in user.watchlist.stocks if s.symbol == symbol]
    if stock:
        return True
    return False


@api.route('/symbol/<string:symbol>')
class WatchlistPost(Resource):
    # @api.param('symbol', 'Stock or crypto symbol to be searched')
    @api.marshal_with(watchlist_item_model, envelope='resource')
    @api.response(200, "Entry in watchlist")
    @api.response(201, "Entry created")
    @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def post(self, symbol: str):

        symbol = symbol.upper()

        user = get_user()

        if not in_watchlist(symbol, user):
            user.watchlist.stocks.append(
                Stock.query.filter_by(symbol=symbol.upper()).first()
            )
            db.session.commit()
            return {"symbol": symbol}, 201
        else:
            return {"symbol": symbol}, 200

    @api.response(200, "Not in watchlist")
    @api.response(200, "Removed from watchlist")
    @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def delete(self, symbol: str):
        user = get_user()
        symbol = symbol.upper()

        stock = Stock.query.filter_by(symbol=symbol.upper()).first()

        if not stock:
            return {"symbol": None}, 404

        if stock in user.watchlist.stocks:
            user.watchlist.stocks.remove(stock)
            db.session.commit()
            return {"symbol": symbol}, 201
        else:
            return {"symbol": symbol}, 200
