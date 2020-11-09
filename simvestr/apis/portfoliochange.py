from flask_restx import Resource, Namespace

from simvestr.helpers.auth import get_user
from simvestr.models import PortfolioPrice

api = Namespace("view portfolio history", description="Api for viewing Portfolio change over time")


@api.route("/user")
class PortfolioQuery(Resource):
    @api.response(200, "Successful")
    @api.response(601, "Portfolio doesn't exist")
    def get(self):
        user = get_user()

        balances = (PortfolioPrice.query
                    .filter(PortfolioPrice.portfolio_id == user.portfolio.id)
                    .order_by(PortfolioPrice.timestamp.desc())
                    .all()
                    )

        data = {
            b.id: dict(
                user_id=user.id,
                portfolio_id=b.portfolio_id,
                balance=b.close_balance,
                investment_value=b.investment_value,
                total_value=b.close_balance + b.investment_value,
            ) for b in balances
        }

        return data, 200
