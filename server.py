import datetime
import queue
import threading
from collections import defaultdict
from concurrent import futures
from random import shuffle

import grpc
import psycopg2
import os
import protos.my_pb2 as my_pb2
import protos.my_pb2_grpc as my_pb2_grpc

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

    def check_user_with_the_same_nickname_exists(self, user_id):
        cur = self.con.cursor()
        request = f"SELECT id FROM mafia.users_ids WHERE id={user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            return None
        return result[0]

    def add_users_nickname(self, nickname, user_id):
        cur = self.con.cursor()
        request = f"INSERT INTO mafia.users_ids (id, nickname) VALUES ('{user_id}', '{nickname}')"
        cur.execute(request)
        self.con.commit()

    def add_stats(self, user_id, game_name, winner, duration):
        cur = self.con.cursor()
        request = f"INSERT INTO mafia.games (id, game_name, winner, duration) VALUES ({user_id}, '{game_name}', {winner}, {duration})"
        cur.execute(request)
        self.con.commit()



class Person:
    def __init__(self, role=None, name=None):
        self.role = role
        self.name = name


class Game:
    def __init__(self):
        self.all_roles = ["mafia", "sherif", "civilian", "civilian"]
        shuffle(self.all_roles)
        self.cv = threading.Condition()
        self.notifications = {}
        self.id_to_info = defaultdict(Person)
        self.ready_counter = 0
        self.votes = {}
        self.end_game = False
        self.counter_killed_civilians = 0
        self.checked_role = None
        self.killed = None
        self.checked = None
        self.date_start = None


