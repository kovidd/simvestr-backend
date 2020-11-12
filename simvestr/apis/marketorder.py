# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:23:31 2020

@author: Kovid
"""
from datetime import datetime

from flask_restx import Resource, fields, reqparse, Namespace

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.portfolio import stock_balance
from simvestr.helpers.search import get_details
from simvestr.models import db, Transaction, Stock
from simvestr.apis.search import StockDetails
from simvestr.models.api_models import market_order_model

api = Namespace(
    "marketorder",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Buying and selling stocks",
    title="Simvestr",
    description="Back-end API for placing market-orders",
)

api.models[market_order_model.name] = market_order_model

trade_parser = reqparse.RequestParser()
trade_parser.add_argument("symbol", type=str)
trade_parser.add_argument("quote", type=float)
trade_parser.add_argument("trade_type", type=str)
trade_parser.add_argument("quantity", type=int)

def check_price(symbol, quote):
    stock_details = get_details(symbol.upper())

    current_quote = stock_details["quote"]["c"]
    cost_diff = abs(current_quote - quote)
    allowed_cost_diff = 0.0005 * quote # cost difference of 0.05%
    
    print('current price quote:', quote)
    print('actual price', current_quote)
    print('price difference', cost_diff)
    
    # if the cost hasn't changed more than 0.05%
    # otherwise if quote is same as current price, commit transaction
    if (cost_diff <= allowed_cost_diff or current_quote == quote) :
        return False, cost_diff
    
    return True, cost_diff


@api.route("")
class TradeStock(Resource):
    @api.response(200, "Successful")
    @api.response(422, "Unprocessable Entity")
    @api.response(417, "Requested Range Not Satisfiable")
    @api.response(417, "Expectation Failed")
    @api.doc(model="Market Order", body=market_order_model, description="Places a market order")
    @api.marshal_with(market_order_model)
    @requires_auth
    def post(self):
        args = trade_parser.parse_args()
        symbol: str = args.get("symbol")
        quote = args.get("quote")
        trade_type = args.get("trade_type")
        quantity = args.get("quantity")
        symbol = symbol.upper()  # TODO: Need wrapper function to automaticlly uppercase the input

        user = get_user()  # get user details from token
        stock = Stock.query.filter_by(symbol=symbol).first()
        fee = 0
        quantity = -quantity if trade_type == "sell" else quantity
        
        # --- Buy --- #
        if quantity > 0:  # check if user even has enough money to buy this stock quantity
            balance_adjustment = ((quote * quantity) + fee)
            if user.portfolio.balance - balance_adjustment < 0:
                return {"message": "Expectation Failed - Insufficient funds"}, 417
            
            variation, slippage = check_price(symbol, quote)
            if variation:
                return {"message": "Expectation Failed - Current price has changed, can't commit this transaction"}, 417
            if stock not in user.portfolio.stocks:
                user.portfolio.stocks.append(stock)
        # --- Buy-ends --- #

        # --- Sell --- #
        elif quantity < 0:  # check if user owns this stock first, then the quantity he's
            check_stock = stock_balance(user, symbol)

            if not check_stock:
                return {"message": "Expectation Failed - You currently don't own this stock"}, 417

            if check_stock[0] + quantity < 0:
                return {"message": "Expectation Failed - Insufficient quantity of stock to sell"}, 417
            
            variation, slippage = check_price(symbol, quote)
            if variation:
                return {"message": "Requested Range Not Satisfiable - Current price has changed, can't commit this transaction"}, 416

            if check_stock[0] + quantity == 0:
                user.portfolio.stocks.remove(stock)

            balance_adjustment = (quote * quantity) + fee
        else:
            return {"message": f"Invalid quantity. Quantity must be a non zero integer. Received {quantity}"}, 422

        stock.last_quote = quote

        user.portfolio.balance -= balance_adjustment  # update user's balance after trade
        # --- Sell-ends --- #

        new_transaction = Transaction(
            portfolio_id=user.portfolio.id,
            symbol=symbol,
            quote=quote,
            quantity=quantity,
            fee=fee,
        )

        db.session.add(new_transaction)
        db.session.commit()


        return dict(symbol=symbol, quote=quote, quantity=quantity, slippage=slippage, ), 200
