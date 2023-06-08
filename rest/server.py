import json
import os
import typing

import psycopg2
import uvicorn
import shutil
from fastapi import FastAPI, UploadFile, Query
from typing import List, Union
from typing_extensions import Annotated
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from fastapi import HTTPException
from fastapi.responses import JSONResponse, Response, FileResponse

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

    def get_users_info(self, user_ids):
        values = ', '.join(map(str, user_ids))
        cur = self.con.cursor()
        request = f"SELECT * FROM mafia.users WHERE id IN ({values})"
        cur.execute(request)
        result = cur.fetchall()
        json_result = {}
        json_result["users"] = []
        result_ids = []
        result = [] if result is None else result
        i = 0
        for value in result:
            json_result["users"].append(
                {"id": value[0]})
            if value[1] is not None:
                json_result["users"][i]["name"] = value[1]
            if value[2] is not None:
                json_result["users"][i]["avatar"] = value[2]
            if value[3] is not None:
                json_result["users"][i]["sex"] = value[3]
            if value[4] is not None:
                json_result["users"][i]["email"] = value[4]
            i += 1
            result_ids.append(value[0])
        if len(result_ids) != len(user_ids):
            raise Exception("Some users not found info")
        return json.dumps(json_result)

    def get_user_stats(self, user_id):
        cur = self.con.cursor()
        json_result = {}
        request = f"SELECT COUNT(*) FROM mafia.games WHERE id='{user_id}'"
        cur.execute(request)
        result = cur.fetchone()
        json_result["all_games"] = 0
        if result is not None:
            json_result["all_games"] = result[0]
        request = f"SELECT COUNT(*) FROM mafia.games WHERE id='{user_id}' AND winner=false"
        cur.execute(request)
        result = cur.fetchone()
        json_result["bad_games"] = 0
        if result is not None:
            json_result["bad_games"] = result[0]
        request = f"SELECT COUNT(*) FROM mafia.games WHERE id='{user_id}' AND winner=true"
        cur.execute(request)
        result = cur.fetchone()
        json_result["good_games"] = 0
        if result is not None:
            json_result["good_games"] = result[0]
        request = f"SELECT duration FROM mafia.games WHERE id='{user_id}'"
        cur.execute(request)
        result = cur.fetchall()
        if result is not None:
            sum_dur = 0
            for i in result:
                sum_dur += i[0]
            json_result["all_games_dur"] = sum_dur
        return json_result

    def add_user_info(self, user_id: str, user_name: typing.Optional[str], avatar: typing.Optional[str],
                      sex: typing.Optional[str], email: typing.Optional[str]):
        cur = self.con.cursor()
        request = f"SELECT * FROM mafia.users WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is not None:
            raise Exception("User has already added information, you can just edit it")
        request = f"SELECT * FROM mafia.users_ids WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("We do not have user with that id")
        cur = self.con.cursor()
        request = f"INSERT INTO mafia.users (id) VALUES ({user_id})"
        cur.execute(request)
        self.con.commit()
        if user_name is not None:
            request = f"UPDATE mafia.users SET user_name='{user_name}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()
        cur = self.con.cursor()
        if avatar is not None:
            request = f"UPDATE mafia.users SET image_url='{avatar}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()
        cur = self.con.cursor()
        if sex is not None:
            request = f"UPDATE mafia.users SET sex='{sex}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()
        cur = self.con.cursor()
        if email is not None:
            request = f"UPDATE mafia.users SET email='{email}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()

    def update_user_info(self, user_id: str, user_name: typing.Optional[str], avatar: typing.Optional[str],
                         sex: typing.Optional[str], email: typing.Optional[str]):
        cur = self.con.cursor()
        request = f"SELECT * FROM mafia.users_ids WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("We do not have user with that id")
        request = f"SELECT * FROM mafia.users WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("Non existed user info")
        if user_name is not None:
            request = f"UPDATE mafia.users SET user_name='{user_name}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()
        cur = self.con.cursor()
        if avatar is not None:
            request = f"UPDATE mafia.users SET image_url='{avatar}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()
        cur = self.con.cursor()
        if sex is not None:
            request = f"UPDATE mafia.users SET sex='{sex}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()
        cur = self.con.cursor()
        if email is not None:
            request = f"UPDATE mafia.users SET email='{email}' WHERE id={user_id}"
            cur.execute(request)
            self.con.commit()

    def delete_user_info(self, user_id: str):
        cur = self.con.cursor()
        request = f"SELECT * FROM mafia.users WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("Non existed user info")
        request = f"DELETE FROM mafia.users WHERE id = {user_id}"
        cur.execute(request)
        self.con.commit()

    def get_or_generate_pdf_name(self, user_id: str):
        cur = self.con.cursor()
        request = f"SELECT * FROM mafia.users WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("Non existed user")
        request = f"INSERT INTO mafia.user_pdf (id, pdf) VALUES ('{user_id}', 'pdf_{user_id}.pdf') ON CONFLICT (id) DO UPDATE SET pdf='pdf_{user_id}.pdf'"
        cur.execute(request)
        self.con.commit()
        return f'pdf_{user_id}.pdf'

    def get_pdf_name(self, user_id: str):
        cur = self.con.cursor()
        request = f"SELECT * FROM mafia.users WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("Non existed user")
        request = f"SELECT pdf FROM mafia.user_pdf WHERE id = {user_id}"
        cur.execute(request)
        result = cur.fetchone()
        if result is None:
            raise Exception("Non existed pdf")
        return result[0]



