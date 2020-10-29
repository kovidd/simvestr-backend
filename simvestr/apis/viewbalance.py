from flask_restx import Resource, Namespace

from simvestr.helpers.auth import requires_auth, get_user

api = Namespace('view closing balance', description='Api for viewing closing balance for a User')


@api.route("")
class PortfolioPriceUsersQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self):

        user = get_user()

        data = dict(
            plist=[dict(
                portfolio_id=p.id,
                balance=p.close_balance,
                time=str(p.timestamp)
            ) for p in user.portfolio.portfolioprice]
        )
        payload = dict(
            data=data
        )
        return payload



@api.route('/user/')
class PortfolioPriceQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self, ):
        user = get_user()

        data = dict(
            name=user.portfolio.portfolio_name,
            portfolio_id=user.portfolio.portfolioprice[-1].id,
            balance=user.portfolio.portfolioprice[-1].close_balance,
            time=str(user.portfolio.portfolioprice[-1].timestamp),

        )
        payload = dict(
            data=data
        )
        return payload


@api.route('/user/detailed')
class PortfolioPriceUserQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self):
        user = get_user()


        data = dict(
            user_id=user.id,
            portfolio_name=user.portfolio.portfolio_name,
            close_balance=user.portfolio.portfolioprice[-1].close_balance
        )
        payload = {user.portfolio.portfolioprice[-1].id: data}
        return payload
