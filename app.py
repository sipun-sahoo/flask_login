
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restx import Api,fields,Resource
import jwt
from datetime import datetime,timedelta
app=Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/newdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma=Marshmallow(app)
api=Api()
api.init_app(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True,autoincrement=True)
    name = db.Column(db.String(12))
    email = db.Column(db.String(22))
    password = db.Column(db.String(22))

class UserSchema(ma.Schema):
    class Meta:
        fields=('id','name','email','password')
model=api.model('demo',{
    'name':fields.String('name'),
    'email':fields.String('email'),
    'password':fields.String('password')
})


user_schema=UserSchema()
users_schema=UserSchema(many=True)

@api.route("/get/<name>")
class getdata(Resource):
    def get(self,name):
        
        #for all data.
        """data=User.query.all()
        return jsonify (users_schema.dump(data))"""

        #for single data
        """user = User.query.filter_by(id=id).first()
        e=user.id,user.name,user.email,user.password
        return jsonify ({"msg":e})"""
    
    
        user=User.query.filter(User.name.contains(name)).all()
        return jsonify (users_schema.dump(user))

    
    

       

@api.route("/signup")
class postdata(Resource):
    @api.expect(model)
    def post(self):
        user=User(name=request.json['name'],email=request.json['email'],password=request.json['password'])
        db.session.add(user)
        db.session.commit()
        return {'msg':"Register susccessfully"}



@api.route("/token_verify")
class postdata(Resource):
    @api.expect(model)
    def post(self):
        
        try:
            token = request.json['token']
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            return jsonify({"decode":data}) 
            
           
           
        except Exception as e:
            print(e)
            return "exception"






@api.route("/login")
class postdata(Resource):
    @api.expect(model)
    def post(self):
        payload=[]
        auth=request.json
        user = User.query.filter_by(name = auth.get('email')).first() and  User.query.filter_by(password = auth.get('password')).first()
        try:
            
            payload = jwt.encode({
                'id': user.id,
                'name' :user.name,
                'email':user.email,
                'password':user.password,
                'exp' : datetime.utcnow() + timedelta(hours=60)
                }, app.config['SECRET_KEY'],algorithm='HS256')
            return jsonify({"token":payload})
        except Exception as e:
            return jsonify({"msg":"please try to put correct email and password"})


@api.route("/put/<int:id>")
class putdata(Resource):
    @api.expect(model)
    def put(self,id):
        user=User.query.get(id)
        user.name=request.json['name']
        user.email=request.json['email']
        user.password=request.json['password']
        db.session.commit()
        return {'msg':"updated successfully"}

@api.route("/delete/<int:id>")
class deletedata(Resource):
    def delete(self,id):
        user=User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return {'msg':"deleted successfully"}



if __name__=='__main__':
    app.run(debug=True)