class Server(my_pb2_grpc.MafiaServerServicer):
    def __init__(self):
        self.games = defaultdict(Game)
        self.manager = DataBaseManagemantSystem()
        self.user_id = 0

    def ResultedPersonVote(self, session):
        max_votes = max(self.games[session].votes.values())
        for i in self.games[session].votes.keys():
            if self.games[session].votes[i] == max_votes:
                return i
        return None

    def GetConnectedPlayers(self, request, context):
        connected_players = []
        for i in self.games[request.session].id_to_info:
            if self.games[request.session].id_to_info[i].role != 'killed':
                connected_players.append(str(i))
        return my_pb2.ConnectedPlayersOnly(names=connected_players)

    def GetMafiaPlayers(self, request, context):
        connected_players = []
        for i in self.games[request.session].id_to_info:
            if self.games[request.session].id_to_info[i].role == 'mafia':
                connected_players.append(str(i))
        return my_pb2.ConnectedPlayersOnly(names=connected_players)


    def SetUserName(self, request, context):
        print("SET USER NAME")
        if self.manager.check_user_with_the_same_nickname_exists(request.name) is None:
            self.user_id += 1
            user_id = self.user_id
            self.manager.add_users_nickname(request.name, user_id)
        else:
            user_id = self.manager.check_user_with_the_same_nickname_exists(request.name)
        self.games[request.session].id_to_info[user_id].name = request.name
        connected_players = []
        print("SET USER NAME")
        for i in self.games[request.session].notifications:
            self.games[request.session].notifications[i].put((request.name, "CONNECT"))
            connected_players.append(self.games[request.session].id_to_info[i].name)
        self.games[request.session].notifications[user_id] = queue.Queue()
        print(connected_players)
        return my_pb2.ConnectedPlayers(names=connected_players, id=user_id)

    def GetNotifications(self, request, context):
        print("SUBSCRIBE")
        print(request.id)
        print(request.session)
        print(self.games[request.session].notifications)
        while True:
            if request.id not in self.games[request.session].notifications:
                continue
            first, second = self.games[request.session].notifications[request.id].get()
            print("SUBCRIBE2")
            if first == "DELETED":
                break
            yield my_pb2.NotificationsResponse(user_name=first, connected=(second == 'CONNECT'))

    def Disconnect(self, request, context):
        self.games[request.session].notifications[request.id].put((None, "DELETED"))
        del self.games[request.session].notifications[request.id]
        for elem in self.games[request.session].notifications:
            self.games[request.session].notifications[elem].put(
                (self.games[request.session].id_to_info[request.id].name, "DISCONNECT"))
        del self.games[request.session].id_to_info[request.id]
        return my_pb2.Empty()

    def SetReadyStatus(self, request, context):
        self.games[request.session].ready_counter += 1
        self.games[request.session].votes[request.id] = 0
        with self.games[request.session].cv:
            while self.games[request.session].ready_counter % 4 != 0:
                self.games[request.session].cv.wait()
            role = self.games[request.session].all_roles.pop()
            self.games[request.session].id_to_info[request.id].role = role
            self.games[request.session].cv.notify()
        self.games[request.session].date_start = datetime.datetime.now()
        return my_pb2.ReadyResponse(role=role,
                                    players=[elem.name for elem in self.games[request.session].id_to_info.values()],
                                    ids=self.games[request.session].id_to_info.keys())

    def EndDay(self, request, context):
        self.games[request.session].checked_role = None
        self.games[request.session].killed = None
        self.games[request.session].ready_counter += 1
        with self.games[request.session].cv:
            while self.games[request.session].ready_counter % 4 != 0:
                self.games[request.session].cv.wait()
            self.games[request.session].cv.notify_all()
        if self.games[request.session].id_to_info[self.ResultedPersonVote(request.session)].role == "mafia":
            duration = int((datetime.datetime.now() - self.games[request.session].date_start).total_seconds())
            self.manager.add_stats(request.id, request.session, self.games[request.session].id_to_info[request.id].role != 'mafia', duration)
            return my_pb2.EndDayResponse(killed=self.ResultedPersonVote(request.session), end_game=True)
        self.games[request.session].id_to_info[self.ResultedPersonVote(request.session)].role = "killed"
        return my_pb2.EndDayResponse(killed=self.ResultedPersonVote(request.session), end_game=False)

    def KillPlayerVote(self, request, context):
        self.games[request.session].votes[request.id] += 1
        return my_pb2.Empty()

    def SkipNight(self, request, context):
        self.games[request.session].ready_counter += 1
        with self.games[request.session].cv:
            while self.games[request.session].ready_counter % 4 != 0:
                self.games[request.session].cv.wait()
            self.games[request.session].cv.notify_all()
        return my_pb2.EndNightResponse(killed=self.games[request.session].killed,
                                       checked_role=self.games[request.session].checked_role,
                                       checked=self.games[request.session].checked,
                                       end_game=self.games[request.session].end_game)

    def KillPlayerMafia(self, request, context):
        self.games[request.session].ready_counter += 1
        self.games[request.session].killed = request.id
        self.games[request.session].id_to_info[request.id].role = "killed"
        counter = 0
        for elem in self.games[request.session].id_to_info.values():
            if elem.role == "civilian" or elem.role == "sherif":
                counter += 1
        if counter <= 1:
            self.games[request.session].end_game = True
        print("killl")
        print(self.games[request.session].ready_counter)
        with self.games[request.session].cv:
            while self.games[request.session].ready_counter % 4 != 0:
                self.games[request.session].cv.wait()
            self.games[request.session].cv.notify_all()
        print('returned mafia')
        if self.games[request.session].end_game:
            duration = int((datetime.datetime.now() - self.games[request.session].date_start).total_seconds())
            for key, elem in self.games[request.session].id_to_info.items():
                self.manager.add_stats(key, request.session, elem.role == 'mafia', duration)
        return my_pb2.EndNightResponse(killed=self.games[request.session].killed,
                                       checked_role=self.games[request.session].checked_role,
                                       checked=self.games[request.session].checked,
                                       end_game=self.games[request.session].end_game)

    def CheckPlayer(self, request, context):
        self.games[request.session].ready_counter += 1
        self.games[request.session].checked_role = self.games[request.session].id_to_info[request.id].role
        self.games[request.session].checked = request.id
        with self.games[request.session].cv:
            while self.games[request.session].ready_counter % 4 != 0:
                self.games[request.session].cv.wait()
            self.games[request.session].cv.notify_all()
        print('returned sheriff')
        return my_pb2.EndNightResponse(killed=self.games[request.session].killed,
                                       checked_role=self.games[request.session].checked_role,
                                       checked=self.games[request.session].checked,
                                       end_game=self.games[request.session].end_game)


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    my_pb2_grpc.add_MafiaServerServicer_to_server(Server(), server)
    listen_addr = '0.0.0.0:8080'
    server.add_insecure_port(listen_addr)
    server.start()
    server.wait_for_termination()
