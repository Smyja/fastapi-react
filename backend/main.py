from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette import status
from fastapi import status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
import json
import time
from typing import Optional
from datetime import datetime, date
from starlette.exceptions import HTTPException
from fastapi import BackgroundTasks
from storage.db import db
from utils.utils import user_rooms
from utils.emails import *
from storage.models import *
import requests

app = FastAPI(
    title="Noticeboard API",
    description="Swagger Documentaion For the Noticeboard Plugin",
)

templates = Jinja2Templates(directory="frontend/")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings_PLUGIN_ID = "61694eea9ea5d3be97df2973"

@app.get("/", status_code=201)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get(
    "/api/v1/sidebar",
    summary="Returns Sidebar Data",
    tags=["Sidebar"],
)
def sidebar_info(org_id: str, user_id: str):
    """Returns the room the logged in user belongs to under Noticeboard
    plugin"""

    if org_id and user_id:
        sidebar = {
            "name": "Noticeboard Plugin",
            "description": "Displays Information On A Noticeboard",
            "plugin_id": settings_PLUGIN_ID,
            "organisation_id": f"{org_id}",
            "user_id": f"{user_id}",
            "category": "productivity",
            "group_name": "Noticeboard",
            "show_group": False,
            "public_rooms": [],
            "joined_rooms": user_rooms(org_id, user_id),
        }
        return JSONResponse(sidebar)
    return JSONResponse(
        {"message": "org id or user id is None"}, status_code=status.HTTP_400_BAD_REQUEST
    )

def create_plugin_room(org_id: str, user_id: str):
    """Function that creates a Noticeboard room"""
    room = db.read("noticeboard_room", org_id)
    if room["status"] == 200:
        if room["data"] is not None:
            room = room["data"][0]
        else:
            serializer = NoticeboardRoom(room_name="Noticeboard")
            room = serializer.dict()
            room.update({"is_admin": user_id})
            if user_id not in room["room_member_id"]:
                room.update({"room_member_id": [user_id]})
                db.save("noticeboard_room", org_id, notice_data=room)


@app.post(
    "/api/v1/install",
    tags=["Install"],
    summary="Install Noticeboard Plugin",
    status_code=200,
)
async def install_plugin(request: Request, install: InstallPlugin):
    """This endpoint is called when an organisation wants to install the
    Noticeboard plugin for their workspace."""

    serializer = install.dict()
    nHeaders = request.headers["Authorization"]
    
    install_payload = serializer
    org_id = install_payload["organisation_id"]
    user_id = install_payload["user_id"]
    print(org_id, user_id)

        # new_token = db.token()
        # print(new_token)

    url = f"https://api.zuri.chat/organizations/{org_id}/plugins"
    print(url)
    payload = {"plugin_id": settings_PLUGIN_ID, "user_id": user_id}
    v2load = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"{nHeaders}"}
    print(headers)
    response = requests.request("POST", url, headers=headers, data=v2load)
    installed = json.loads(response.text)
    print(installed)
    if installed["status"] == 200:

        create_plugin_room(org_id, user_id)

        return JSONResponse(
            {
                "success": True,
                "data": {"redirect_url": "/noticeboard"},
                "message": "sucessfully retrieved",
            }
        )
    return JSONResponse(
        {
            "success":False,
            "message":"Plugin has already been added",
        }
    )


@app.delete(
    "/api/v1/uninstall",
    summary="Uninstall Noticeboard Plugin",
    tags=["Uninstall"],
)
def uninstall_plugin(uninstall: UninstallPlugin):
    """This endpoint is called when an organisation wants to uinstall the
    Noticeboard plugin for their workspace."""
    serializer = uninstall.dict()
    uninstall_payload = serializer
    org_id = uninstall_payload["organisation_id"]
    user_id = uninstall_payload["user_id"]
    print(user_id)

    new_token = db.token()
    print(new_token)

    url = (
        f"https://api.zuri.chat/organizations/{org_id}/plugins/{settings_PLUGIN_ID}"
    )
    print(url)
    payload = {"user_id": user_id}
    v2load = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {new_token}"}
    response = requests.request("DELETE", url, headers=headers, data=v2load)
    uninstalled = json.loads(response.text)
    print(uninstalled)
    if uninstalled["status"] == 200:
        return JSONResponse(
            uninstalled,
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "Plugin does not exist"}, status_code=status.HTTP_404_NOT_FOUND
    )

