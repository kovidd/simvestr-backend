from simvestr.models import db
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import func, and_, join
from flask import jsonify
from flask_restx import Resource, reqparse, Namespace
from sqlalchemy.sql import select
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice
from simvestr.helpers.auth import requires_auth, get_user

api = Namespace("leader board", description="Leaderboard")

authorizations = {
    "TOKEN-BASED": {
        "name": "API-TOKEN",
        "in": "header",
        "type": "apiKey"
    }
}
api = Namespace(
    'leaderboard',
    authorizations=authorizations,
    security="TOKEN-BASED",
    description="query for leaderboard"
)

ORDINAL_SUFFIXES = ["th", "st", "nd", "rd", "th"]


def get_ordered_portfolios():
    # returns array of {"porfolio_id","value"} objects ordered by value of the portfolio (closing_balance + investment value)
    subq = db.session.query(PortfolioPrice.portfolio_id, func.max(PortfolioPrice.timestamp).label(
        "maxdate")).group_by(PortfolioPrice.portfolio_id).subquery("t2")
    close_balances = []
    for p in db.session.query(PortfolioPrice).join(subq, and_(
        PortfolioPrice.portfolio_id == subq.c.portfolio_id,
        PortfolioPrice.timestamp == subq.c.maxdate
    )
    ):
        value = p.close_balance + p.investment_value
        close_balances.append(
            {"portfolio": p.portfolio_id, "value": value})
    return sorted(close_balances, key=lambda i: i["value"], reverse=True)


@ api.route("/position")
class PortfolioQuery(Resource):
    @ api.response(200, "Successful")
    @ api.response(602, "PortfolioPrice doesn\'t exist")
    @ api.doc(
        description="Gets position of user's portfolio",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def get(self):
        user = get_user()
        portfolio_id = user.portfolio.id
        balances_sorted = get_ordered_portfolios()
        pos = 1
        while (balances_sorted[pos - 1]["portfolio"] != portfolio_id):
            pos += 1
        suffix = ORDINAL_SUFFIXES[min(pos % 10, 4)]
        if 11 <= (pos % 100) <= 13:
            suffix = "th"
        return jsonify(str(pos) + suffix)


@api.route("/all")
class TopInvestorsAll(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    @api.doc(
        description="returns array of {'id', 'position', 'user', 'name', 'value'}",
    )
    def get(self):
        balances_sorted = get_ordered_portfolios()
        users = []
        id_value_pos = {}
        portfolios = []
        num_ports = len(balances_sorted)
        if(num_ports > 0):
            for i in range(num_ports):
                id_value_pos.update(
                    {balances_sorted[i]["portfolio"]: [balances_sorted[i]["value"], i+1]})
                users.append(balances_sorted[i]["portfolio"])
            for p in db.session.query(Portfolio).join(Portfolio.user).filter(Portfolio.id.in_(users)).all():
                portfolios.append({"id": p.id, "position": id_value_pos[p.id][1], "user": p.user.first_name +
                                   " "+p.user.last_name, "name": p.portfolio_name, "value": id_value_pos[p.id][0]})
        return jsonify(portfolios)
