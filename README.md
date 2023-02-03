# Let's Chat
"Let's Chat" is a real-time chat website.


## Some of The "Let's Chat" Features:
- Login with third-party (Google or GitHub) account
- Send, accept and cancel friend requests
- Have private chat room with friends
- See the friends status in real-time (online or offline)
- Chat in public chat room
- Get real-time notifications


## The Challenges I Solved In This Project

### Preventing users from having unlimited websocket connections
when I realized that I can open countless websocket connections to the app, It was obvious that the application is vulnerable for DOS attacks. So I tracked the number of each user's connections and closed the oldest one whenever it exceeded the limit.

### Sending real-time notifications
The simple way to solve this problem is to make the client side to request new notifications at specific intervals (ex: for each 4 second). But as you know it's not so efficient and for this reason I send notifications through websocket connections whenever and wherever I create them.

### Keeping track of online users
I could use database to save and update users status but the performance wouldn't be so good and beacuse of that I used python defaultdict to store users status in RAM.

## Prerequisites
You just need to have **Docker** and **Docker Compose** (to be more persice I used Docker Compose version v2.13.0) installed on your system.

## Run Project
Run project containers with Docker Compose by entering this command in your terminal:

    docker compose up -d

> **_NOTE:_** if you want to see logs then remove "-d" flag.

Now that the server’s running, visit http://127.0.0.1:8000/ or localhost:8000 with your web browser. You’ll see index page of "let's Chat".

But before doing anything else you should create a super user. So first connect to the django or web container's bash:

    docker container exec -it letschat-web-1 bash

run following command in opened bash:

    python manage.py createsuperuser

then enter username, password and ... for creating a super user.


## Run Tests
After running docker containers enter below command in your terminal to connect to the web container's bash:

    docker container exec -it letschat-web-1 bash

Then run test with:

    pytest

## What did I used in this project
### Backend:
- Postgresql
- Redis
- Djagno
    - django-allauth
    - Django Channels
    - Django Debug Toolbar
    - django-crispy-forms
    - ...

### Frontend:
- javascript
- Bootstrap



