# Authentication implementation:
### access token lifetime : 7days
### refresh token lifetime : 30 days

## New user: 
- 1st register to the app - aiming to add the user to the db
- 2nd login  - aiming to get the access and refresh tokens

_The use must register then return to login screen inorder to logon the app getting the needed tokens, this behavior could be change if needed_ 

## Old user:
- 2nd login only - aiming to get the access and refresh tokens

* * *
# API Routes
## registration : https://ai-personal-trainer.onrender.com/api/auth/register/
### req type: POST
### req body: 
```
{
    "username":"<full name>",
    "email":"<email>",
    "password":"<pass>" 
}
```   
### req headers:
- content-type: application/json

* * *
## login : https://ai-personal-trainer.onrender.com/api/auth/login/
### req type: POST
### req body: 
```
{
    "username":"<name>",
    "password":"<password>" 
}
```   
### req headers:
- content-type: application/json
### res obj:
```
{
    "username": "<name>",
    "access_token":"token",
    "refresh_token":"token"
}

```

### _Note:_
**_Both tokens must be stored in order to use the app_**

* * *
## logout : https://ai-personal-trainer.onrender.com/api/auth/logout/
### req type: POST
### req body: 
```
{
    "refresh":"<user's refresh token>"
}
```   
### req headers:
- Content-Type: application/json
- Authorization:'Bearer <user's access token> 
### res code: 204
* * *
## refresh : https://ai-personal-trainer.onrender.com/api/auth/token/refresh/
### req type: POST
### req body: 
```
{
    "refresh":"<user's refresh token>"
}
```   
### req headers:
- Content-Type: application/json
- Authorization:'Bearer <user's access token> 
### res obj:
```
{
    "username": "<name>",
    "access_token":"token",
    "refresh_token":"token"
}
```
### _Notes:_
- **_Both tokens must be stored in order to use the app_**
- **_This request is used to refresh the tokens_**

* * *
## Get all exercises : https://ai-personal-trainer.onrender.com/exercises/list/
### req type: GET
### req headers:
- Content-Type: application/json
- Authorization:'Bearer <user's access token> 
### res obj:
```
{
	"excercises": [
        {
            "id": <int>,
            "name": "<name>",
            "instructions": "<str>",
            "targeted_muscles": "<str>",
            "groupID": <int>,
            "groupName": "<name>"
        },
		
		]
}
```

* * *
## Get exercise by id : https://ai-personal-trainer.onrender.com/exercises/exercise/```<int:id>```/
### req type: GET
### req headers:
- Content-Type: application/json
- Authorization:'Bearer <user's access token> 
### res obj:
```

        {
            "id": <int>,
            "name": "<name>",
            "instructions": "<str>",
            "targeted_muscles": "<str>",
            "groupID": <int>,
            "groupName": "<name>"
        }
```

* * *
## Start streaming session : https://ai-personal-trainer.onrender.com/stream/sessions/start/
### req type: GET
### req headers:
- Content-Type: application/json
- Authorization:'Bearer <user's access token> 
### res obj:
```
{
    "session_id": "<uuid:session>",
    "message": "Session started"
}
```
### _Notes:_
- **_session id must be used to connect to server socket_**
- **_Once the socket is closed the session will be killed_**

* * *
# Testing Routes
## End streaming session : https://ai-personal-trainer.onrender.com/stream/sessions/end/
### req type: GET
### req body: 
```
{
		"session_id": "<uuid:session>"
}
```   
### req headers:
- content-type: application/json
- Authorization:'Bearer <user's access token> 
* * *
## Get all streaming sessions : https://ai-personal-trainer.onrender.com/stream/sessions/active/
### req type: GET
### req headers:
- Content-Type: application/json
### res obj:
```
{	 "sessions": [
						{
							"session_id": "<uuid:session>",
							"message": "Session started"
						},
				]
}
```
* * *
# Admin Dashboard 
### Following the link : https://ai-personal-trainer.onrender.com/admin
### Note:
- This dashboard is used as content management system where the admin could add users accounts and any other data needed 

* * * 