MAFIA_API = FastAPI()
manager = DataBaseManagemantSystem()


@MAFIA_API.post("/user")
def add_user_info(user_id: str, user_name: Union[str, None], avatar: Union[UploadFile, None],
                  sex: Union[str, None], email: Union[str, None]):
    try:
        if avatar is not None:
            with open(avatar.filename, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
        manager.add_user_info(user_id, user_name, avatar.filename if avatar is not None else None, sex, email)
        return JSONResponse(content=json.dumps(json.loads(manager.get_users_info([user_id]))["users"][0]))
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@MAFIA_API.get("/user")
def get_user_info(user_ids: Annotated[List[str], Query()]):
    try:
        return JSONResponse(content=manager.get_users_info(user_ids))
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@MAFIA_API.get("/stats")
async def get_user_stats(user_id: str):
    try:
        manager.get_or_generate_pdf_name(user_id)
        json_result = json.dumps({"pdf_url": f"/pdf/{user_id}"})
        return JSONResponse(content=json_result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


def generate_statistics_pdf(filename, user_id):
    player = None
    stats = None
    try:
        player = (json.loads(manager.get_users_info([user_id])))["users"][0]
        stats = manager.get_user_stats(user_id)
    except Exception as e:
        raise Exception("Cannot ger user or stats")
    pdf = canvas.Canvas(filename, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(52, 710, f"Name: {player['name']}")
    pdf.drawString(52, 650, f"Sex: {player['sex']}")
    pdf.drawString(52, 680, f"Email: {player['email']}")
    pdf.drawString(52, 620, f"All games: {stats['all_games']}")
    pdf.drawString(52, 590, f"Winer games: {stats['good_games']}")
    pdf.drawString(52, 560, f"Bad games: {stats['bad_games']}")
    pdf.drawString(52, 530, f"Seconds in game: {stats['all_games_dur']}")
    if os.path.isfile(player['avatar']):
        avatar_file = player['avatar']
        try:
            pdf.drawImage(avatar_file, 420, 500, 150, 150)
        except:
            pass
    pdf.save()

@MAFIA_API.get("/pdf/{user_id}")
async def get_user_stats_pdf(user_id: str):
    try:
        pdf_name = manager.get_pdf_name(user_id)
        generate_statistics_pdf(pdf_name, user_id)
        return FileResponse(path=pdf_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@MAFIA_API.put("/user")
def edit_user_info(user_id: str, user_name: Union[str, None], avatar: Union[UploadFile, None],
                   sex: Union[str, None], email: Union[str, None]):
    try:
        if avatar is not None:
            with open(avatar.filename, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
        manager.update_user_info(user_id, user_name, avatar.filename if avatar is not None else None, sex, email)
        return JSONResponse(content=json.dumps(json.loads(manager.get_users_info([user_id]))["users"][0]))
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@MAFIA_API.delete("/user")
def delete_user_info(user_id: str):
    try:
        manager.delete_user_info(user_id)
        return Response(status_code=200)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


if __name__ == "__main__":
    uvicorn.run(MAFIA_API, host="0.0.0.0", port=5050)
