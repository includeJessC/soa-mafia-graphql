import os

import psycopg2
import grpc
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from fastapi import FastAPI
from graphene import Int, Boolean
from graphene import ObjectType, List, String, Mutation, Schema, Field
import uvicorn

from protos import my_pb2
from protos import my_pb2_grpc

stub = None

username = os.environ.get("DB_USER")
db_name = os.environ.get("DB_NAME")
us_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")


class DataBaseManagemantSystem:
    def __init__(self):
        self.con = psycopg2.connect(
            database=db_name,
            user=username,
            password=us_password,
            host='postgres',
        )
        self.cur = self.con.cursor()

    def __del__(self):
        self.con.close()

    def add_comment_and_get(self, session_name, user_id, comment):
        cur = self.con.cursor()
        request = f"INSERT INTO mafia.games_comments (id, game_name, comment) VALUES ({user_id}, '{session_name}', '{comment}')"
        cur.execute(request)
        self.con.commit()
        cur = self.con.cursor()
        request = f"SELECT comment FROM mafia.games_comments WHERE game_name='{session_name}'"
        cur.execute(request)
        result = cur.fetchall()
        comments = []
        if result is not None:
            for i in result:
                comments.append(i[0])
        return comments


manager = DataBaseManagemantSystem()


class Player(ObjectType):
    user_id = Int()
    name = String()
    role = String()


class Scoreboard(ObjectType):
    is_ended = Boolean()
    is_mafia_win = Boolean()
    players = List(Player)


class Query(ObjectType):
    current_games = List(Int)
    past_games = List(Int)
    scoreboard = Field(Scoreboard, session_name=String())
    def resolve_get_current_games(self, info):
        print("Get all games")
        try:
            return stub.GetActiveGames(my_pb2.Empty()).sessions
        except:
            return []

    def resolve_get_past_games(self, info):
        print("Print games")
        try:
            return stub.GetPastGames(my_pb2.Empty()).sessions
        except:
            return []

    def resolve_get_scoreboard(self, info, session_name):
        response = stub.GetScoreboard(my_pb2.SessionName(session=session_name))
        return {"session_name": session_name, "is_ended": response.is_ended, "is_mafia_win": response.is_is_mafia_win,
                "players": [{"user_id": elem.id, "name": elem.name, "role": elem.role} for elem in response.players]}


class AddComment(Mutation):
    class Arguments:
        user_id = Int()
        session_name = String(required=True)
        comment = String(required=True)
    comments = List(String)

    def mutate(self, info, user_id, session_name, comment):
        comments = manager.add_comment_and_get(user_id, session_name, comment)
        return AddComment(comments=comments)


class CommentMutation(ObjectType):
  add_comment = AddComment.Field()

schema = Schema(query=Query, mutation=CommentMutation)

gapp = GraphQLApp(
  schema=schema, on_get=make_graphiql_handler())

app = FastAPI()
app.add_route("/", gapp
)

if __name__ == "__main__":
    while stub is None:
        try:
            grpc_channel = grpc.insecure_channel('server:8080')
            stub = my_pb2_grpc.MafiaServerStub(grpc_channel)
            stub.GetConnectedPlayers(my_pb2.SessionName(session=''))
        except:
            print("cannot connect")
            stub = None
            pass
    uvicorn.run(app, host="0.0.0.0", port=9095)
