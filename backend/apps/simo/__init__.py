from flask_restful import Api
from apps.simo.views import boardlist,bladelist,getboardinfo,checkall,checkblade,upgradeall,upgradeone

def register_simo(app):
    api = Api(app)
    ####################清单下载的接口###################################################################
    api.add_resource(boardlist, '/api/getboardlist', endpoint="getboardlist")
    api.add_resource(bladelist, '/api/getbladelist', endpoint="getbladelist")
    api.add_resource(getboardinfo, '/api/getboardinfo', endpoint="getboardinfo")
    api.add_resource(checkall, '/api/checkall', endpoint="checkall")
    api.add_resource(checkblade, '/api/checkblade', endpoint="checkblade")
    
    api.add_resource(upgradeone, '/api/upgradeone', endpoint="upgradeone")
    api.add_resource(upgradeall, '/api/upgradeall', endpoint="upgradeall")