@app.post(
    "/api/v1/organisation/{org_id}/user/{user_id}/room",
    tags=["Room"],
    summary="Create Noticeboard Room",
)
async def create_noticeboard_room(org_id: str, user_id: str, notice_room: NoticeboardRoom):
    """Creates a room for the organisation under Noticeboard plugin."""
    
    room = db.read("noticeboard_room", org_id)
    if room["status"] == 200:
        if room["data"] is not None:
            room = room["data"][0]
            return JSONResponse(
                {"message": "room already exists", "data": room}, status_code=status.HTTP_200_OK
            )
        else:
            serializer = jsonable_encoder(notice_room)
            room = serializer
            room.update({"is_admin": user_id})
            if user_id not in room["room_member_id"]:
                room.update({"room_member_id": [user_id]})
                db.save("noticeboard_room", org_id, notice_data=room)
            return JSONResponse(
                {"message": "successfully created your room", "data": room},
                status_code=status.HTTP_201_CREATED,
            )
    return JSONResponse(
        {"message": "room couldn't be created"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.get(
    "/api/v1/organisation/{org_id}/get-room",
    tags=["Room"],
    summary="List Noticeboard Room",
    status_code=200,
)
def get_room(org_id: str):
    """Gets all the rooms created under the Noticeboard plugin."""
    data = db.read("noticeboard_room", org_id)
    if data["data"] is None:
        data["data"] = {}
    return JSONResponse(data)

@app.delete(
    "/api/v1/organisation/{org_id}/room/{obj_id}/delete",
    tags=["Room"],
    summary="Delete Noticeboard Room",
)
def delete_room(org_id: str, obj_id: str):
    """This endpoint enables a user delete a room."""
    deleted_room = db.delete(org_id, "noticeboard_room", obj_id)

    if deleted_room["status"] == 200:
        return JSONResponse(
            {"message": "successfully deleted room"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "could not delete room"},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.post(
    "/api/v1/organisation/{org_id}/create",
    response_model=CreateNotice,
    summary="Creates Notices",
    tags=["Notices"],
    status_code=201,
)
async def create_notice_view(org_id: str, notices: CreateNotice):
    """
    This endpoint is used to creates notices for organisations
    """
    notice = jsonable_encoder(notices)

    db.save(
        "noticeboard",
        org_id,
        notice_data=notice,
    )
    updated_data = db.read("noticeboard", org_id)


    return JSONResponse({
        "success":True,
        "data":notice,
        "message":"successfully created"
    })


@app.get(
    "/api/v1/organisation/{org_id}/notices", summary="List of Notices", tags=["Notices"]
)
async def view_notice(org_id: str, response: Response):

    """This endpoint returns all the notices created under a particular
    organisation in the database."""

    # org_id = "613a1a3b59842c7444fb0220"
    notice = db.read("noticeboard", org_id)
    get_data = notice["data"] or {}
    reversed_list = get_data[::-1]
    # print(reversed_list)
    notice.update(data=reversed_list)
    if notice["status"] == 200:
        # print(notice)
        return JSONResponse({
            "success": True,
            "data": notice["data"],
            "message": "retrieved successfully"
        }, status_code=status.HTTP_200_OK)
    return JSONResponse(
        {"status": False, "message": "retrieved unsuccessfully"},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.delete(
    "/api/v1/organisation/{org_id}/notices/{object_id}/delete",
    summary="Delete Notices",
    tags=["Notices"],
)
def delete_notice(object_id: str, org_id: str, response: Response):
    """Delete a notice from the database."""
    deleted_data = db.delete(
        collection_name="noticeboard", org_id=org_id, object_id=object_id
    )
    data = db.read("noticeboard", org_id)

    db.post_to_centrifugo("team-aquinas-zuri-challenge-007", data)

    if deleted_data["status"] == 200:
        return JSONResponse(
            {"success": True, "message": "Delete Operation Successful"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {
            "success": False,
            "message": "Delete Operation Failed. Object does not exist in the database",
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )

@app.patch(
    "/api/v1/organisation/{org_id}/notices/{object_id}/edit",
    response_model=UpdateNotice,
    response_model_exclude_none=True,
    summary="Updates Notices",
    tags=["Notices"],
    status_code=201,
)
async def update_notice_view(request: Request,object_id:str, org_id:str,notices: UpdateNotice):
    """Update A Notice In A Database."""

    notice= notices.dict(exclude_unset=True)
    #61767acbbc003777d000a92a

    # print("w"*50)
    # print(notice)
    updated = db.update("noticeboard", org_id, notice, object_id=object_id)
    if updated["status"]==200:

        return JSONResponse(
            {
                "success": True,
                "data": notice,
                "message": "Notice has been successfully updated",
            },
            status_code=status.HTTP_201_CREATED,
        )
    return JSONResponse(
    {"success": False, "message": "Notice not updated, Please Try Again"},
    status_code=status.HTTP_400_BAD_REQUEST,)

@app.get(
    "/api/v1/organisation/{org_id}/user/{user_id}/bookmark",
    summary="List Bookmarked Notices",
    tags=["Bookmark"],
)
def bookmark_notice(org_id: str, user_id: str):
    """Retrieve all the notices a particular user has bookmarked."""
    bookmarked_notices = db.read(
        "bookmark_notice", org_id, filter={"user_id": user_id}
    )
    if bookmarked_notices["status"] == 200:
        return JSONResponse(
            {
                "success":True,
                "data":bookmarked_notices["data"] or {},
                "message":"Notices successfully retrieved"
            }, 
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        {
            "success":False,
            "message": "Notice does not exist"
        }, 
        status_code=status.HTTP_404_NOT_FOUND
    )

@app.post(
    "/api/v1/organisation/{org_id}/bookmark",
    tags=["Bookmark"],
    summary="Bookmark A Notice",
    status_code=201,
)
def create_bookmark(org_id: str, notice: BookmarkNotice):
    """This endpoint enables a user to bookmark a notice."""
    serializer = notice.dict()
    bookmarked_data = db.save("bookmark_notice", org_id, serializer)

    return JSONResponse({
        "success":True,
        "data":serializer,
        "message":"successfully bookmarked"
    })

@app.delete(
    "/api/v1/organisation/{org_id}/bookmark/{obj_id}/delete",
    tags=["Bookmark"],
    summary="Delete A Bookmarked Notice"
)
def delete_bookmarked_notice(org_id: str, obj_id: str):
    """This endpoint enables a user delete a bookmarked notice."""
    bookmarked_notice = db.delete(org_id, "bookmark_notice", obj_id)

    if bookmarked_notice["status"] == 200:
        return JSONResponse(
            {"message": "successfully deleted bookmarked notice"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "could not delete bookmarked notice"},
        status_code=status.HTTP_404_NOT_FOUND,
    )

@app.post(
    "/api/v1/organisation/{org_id}/create_draft",
    tags=["Notices"],
    summary="Draft Of A Notice",
    status_code=201,
)
def notice_draft(org_id: str, notice_draft: NoticeDraft):
    """For creating Drafts for A Notice."""
    serializer = jsonable_encoder(notice_draft)
    draft = db.save("noticeboard", org_id, notice_data=serializer)
    return JSONResponse({
        "success":True,
        "data":serializer,
        "message":"successfully drafted"
    })

@app.get(
    "/api/v1/organisation/email-notification",
    tags=['Email'],
    summary="Sends Email To Subscribers",
)
def email_notification(org: str, sendemail: str):
    """
    This endpoint is used to send email notifications to subscribed users
    when new notices are published.
    """

    if org and sendemail == "true":
        response_subscribers = db.read("email_subscribers", org)

        if response_subscribers["status"] == 200 and response_subscribers["data"]:
            email_subscribers = response_subscribers["data"]

            # email sending setup
            url = "https://api.zuri.chat/external/send-mail?custom_mail=1"

            for user in email_subscribers:
                email = user["email"]
                payload = {
                    "email": email,
                    "subject": "notice",
                    "content_type": "text/html",
                    "mail_body": '<div style="background-color: chocolate; width: 100%; height: 50%;"><h1 style="color: white; text-align: center; padding: 1em">Noticeboard Plugin</h2></div><div style="margin: 0% 5% 10% 5%;"><h2>New Notice</h2><p>Hey!</p><br><p>You have a new notice!</p><p>Visit <a href="https://zuri.chat/">zuri chat</a> to view notice.</p><br><p>Cheers,</p><p>Noticeboard Plugin</p></div>',
                }
                requests.post(url=url, json=payload)

            return JSONResponse(
                {"status": "emails sent successfully"},
                status_code=status.HTTP_200_OK,
            )
        return JSONResponse(
            {"error": response_subscribers["message"]},
            status_code=response_subscribers["status"],
        )

    return JSONResponse(
        {
            "status": "no emails sent, check if org is not null or if send has a boolean value of true"
        }
    )

@app.post(
    "/api/v1/organisation/email-subscription",
    tags=['Email'],
    summary="Enable Users Subscribe"
)
async def email_subscription(org: str, user: str, subscribe: EmailSubscribe):
    """
    This endpoint is used to allow users subscribe to receiving email
    notifications when new notices are published.
    """

    if org and user:  # and user_id
        serializer = subscribe.dict()
        user_email = serializer["email"]
        user_data = {"user_id": user, "email": user_email}

        response_subscribers = db.read("email_subscribers", org)

        if response_subscribers["status"] == 200 and response_subscribers["data"]:
            for user_obj in response_subscribers["data"]:
                if user == user_obj["user_id"]:
                    return JSONResponse(
                        {"status": "already subscribed"},
                        status_code=status.HTTP_409_CONFLICT,
                    )

            # if user_id doesn't exist, then the user is subscribed
            db.save("email_subscribers", org, user_data)
            subscription_success_mail(email=user_email)
            return JSONResponse(
                {"status": "subscription successful", "data": user_data},
                status_code=status.HTTP_201_CREATED,
            )

        return JSONResponse(
            {"status": response_subscribers["message"]},
            status_code=response_subscribers["status"],
        )

    return JSONResponse(
        {"status": "no action taken, check org and/or user parameter values"}
    )

@app.post(
    "/api/v1/organisation/{org_id}/room/{room_id}/members/{member_id}",
    tags=["Room"],
    summary="Add Members To Room",
)
async def add_users_to_room(org_id: str, room_id: str, member_id: str, room_members: AddMemberToRoom):
    """
    This endpoint enables a user to be added to a room
    """
    serializer = room_members.dict()
    room_id = serializer["room_id"]
    member_ids = serializer["member_ids"]
    room = db.read("noticeboard_room", org_id, filter={"room_id": room_id})
    if room["status"] == 200:
        user_room = room["data"][0]
        room_members = user_room["room_member_id"]
        for member_id in member_ids:
            if member_id not in room_members:
                room_members.append(member_id)
                user_room.update({"room_member_id": room_members})
                new_data = user_room
                db.update(
                    "noticeboard_room",
                    org_id,
                    {"room_member_id": new_data["room_member_id"]},
                    user_room["_id"],
                )

        return JSONResponse(
            {"message": "successfully added", "data": user_room},
            status_code=status.HTTP_201_CREATED,
        )
    return JSONResponse(
        {"message": "could not be added"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.patch(
    "/api/v1/organisation/{org_id}/room/{room_id}/members/{member_id}",
    tags=["Room"],
    summary="Remove Members From Room",
)
async def patch(org_id: str, room_id: str, member_id: str, room_members: AddMemberToRoom):
    """
    This endpoint enables a user to be removed from a room
    """
    serializer = room_members.dict()
    room_id = serializer["room_id"]
    member_ids = serializer["member_ids"]
    room = db.read("noticeboard_room", org_id, filter={"room_id": room_id})
    if room["status"] == 200:
        user_room = room["data"][0] 
        room_members = user_room["room_member_id"]
        for member_id in member_ids:
            if member_id in room_members:
                room_members.remove(member_id)
                user_room.update({"room_member_id": room_members})
                new_data = user_room
                db.update(
                    "noticeboard_room",
                    org_id,
                    {"room_member_id": new_data["room_member_id"]},
                    user_room["_id"],
                )

        return JSONResponse(
            {"message": "successfully removed", "data": user_room},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "could not be removed"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.get(
    "/api/v1/search-suggestions/{org_id}",
    tags=['Search'],
    summary='Returns Search Suggestion',
)
async def search_suggestions(org_id: str):
    """Returns search suggestion"""

    notices = db.read("noticeboard", org_id)["data"]

    data = {}

    try:
        for notice in notices:
            data[notice["message"]] = notice["message"]

        return Response(
            {
                "status": "ok",
                "type": "suggestions",
                "total_count": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(e)
        return Response(
            {
                "status": "ok",
                "type": "suggestions",
                "total_count": len(data),
                "data": data,
            }
        )

@app.get(
    "/api/v1/organisation/{org_id}/attachfile",
    tags=['Files'],
    summary="List Attached Files",
)
def get_attached_file(org_id: str):
    """This endpoint is a send message endpoint that can take files, upload
    them and return the urls to the uploaded files to the media list in the
    message serializer This endpoint uses form data The file must be passed in
    with the key "file"."""

    notice = db.read("noticeboard", org_id)
    get_data = notice["data"]
    reversed_list = get_data[::-1]
    print(reversed_list)
    notice.update(data=reversed_list)
    if notice["status"] == 200:
        print(notice)
        return JSONResponse(
            {
                "success":True,
                "data": notice["data"],
                "message": "successfully retrieved"
            }, 
            status_code=status.HTTP_200_OK)
    return JSONResponse(
        {"status": False, "message": "retrieved unsuccessfully"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.post(
    "/api/v1/organisation/{org_id}/attachfile",
    tags=['Files'],
    summary="Send Files",
)
async def send_files(request: Request, org_id: str):
    file_urls = []
    files = request.FILES.getlist("file")

    token = request.META.get("HTTP_AUTHORIZATION")
    if request.FILES and len(files) == 1:
        for file in request.FILES.getlist("file"):
            file_data = db.upload(file=file, token=token)
            if file_data["status"] == 200:
                for datum in file_data["data"]["files_info"]:
                    file_urls.append(datum["file_url"])
                return JSONResponse(file_data)
            return JSONResponse(file_data)
    return JSONResponse({"success": False, "message": "No file has been attached"})

@app.post(
    "/api/v1/organisation/{org_id}/schedule",
    response_model=ScheduleNotice,
    summary="Schedules Notices",
    tags=["Notices"],
    status_code=200,
)
async def schedule_notice(org_id: str, notices: ScheduleNotice,background_tasks: BackgroundTasks):
    """
    This endpoint is used to schedule notices for organisations
    """
    notice_dict = notices.dict()

    get_timer = notice_dict["timer"]
    time_format="%Y-%m-%d %H:%M:%S"
    formatted_time=get_timer.strftime(time_format)

    print(get_timer)
    remove_timer=notice_dict.pop("timer")
    print(notice_dict)
    now = datetime.now()
    timer = datetime.strptime(formatted_time, "%Y-%m-%d %H:%M:%S")
    
    duration = timer - now
    duration = duration.total_seconds()

    def background_duration():
        "A function for the background duration"
        time.sleep(duration)
        print("Duration reached, Now Sending notice")
        return True

    def db_save():
        "A function for background save to db"
        db.save(
            "noticeboard",
            org_id,
            notice_data=notice_dict,
        )
        print("Saved to db")
        return True
    background_tasks.add_task(background_duration)
    background_tasks.add_task(db_save)
    updated_data = db.read("noticeboard", org_id)

    return JSONResponse({
        "success":True,
        "data":jsonable_encoder(notice_dict),
        "message":"successfully created"
    })

