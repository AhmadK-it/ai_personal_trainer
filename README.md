# Authentication implementation:

### access token lifetime : 7days

### refresh token lifetime : 30 days

## New user:

- 1st register to the app - aiming to add the user to the db
- 2nd login  - aiming to get the access and refresh tokens

_The use must register then return to login screen inorder to logon the app getting the needed tokens, this behavior could be change if needed_

## Old user:

- 2nd login only - aiming to get the access and refresh tokens

---

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

---

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

---

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

---

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

---

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

---

## Get exercise by id : https://ai-personal-trainer.onrender.com/exercises/exercise/``<int:id>``/

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

---

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


---

## User's Profile fields & options :

### Fields 

```
{
    age = IntegerField | null | blank
    gender = CharField | null | blank
    weight = FloatField | null | blank  # kg
    height = FloatField | null | blank  # cm
    body_fat = FloatField | null | blank # percentage
    goal = CharField | null | blank
    lifestyle_intensity = CharField | null | blank
    recommended_calories = FloatField | null | blank
    weakness_points = CharField | blank | null
    experience_level = CharField | blank | null
}
```
### Options 

```
{
	WEAKNESS_CHOICES = [
        'No',
        'Shoulder',
        'Knee',
        'Hips',
        'Lower Back',
        'Elbow',
        'Wrist',
        'Ankle',
        'Neck',
    ]
    EXPERIENCE_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE_ADVANCED', 'Intermediate & Advanced'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
    ]

    LIFESTYLE_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('moderate', 'Moderate'),
        ('intensive', 'Intensive'),
    ]    
}
```
_No Other Option will be passed_
_For Weakness Points it must be a string with each optin sperated with ","_

---

## View User's Profile : https://ai-personal-trainer.onrender.com/api/auth/profile/

### req type: GET

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### res obj:
### res code: 200 

```
{
    "msg": "User's profile found:",
    "data": {
        "age": 29,
        "gender": "male",
        "weight": 100.0,
        "height": 178.0,
        "body_fat": 19.5,
        "goal": "weight_loss",
        "lifestyle_intensity": "moderate",
        "recommended_calories": 2000.0,
        "weakness_points": "Shoulder,Knee,Lower Back",
        "experience_level": "INTERMEDIATE_ADVANCED"
    }
}
```

---

## Create User's Profile : https://ai-personal-trainer.onrender.com/api/auth/profile/

### req type: POST

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### request obj:

```
{
    "profile": {
        "age": 29,
        "gender": "male",
        "weight": 100.0,
        "height": 178.0,
        "body_fat": 19.5,
        "goal": "weight_loss",
        "lifestyle_intensity": "moderate",
        "recommended_calories": 2000.0,
        "weakness_points": "Shoulder,Knee,Lower Back",
        "experience_level": "INTERMEDIATE_ADVANCED"
    }
}
```


### response obj:
### response code 201
```
{
 
    "age": 46,
    "gender": "male",
    "weight": 90.0,
    "height": 180.0,
    "body_fat": 29.5,
    "goal": "weight_loss",
    "lifestyle_intensity": "moderate",
    "recommended_calories": 2500.0,
    "weakness_points": "Shoulder,Knee",
    "experience_level": "BEGINNER"

}
```


---

## Update User's Profile : https://ai-personal-trainer.onrender.com/api/auth/profile/

### req type: PUT

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### request obj:

```
{
    "profile":{
        "age":46,
        "weight":90,
        "height":180,
        "gender":"male",
        "body_fat": 29.5,
        "goal": "weight_loss",
        "lifestyle_intensity":"moderate",
        "recommended_calories": 2500,
        "weakness_points": "Shoulder,Knee,Lower Back",
        "experience_level": "INTERMEDIATE_ADVANCED"
    }
}
```


### response obj:
### response code 200
```
{
    "msg": "User's profile updated:",
    "data": {
        "age": 46,
        "gender": "male",
        "weight": 90.0,
        "height": 180.0,
        "body_fat": 29.5,
        "goal": "weight_loss",
        "lifestyle_intensity": "moderate",
        "recommended_calories": 2500.0,
        "weakness_points": "Shoulder,Knee,Lower Back",
        "experience_level": "INTERMEDIATE_ADVANCED"
    }
}
```
---

## Generate User's Weekly Meal Plan : https://ai-personal-trainer.onrender.com/meals/generate-meal-plan/

### req type: POST

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### request obj:

```
{
    "profile":{
        "age":29,
        "weight":100,
        "height":178,
        "gender":"male",
        "body_fat": 19.5,
        "goal": "weight_loss",
        "lifestyle_intensity":"moderate",
        "recommended_calories": 2000
    }
}

```


### response code 201
### response breackdown:
- message : telling the status 
- meal plan id : this id needed to be stored in order to retrive the assosiated meal plan later from db
- start date : represents day 1 date for the generated plan
- end date : represents day 7 date for the generated plan
- weekly plan: is a list of sublists each sublist contain multi dictionaries each one for a meal within that day
- each dictionaries have :
	- meal name
	- meal category : breakfast, snak ...etc.
	- calories
	- protein
	- fat
	- carbohydrates
### response obj:
```
{
    "message": "Meal plan generated successfully",
    "meal_plan_id": 9,
    "start_date": "2024-08-11",
    "end_date": "2024-08-17",
    "weekly_plan": [
        [
            {
                "name": "Egg White Omelet Scrambled Or Fried With Cheese And Meat Ns As To Fat Added In Cooking",
                "category": "breakfast",
                "calories": 462.28160962078664,
                "protein": 23.05563243841683,
                "fat": 24.35759347591937,
                "carbohydrates": 5.407987643371093
            },
            {
                "name": "Submarine Sandwich Cold Cut On White Bread With Lettuce And Tomato",
                "category": "lunch",
                "calories": 449.616360042135,
                "protein": 14.558538610572931,
                "fat": 15.448530543160482,
                "carbohydrates": 62.07033008655698
            },
            {
                "name": "Turkey Or Chicken Burger Plain On White Bun",
                "category": "lunch",
                "calories": 491.8338586376406,
                "protein": 27.608635482978134,
                "fat": 11.786428681335588,
                "carbohydrates": 63.01217063118902
            },
            {
                "name": "Chicken Or Turkey Parmigiana",
                "category": "dinner",
                "calories": 367.292237780899,
                "protein": 22.225297536673125,
                "fat": 13.00200030773965,
                "carbohydrates": 24.335944395169918
            },
            {
                "name": "Tortilla Chips Cool Ranch Flavor (Doritos)",
                "category": "snacks",
                "calories": 992.1112169943823,
                "protein": 9.770274010517575,
                "fat": 31.666410216956447,
                "carbohydrates": 204.89589138704858
            },
            {
                "name": "Fruit Juice Drink Greater Than 3% Fruit Juice High Vitamin C And Added Thiamin",
                "category": "snacks",
                "calories": 113.98724620786521,
                "protein": 0.1799058953778024,
                "fat": 0.0,
                "carbohydrates": 39.98265021728291
            },
            {
                "name": "Vegetable Combinations Asian Style Broccoli Green Pepper Water Chestnut Etc. Cooked Fat Added In Cooking Ns As To Type Of Fat",
                "category": "snacks",
                "calories": 128.76337071629217,
                "protein": 2.601716025463604,
                "fat": 3.739036774888444,
                "carbohydrates": 26.766500639381647
            }
        ],
        [
            {
                "name": "Whole Wheat Cereal Cooked Ns As To Fat Added In Cooking",
                "category": "breakfast",
                "calories": 123.19204508196725,
                "protein": 2.6627218934911236,
                "fat": 3.9202945635694175,
                "carbohydrates": 21.75505250936798
            },
            {
                "name": "Rolls Hamburger Or Hotdog Mixed-Grain",
                "category": "lunch",
                "calories": 539.9917976092897,
                "protein": 16.70727462582666,
                "fat": 12.995451591942821,
                "carbohydrates": 95.03186502623036
            },
            {
                "name": "Turkey And Bacon Submarine Sandwich With Lettuce Tomato And Spread",
                "category": "lunch",
                "calories": 422.95935478142087,
                "protein": 18.151757744517923,
                "fat": 20.511154429283085,
                "carbohydrates": 41.443268492380724
            },
            {
                "name": "Chicken Broilers Or Fryers Back Meat And Skin Cooked Fried Batter",
                "category": "dinner",
                "calories": 679.609448702186,
                "protein": 38.23529411764705,
                "fat": 47.455057396577864,
                "carbohydrates": 21.840282881588816
            },
            {
                "name": "Oatmeal Instant Fruit Flavored Fat Not Added In Cooking",
                "category": "snacks",
                "calories": 197.1072721311476,
                "protein": 4.072398190045248,
                "fat": 2.5774312324019926,
                "carbohydrates": 42.80695444791408
            },
            {
                "name": "Grapefruit And Orange Sections Cooked Canned Or Frozen In Light Syrup",
                "category": "snacks",
                "calories": 123.19204508196725,
                "protein": 1.0268012530455968,
                "fat": 0.1949317738791423,
                "carbohydrates": 32.7071553397452
            },
            {
                "name": "Tortilla Chips Low Fat Baked Without Fat",
                "category": "snacks",
                "calories": 919.8339366120222,
                "protein": 19.14375217542638,
                "fat": 12.345679012345679,
                "carbohydrates": 170.88689630277298
            }
        ],
        [
            {
                "name": "Cereal (General Mills Chex Honey Nut)",
                "category": "breakfast",
                "calories": 872.4514028637773,
                "protein": 11.54692082111437,
                "fat": 6.476683937823834,
                "carbohydrates": 178.90746727129726
            },
            {
                "name": "Pasta Whole Grain With Cream Sauce Ready-To-Heat",
                "category": "lunch",
                "calories": 374.5724689628484,
                "protein": 7.881231671554252,
                "fat": 31.57383419689119,
                "carbohydrates": 32.44981407066797
            },
            {
                "name": "Frankfurter Or Hot Dog Sandwich Reduced Fat Or Light Plain On Whole Grain White Bun",
                "category": "lunch",
                "calories": 428.08282167182676,
                "protein": 24.230205278592376,
                "fat": 10.330310880829016,
                "carbohydrates": 52.55548767424978
            },
            {
                "name": "Beef Loin Top Sirloin Cap Steak Boneless Separable Lean And Fat Trimmed To 1/8 Inch Fat All Grades Cooked Grilled",
                "category": "dinner",
                "calories": 563.0219719814243,
                "protein": 47.65395894428152,
                "fat": 48.575129533678755,
                "carbohydrates": 1.651390029041627
            },
            {
                "name": "Purple Passion Fruit Juice",
                "category": "snacks",
                "calories": 118.65339078947372,
                "protein": 0.7148093841642229,
                "fat": 0.16191709844559588,
                "carbohydrates": 28.073630493707658
            },
            {
                "name": "Nuts Chestnuts Japanese Roasted",
                "category": "snacks",
                "calories": 467.6339519349846,
                "protein": 5.443548387096774,
                "fat": 2.590673575129534,
                "carbohydrates": 93.15904001331079
            },
            {
                "name": "Water Chestnut",
                "category": "snacks",
                "calories": 181.4698917956657,
                "protein": 2.5293255131964805,
                "fat": 0.2914507772020725,
                "carbohydrates": 39.674645447725084
            }
        ],
        [
            {
                "name": "Egg Roll Meatless",
                "category": "breakfast",
                "calories": 493.9421546120954,
                "protein": 8.94619547914677,
                "fat": 24.557137895102464,
                "carbohydrates": 58.33716248746927
            },
            {
                "name": "Macaroni Or Pasta Salad With Tuna",
                "category": "lunch",
                "calories": 369.07945381795975,
                "protein": 10.760904170646292,
                "fat": 17.193469954845433,
                "carbohydrates": 40.536749150186836
            },
            {
                "name": "Frankfurter Or Hot Dog Sandwich Chicken And/or Turkey Plain On Wheat Bun",
                "category": "lunch",
                "calories": 459.0540470372634,
                "protein": 22.7316141356256,
                "fat": 19.31226120180618,
                "carbohydrates": 43.68485718581976
            },
            {
                "name": "Chicken Drumstick Sauteed Skin Eaten",
                "category": "dinner",
                "calories": 372.75188619425785,
                "protein": 36.1349888570519,
                "fat": 20.580062521708925,
                "carbohydrates": 0.0
            },
            {
                "name": "Syrup Fruit Flavored",
                "category": "snacks",
                "calories": 479.252425106903,
                "protein": 0.0,
                "fat": 0.03473428273706148,
                "carbohydrates": 126.50730439487839
            },
            {
                "name": "Yogurt Whole Milk Flavors Other Than Fruit",
                "category": "snacks",
                "calories": 141.38864648747713,
                "protein": 5.253104106972303,
                "fat": 5.366446682875998,
                "carbohydrates": 18.325098009887913
            },
            {
                "name": "Quaker Instant Oatmeal Fruit And Cream Variety Of Flavors Reduced Sugar",
                "category": "snacks",
                "calories": 690.4172867440441,
                "protein": 16.17319325055715,
                "fat": 12.95588746092393,
                "carbohydrates": 139.080303771758
            }
        ],
        [
            {
                "name": "Egg Substitute Omelet Scrambled Or Fried Made With Butter",
                "category": "breakfast",
                "calories": 252.9224381877023,
                "protein": 24.101864483856296,
                "fat": 7.881388997268826,
                "carbohydrates": 9.571905246782261
            },
            {
                "name": "Salad Dressing Italian Dressing Commercial Regular Without Salt",
                "category": "lunch",
                "calories": 710.1283841423949,
                "protein": 0.8640291041382446,
                "fat": 36.89686565223046,
                "carbohydrates": 47.31515247580047
            },
            {
                "name": "Chicken Fillet Broiled Sandwich On Oat Bran Bun With Lettuce Tomato Spread",
                "category": "lunch",
                "calories": 488.8212507281554,
                "protein": 37.47157798999545,
                "fat": 9.155937052932762,
                "carbohydrates": 76.75669989362838
            },
            {
                "name": "Frankfurter Beef Heated",
                "category": "dinner",
                "calories": 783.0867797734629,
                "protein": 26.58026375625284,
                "fat": 38.18441930029913,
                "carbohydrates": 12.066951638123609
            },
            {
                "name": "Grapefruit Juice White Canned Or Bottled Unsweetened",
                "category": "snacks",
                "calories": 89.98202127831716,
                "protein": 1.250568440200091,
                "fat": 0.8583690987124465,
                "carbohydrates": 34.20481780129775
            },
            {
                "name": "Vegetable Combinations Asian Style Broccoli Green Pepper Water Chestnut Etc. Cooked Made With Oil",
                "category": "snacks",
                "calories": 162.94041690938514,
                "protein": 4.229195088676671,
                "fat": 4.083756015086488,
                "carbohydrates": 39.96610674130414
            },
            {
                "name": "Nuts Chestnuts European Raw Unpeeled",
                "category": "snacks",
                "calories": 518.0046089805826,
                "protein": 5.5025011368804,
                "fat": 2.939263883469892,
                "carbohydrates": 206.58984120306357
            }
        ],
        [
            {
                "name": "Egg Substitute Omelet Scrambled Or Fried With Vegetables Fat Added In Cooking",
                "category": "breakfast",
                "calories": 216.96026837270347,
                "protein": 19.294940796555434,
                "fat": 7.696981972858009,
                "carbohydrates": 13.04100398602795
            },
            {
                "name": "Cookies Vanilla Sandwich With Creme Filling Reduced Fat",
                "category": "lunch",
                "calories": 834.3108501968505,
                "protein": 11.221743810548977,
                "fat": 10.552967389102692,
                "carbohydrates": 266.1318202475051
            },
            {
                "name": "Tuna Salad Made With Light Italian Dressing",
                "category": "lunch",
                "calories": 149.89982178477695,
                "protein": 27.045209903121638,
                "fat": 2.035649179663763,
                "carbohydrates": 16.343817005988033
            },
            {
                "name": "Beef New Zealand Imported Subcutaneous Fat Cooked",
                "category": "dinner",
                "calories": 1441.7996016404202,
                "protein": 17.491926803013992,
                "fat": 79.29916953615555,
                "carbohydrates": 0.0
            },
            {
                "name": "Yogurt Greek Nonfat Fruit On Bottom Strawberry Chobani",
                "category": "snacks",
                "calories": 155.8169200131234,
                "protein": 19.590958019375673,
                "fat": 0.23293498075754504,
                "carbohydrates": 40.38284785229543
            },
            {
                "name": "Cooked Butternut Squash",
                "category": "snacks",
                "calories": 78.89464304461944,
                "protein": 2.4219590958019377,
                "fat": 0.09114847073121327,
                "carbohydrates": 35.718050081836346
            },
            {
                "name": "Gelatin Dessert With Fruit",
                "category": "snacks",
                "calories": 128.2037949475066,
                "protein": 2.9332615715823467,
                "fat": 0.09114847073121327,
                "carbohydrates": 54.85393582634733
            }
        ],
        [
            {
                "name": "Bread Lard Toasted Puerto Rican Style",
                "category": "breakfast",
                "calories": 649.6389957609454,
                "protein": 12.874251497005986,
                "fat": 6.0702278670153165,
                "carbohydrates": 144.32582924463597
            },
            {
                "name": "Ham Sandwich With Spread",
                "category": "lunch",
                "calories": 503.41799993050745,
                "protein": 20.076513639387887,
                "fat": 18.565558460963768,
                "carbohydrates": 58.483905834659524
            },
            {
                "name": "Hamburger; Single Large Patty; With Condiments Vegetables And Mayonnaise",
                "category": "lunch",
                "calories": 472.0849293954136,
                "protein": 18.862275449101794,
                "fat": 23.104221143070603,
                "carbohydrates": 40.55726643115844
            },
            {
                "name": "Fish Ns As To Type Baked Or Broiled Made With Oil",
                "category": "dinner",
                "calories": 346.7526472550383,
                "protein": 36.85961410512308,
                "fat": 15.016809861785582,
                "carbohydrates": 0.23402923503265116
            },
            {
                "name": "Gelatin Dessert With Fruit And Vegetables",
                "category": "snacks",
                "calories": 127.42115350938155,
                "protein": 1.6966067864271455,
                "fat": 0.11206574523720583,
                "carbohydrates": 35.221399872414004
            },
            {
                "name": "Pastry Fruit-Filled",
                "category": "snacks",
                "calories": 708.1273940931204,
                "protein": 6.76979374584165,
                "fat": 35.93574897273067,
                "carbohydrates": 93.23724723700823
            },
            {
                "name": "Jackfruit",
                "category": "snacks",
                "calories": 198.44278005559423,
                "protein": 2.8609447771124414,
                "fat": 1.1953679491968623,
                "carbohydrates": 54.4117971450914
            }
        ]
    ]
}
```
---

## Update User's Weekly Meal Plan : https://ai-personal-trainer.onrender.com/meals/update-meal-plan/

### req type: POST

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### request obj:

```
{
    "profile":{
        "age":29,
        "weight":100,
        "height":178,
        "gender":"male",
        "body_fat": 19.5,
        "goal": "weight_loss",
        "lifestyle_intensity":"moderate",
        "recommended_calories": 2000
    }
}

```


### response code 205
### response breackdown:
- message : telling the status 
- meal plan id : this id needed to be stored in order to retrive the assosiated meal plan later from db
- start date : represents day 1 date for the generated plan
- end date : represents day 7 date for the generated plan
- weekly plan: is a list of sublists each sublist contain multi dictionaries each one for a meal within that day
- each dictionaries have :
	- meal name
	- meal category : breakfast, snak ...etc.
	- calories
	- protein
	- fat
	- carbohydrates
### response obj:
```
{
    "message": "Meal plan generated successfully",
    "meal_plan_id": 9,
    "start_date": "2024-08-11",
    "end_date": "2024-08-17",
    "weekly_plan": [
        [
            {
                "name": "Egg White Omelet Scrambled Or Fried With Cheese And Meat Ns As To Fat Added In Cooking",
                "category": "breakfast",
                "calories": 462.28160962078664,
                "protein": 23.05563243841683,
                "fat": 24.35759347591937,
                "carbohydrates": 5.407987643371093
            },
            {
                "name": "Submarine Sandwich Cold Cut On White Bread With Lettuce And Tomato",
                "category": "lunch",
                "calories": 449.616360042135,
                "protein": 14.558538610572931,
                "fat": 15.448530543160482,
                "carbohydrates": 62.07033008655698
            },
            {
                "name": "Turkey Or Chicken Burger Plain On White Bun",
                "category": "lunch",
                "calories": 491.8338586376406,
                "protein": 27.608635482978134,
                "fat": 11.786428681335588,
                "carbohydrates": 63.01217063118902
            },
            {
                "name": "Chicken Or Turkey Parmigiana",
                "category": "dinner",
                "calories": 367.292237780899,
                "protein": 22.225297536673125,
                "fat": 13.00200030773965,
                "carbohydrates": 24.335944395169918
            },
            {
                "name": "Tortilla Chips Cool Ranch Flavor (Doritos)",
                "category": "snacks",
                "calories": 992.1112169943823,
                "protein": 9.770274010517575,
                "fat": 31.666410216956447,
                "carbohydrates": 204.89589138704858
            },
            {
                "name": "Fruit Juice Drink Greater Than 3% Fruit Juice High Vitamin C And Added Thiamin",
                "category": "snacks",
                "calories": 113.98724620786521,
                "protein": 0.1799058953778024,
                "fat": 0.0,
                "carbohydrates": 39.98265021728291
            },
            {
                "name": "Vegetable Combinations Asian Style Broccoli Green Pepper Water Chestnut Etc. Cooked Fat Added In Cooking Ns As To Type Of Fat",
                "category": "snacks",
                "calories": 128.76337071629217,
                "protein": 2.601716025463604,
                "fat": 3.739036774888444,
                "carbohydrates": 26.766500639381647
            }
        ],
        [
            {
                "name": "Whole Wheat Cereal Cooked Ns As To Fat Added In Cooking",
                "category": "breakfast",
                "calories": 123.19204508196725,
                "protein": 2.6627218934911236,
                "fat": 3.9202945635694175,
                "carbohydrates": 21.75505250936798
            },
            {
                "name": "Rolls Hamburger Or Hotdog Mixed-Grain",
                "category": "lunch",
                "calories": 539.9917976092897,
                "protein": 16.70727462582666,
                "fat": 12.995451591942821,
                "carbohydrates": 95.03186502623036
            },
            {
                "name": "Turkey And Bacon Submarine Sandwich With Lettuce Tomato And Spread",
                "category": "lunch",
                "calories": 422.95935478142087,
                "protein": 18.151757744517923,
                "fat": 20.511154429283085,
                "carbohydrates": 41.443268492380724
            },
            {
                "name": "Chicken Broilers Or Fryers Back Meat And Skin Cooked Fried Batter",
                "category": "dinner",
                "calories": 679.609448702186,
                "protein": 38.23529411764705,
                "fat": 47.455057396577864,
                "carbohydrates": 21.840282881588816
            },
            {
                "name": "Oatmeal Instant Fruit Flavored Fat Not Added In Cooking",
                "category": "snacks",
                "calories": 197.1072721311476,
                "protein": 4.072398190045248,
                "fat": 2.5774312324019926,
                "carbohydrates": 42.80695444791408
            },
            {
                "name": "Grapefruit And Orange Sections Cooked Canned Or Frozen In Light Syrup",
                "category": "snacks",
                "calories": 123.19204508196725,
                "protein": 1.0268012530455968,
                "fat": 0.1949317738791423,
                "carbohydrates": 32.7071553397452
            },
            {
                "name": "Tortilla Chips Low Fat Baked Without Fat",
                "category": "snacks",
                "calories": 919.8339366120222,
                "protein": 19.14375217542638,
                "fat": 12.345679012345679,
                "carbohydrates": 170.88689630277298
            }
        ],
        [
            {
                "name": "Cereal (General Mills Chex Honey Nut)",
                "category": "breakfast",
                "calories": 872.4514028637773,
                "protein": 11.54692082111437,
                "fat": 6.476683937823834,
                "carbohydrates": 178.90746727129726
            },
            {
                "name": "Pasta Whole Grain With Cream Sauce Ready-To-Heat",
                "category": "lunch",
                "calories": 374.5724689628484,
                "protein": 7.881231671554252,
                "fat": 31.57383419689119,
                "carbohydrates": 32.44981407066797
            },
            {
                "name": "Frankfurter Or Hot Dog Sandwich Reduced Fat Or Light Plain On Whole Grain White Bun",
                "category": "lunch",
                "calories": 428.08282167182676,
                "protein": 24.230205278592376,
                "fat": 10.330310880829016,
                "carbohydrates": 52.55548767424978
            },
            {
                "name": "Beef Loin Top Sirloin Cap Steak Boneless Separable Lean And Fat Trimmed To 1/8 Inch Fat All Grades Cooked Grilled",
                "category": "dinner",
                "calories": 563.0219719814243,
                "protein": 47.65395894428152,
                "fat": 48.575129533678755,
                "carbohydrates": 1.651390029041627
            },
            {
                "name": "Purple Passion Fruit Juice",
                "category": "snacks",
                "calories": 118.65339078947372,
                "protein": 0.7148093841642229,
                "fat": 0.16191709844559588,
                "carbohydrates": 28.073630493707658
            },
            {
                "name": "Nuts Chestnuts Japanese Roasted",
                "category": "snacks",
                "calories": 467.6339519349846,
                "protein": 5.443548387096774,
                "fat": 2.590673575129534,
                "carbohydrates": 93.15904001331079
            },
            {
                "name": "Water Chestnut",
                "category": "snacks",
                "calories": 181.4698917956657,
                "protein": 2.5293255131964805,
                "fat": 0.2914507772020725,
                "carbohydrates": 39.674645447725084
            }
        ],
        [
            {
                "name": "Egg Roll Meatless",
                "category": "breakfast",
                "calories": 493.9421546120954,
                "protein": 8.94619547914677,
                "fat": 24.557137895102464,
                "carbohydrates": 58.33716248746927
            },
            {
                "name": "Macaroni Or Pasta Salad With Tuna",
                "category": "lunch",
                "calories": 369.07945381795975,
                "protein": 10.760904170646292,
                "fat": 17.193469954845433,
                "carbohydrates": 40.536749150186836
            },
            {
                "name": "Frankfurter Or Hot Dog Sandwich Chicken And/or Turkey Plain On Wheat Bun",
                "category": "lunch",
                "calories": 459.0540470372634,
                "protein": 22.7316141356256,
                "fat": 19.31226120180618,
                "carbohydrates": 43.68485718581976
            },
            {
                "name": "Chicken Drumstick Sauteed Skin Eaten",
                "category": "dinner",
                "calories": 372.75188619425785,
                "protein": 36.1349888570519,
                "fat": 20.580062521708925,
                "carbohydrates": 0.0
            },
            {
                "name": "Syrup Fruit Flavored",
                "category": "snacks",
                "calories": 479.252425106903,
                "protein": 0.0,
                "fat": 0.03473428273706148,
                "carbohydrates": 126.50730439487839
            },
            {
                "name": "Yogurt Whole Milk Flavors Other Than Fruit",
                "category": "snacks",
                "calories": 141.38864648747713,
                "protein": 5.253104106972303,
                "fat": 5.366446682875998,
                "carbohydrates": 18.325098009887913
            },
            {
                "name": "Quaker Instant Oatmeal Fruit And Cream Variety Of Flavors Reduced Sugar",
                "category": "snacks",
                "calories": 690.4172867440441,
                "protein": 16.17319325055715,
                "fat": 12.95588746092393,
                "carbohydrates": 139.080303771758
            }
        ],
        [
            {
                "name": "Egg Substitute Omelet Scrambled Or Fried Made With Butter",
                "category": "breakfast",
                "calories": 252.9224381877023,
                "protein": 24.101864483856296,
                "fat": 7.881388997268826,
                "carbohydrates": 9.571905246782261
            },
            {
                "name": "Salad Dressing Italian Dressing Commercial Regular Without Salt",
                "category": "lunch",
                "calories": 710.1283841423949,
                "protein": 0.8640291041382446,
                "fat": 36.89686565223046,
                "carbohydrates": 47.31515247580047
            },
            {
                "name": "Chicken Fillet Broiled Sandwich On Oat Bran Bun With Lettuce Tomato Spread",
                "category": "lunch",
                "calories": 488.8212507281554,
                "protein": 37.47157798999545,
                "fat": 9.155937052932762,
                "carbohydrates": 76.75669989362838
            },
            {
                "name": "Frankfurter Beef Heated",
                "category": "dinner",
                "calories": 783.0867797734629,
                "protein": 26.58026375625284,
                "fat": 38.18441930029913,
                "carbohydrates": 12.066951638123609
            },
            {
                "name": "Grapefruit Juice White Canned Or Bottled Unsweetened",
                "category": "snacks",
                "calories": 89.98202127831716,
                "protein": 1.250568440200091,
                "fat": 0.8583690987124465,
                "carbohydrates": 34.20481780129775
            },
            {
                "name": "Vegetable Combinations Asian Style Broccoli Green Pepper Water Chestnut Etc. Cooked Made With Oil",
                "category": "snacks",
                "calories": 162.94041690938514,
                "protein": 4.229195088676671,
                "fat": 4.083756015086488,
                "carbohydrates": 39.96610674130414
            },
            {
                "name": "Nuts Chestnuts European Raw Unpeeled",
                "category": "snacks",
                "calories": 518.0046089805826,
                "protein": 5.5025011368804,
                "fat": 2.939263883469892,
                "carbohydrates": 206.58984120306357
            }
        ],
        [
            {
                "name": "Egg Substitute Omelet Scrambled Or Fried With Vegetables Fat Added In Cooking",
                "category": "breakfast",
                "calories": 216.96026837270347,
                "protein": 19.294940796555434,
                "fat": 7.696981972858009,
                "carbohydrates": 13.04100398602795
            },
            {
                "name": "Cookies Vanilla Sandwich With Creme Filling Reduced Fat",
                "category": "lunch",
                "calories": 834.3108501968505,
                "protein": 11.221743810548977,
                "fat": 10.552967389102692,
                "carbohydrates": 266.1318202475051
            },
            {
                "name": "Tuna Salad Made With Light Italian Dressing",
                "category": "lunch",
                "calories": 149.89982178477695,
                "protein": 27.045209903121638,
                "fat": 2.035649179663763,
                "carbohydrates": 16.343817005988033
            },
            {
                "name": "Beef New Zealand Imported Subcutaneous Fat Cooked",
                "category": "dinner",
                "calories": 1441.7996016404202,
                "protein": 17.491926803013992,
                "fat": 79.29916953615555,
                "carbohydrates": 0.0
            },
            {
                "name": "Yogurt Greek Nonfat Fruit On Bottom Strawberry Chobani",
                "category": "snacks",
                "calories": 155.8169200131234,
                "protein": 19.590958019375673,
                "fat": 0.23293498075754504,
                "carbohydrates": 40.38284785229543
            },
            {
                "name": "Cooked Butternut Squash",
                "category": "snacks",
                "calories": 78.89464304461944,
                "protein": 2.4219590958019377,
                "fat": 0.09114847073121327,
                "carbohydrates": 35.718050081836346
            },
            {
                "name": "Gelatin Dessert With Fruit",
                "category": "snacks",
                "calories": 128.2037949475066,
                "protein": 2.9332615715823467,
                "fat": 0.09114847073121327,
                "carbohydrates": 54.85393582634733
            }
        ],
        [
            {
                "name": "Bread Lard Toasted Puerto Rican Style",
                "category": "breakfast",
                "calories": 649.6389957609454,
                "protein": 12.874251497005986,
                "fat": 6.0702278670153165,
                "carbohydrates": 144.32582924463597
            },
            {
                "name": "Ham Sandwich With Spread",
                "category": "lunch",
                "calories": 503.41799993050745,
                "protein": 20.076513639387887,
                "fat": 18.565558460963768,
                "carbohydrates": 58.483905834659524
            },
            {
                "name": "Hamburger; Single Large Patty; With Condiments Vegetables And Mayonnaise",
                "category": "lunch",
                "calories": 472.0849293954136,
                "protein": 18.862275449101794,
                "fat": 23.104221143070603,
                "carbohydrates": 40.55726643115844
            },
            {
                "name": "Fish Ns As To Type Baked Or Broiled Made With Oil",
                "category": "dinner",
                "calories": 346.7526472550383,
                "protein": 36.85961410512308,
                "fat": 15.016809861785582,
                "carbohydrates": 0.23402923503265116
            },
            {
                "name": "Gelatin Dessert With Fruit And Vegetables",
                "category": "snacks",
                "calories": 127.42115350938155,
                "protein": 1.6966067864271455,
                "fat": 0.11206574523720583,
                "carbohydrates": 35.221399872414004
            },
            {
                "name": "Pastry Fruit-Filled",
                "category": "snacks",
                "calories": 708.1273940931204,
                "protein": 6.76979374584165,
                "fat": 35.93574897273067,
                "carbohydrates": 93.23724723700823
            },
            {
                "name": "Jackfruit",
                "category": "snacks",
                "calories": 198.44278005559423,
                "protein": 2.8609447771124414,
                "fat": 1.1953679491968623,
                "carbohydrates": 54.4117971450914
            }
        ]
    ]
}
```
---

## Get User's  Weekly Meal Plan by Id: https://ai-personal-trainer.onrender.com/meals/view-daily-meal/< Plan_id:int >
### req type: GET

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### response code 200
### response breackdown:
- id : meal plan id
- start date : represents day 1 date for the generated plan
- end date : represents day 7 date for the generated plan
- created at: time of creation
- daily meals: is a list of dictionaries each one is a day and have:
	- id: day id
	- date: day date
	- meals: is a list of dictionaries each dictionary is a meal and have :
		- meal name
		- meal category : breakfast, snak ...etc.
		- calories
		- protein
		- fat
		- carbohydrates
### response obj:
```
{
    "id": 4,
    "user": 4,
    "start_date": "2024-08-11",
    "end_date": "2024-08-17",
    "created_at": "2024-08-11T16:17:02.471665Z",
    "daily_meals": [
        {
            "id": 22,
            "date": "2024-08-11",
            "meals": [
                {
                    "fat": 13.008511887290872,
                    "name": "Egg Omelet Or Scrambled Egg With Potatoes And/or Onions Fat Added In Cooking",
                    "protein": 13.768115942028983,
                    "calories": 392.1252143717727,
                    "category": "breakfast",
                    "carbohydrates": 39.270272335319426
                },
                {
                    "fat": 18.726152039917814,
                    "name": "Seafood Salad",
                    "protein": 18.26086956521739,
                    "calories": 459.48414690189315,
                    "category": "lunch",
                    "carbohydrates": 5.713800413770274
                },
                {
                    "fat": 33.002641620193714,
                    "name": "Beef Rib Whole (Ribs 6-12) Separable Lean And Fat Trimmed To 1/8 Inch Fat All Grades Cooked Roasted",
                    "protein": 41.24999999999999,
                    "calories": 844.3923327882958,
                    "category": "dinner",
                    "carbohydrates": 0.0
                },
                {
                    "fat": 15.262694452597593,
                    "name": "Cake Snack Cakes Creme-Filled Chocolate With Frosting Low-Fat With Added Fiber",
                    "protein": 6.721014492753622,
                    "calories": 983.9215501721168,
                    "category": "snacks",
                    "carbohydrates": 335.90367347732536
                },
                {
                    "fat": 0.0,
                    "name": "Fruit Punch Drink Without Added Nutrients Canned",
                    "protein": 0.0,
                    "calories": 115.4724557659208,
                    "category": "snacks",
                    "carbohydrates": 57.961178773584905
                }
            ]
        },
        {
            "id": 23,
            "date": "2024-08-12",
            "meals": [
                {
                    "fat": 30.26570048309178,
                    "name": "Egg Omelet Or Scrambled Egg With Cheese Made With Cooking Spray",
                    "protein": 27.93418647166362,
                    "calories": 931.7985666666665,
                    "category": "breakfast",
                    "carbohydrates": 43.86477104539201
                },
                {
                    "fat": 11.207729468599032,
                    "name": "Cabbage Salad Or Coleslaw Made With Italian Dressing",
                    "protein": 2.193784277879342,
                    "calories": 382.14210880149807,
                    "category": "lunch",
                    "carbohydrates": 153.52669865887202
                },
                {
                    "fat": 38.30917874396135,
                    "name": "Pork Steak Or Cutlet Fried Lean And Fat Eaten",
                    "protein": 47.97074954296161,
                    "calories": 1251.122794569288,
                    "category": "dinner",
                    "carbohydrates": 1.207287276478679
                },
                {
                    "fat": 0.0,
                    "name": "Fruit Flavored Drink Diet",
                    "protein": 0.020893183598850874,
                    "calories": 20.939293632958798,
                    "category": "snacks",
                    "carbohydrates": 29.176109181568076
                },
                {
                    "fat": 0.21739130434782605,
                    "name": "Cooked Butternut Squash",
                    "protein": 1.880386523896579,
                    "calories": 209.39293632958797,
                    "category": "snacks",
                    "carbohydrates": 211.07405883768905
                }
            ]
        },
        {
            "id": 24,
            "date": "2024-08-13",
            "meals": [
                {
                    "fat": 1.0283315844700944,
                    "name": "Malt-O-Meal Farina Hot Wheat Cereal Dry",
                    "protein": 11.343525909890408,
                    "calories": 814.9516218051117,
                    "category": "breakfast",
                    "carbohydrates": 228.17306714709048
                },
                {
                    "fat": 29.171038824763908,
                    "name": "Luncheon Meat Pork And Chicken Minced Canned Includes Spam Lite",
                    "protein": 16.484914084697607,
                    "calories": 437.61785718849836,
                    "category": "lunch",
                    "carbohydrates": 3.9900730653960124
                },
                {
                    "fat": 28.52046169989507,
                    "name": "Beef Chuck Shoulder Clod Top Blade Steak Separable Lean And Fat Trimmed To 0 Inch Fat Choice Cooked Grilled",
                    "protein": 26.73521850899743,
                    "calories": 509.0656706070287,
                    "category": "dinner",
                    "carbohydrates": 0.0
                },
                {
                    "fat": 18.71983210912907,
                    "name": "Formulated Bar Slim-Fast Optima Meal Bar Milk Chocolate Peanut",
                    "protein": 17.524015694763904,
                    "calories": 861.8392493610223,
                    "category": "snacks",
                    "carbohydrates": 177.95725871666215
                },
                {
                    "fat": 2.560335781741868,
                    "name": "Fruit Smoothie With Whole Fruit And Dairy Added Protein",
                    "protein": 7.912325801650656,
                    "calories": 171.92130103833864,
                    "category": "snacks",
                    "carbohydrates": 28.728526070851288
                }
            ]
        },
        {
            "id": 25,
            "date": "2024-08-14",
            "meals": [
                {
                    "fat": 13.394018205461641,
                    "name": "Continental Mills Krusteaz Almond Poppyseed Muffin Mix Artificially Flavored Dry",
                    "protein": 8.741463414634145,
                    "calories": 687.7430268393172,
                    "category": "breakfast",
                    "carbohydrates": 142.3599173138811
                },
                {
                    "fat": 20.598179453836153,
                    "name": "Frankfurter Or Hot Dog Sandwich Beef And Pork Plain On Whole Grain White Bun",
                    "protein": 15.67219512195122,
                    "calories": 462.33442713360796,
                    "category": "lunch",
                    "carbohydrates": 46.22931177322462
                },
                {
                    "fat": 10.403120936280885,
                    "name": "Beef Chuck Top Blade Separable Lean Only Trimmed To 0 Inch Fat Select Cooked Broiled",
                    "protein": 40.83512195121951,
                    "calories": 302.7385572689817,
                    "category": "dinner",
                    "carbohydrates": 0.0
                },
                {
                    "fat": 12.379713914174253,
                    "name": "Soft Fruit And Nut Squares",
                    "protein": 3.6058536585365855,
                    "calories": 641.6741159505591,
                    "category": "snacks",
                    "carbohydrates": 138.9892261499678
                },
                {
                    "fat": 23.224967490247074,
                    "name": "Snacks Shrimp Cracker",
                    "protein": 11.145365853658536,
                    "calories": 700.9055728075338,
                    "category": "snacks",
                    "carbohydrates": 111.27046976292641
                }
            ]
        },
        {
            "id": 26,
            "date": "2024-08-15",
            "meals": [
                {
                    "fat": 3.2388663967611335,
                    "name": "English Muffins Whole-Wheat",
                    "protein": 16.098788017379373,
                    "calories": 498.21363222124666,
                    "category": "breakfast",
                    "carbohydrates": 135.31900908258277
                },
                {
                    "fat": 28.471177944862156,
                    "name": "Frankfurter Or Hot Dog Sandwich Beef Plain On Whole Wheat Bun",
                    "protein": 22.57489137891607,
                    "calories": 746.0933211589113,
                    "category": "lunch",
                    "carbohydrates": 72.24829272057698
                },
                {
                    "fat": 15.639097744360903,
                    "name": "Pork Fresh Variety Meats And By-Products Stomach Raw",
                    "protein": 30.825520237823003,
                    "calories": 390.2264410008779,
                    "category": "dinner",
                    "carbohydrates": 0.0
                },
                {
                    "fat": 32.51204935415461,
                    "name": "Cake Or Cupcake Peanut Butter",
                    "protein": 9.421449805625429,
                    "calories": 1013.6070448639157,
                    "category": "snacks",
                    "carbohydrates": 179.86709870630435
                },
                {
                    "fat": 0.13880855986119142,
                    "name": "Grapefruit And Orange Sections Cooked Canned Or Frozen In Light Syrup",
                    "protein": 1.0793505602561169,
                    "calories": 147.25526075504828,
                    "category": "snacks",
                    "carbohydrates": 51.414524490535776
                }
            ]
        },
        {
            "id": 27,
            "date": "2024-08-16",
            "meals": [
                {
                    "fat": 16.970146486185797,
                    "name": "Macaroni Or Pasta Salad With Egg",
                    "protein": 9.065502183406114,
                    "calories": 516.7756453138435,
                    "category": "breakfast",
                    "carbohydrates": 79.65251172359622
                },
                {
                    "fat": 15.590580381976638,
                    "name": "Taco Or Tostada Salad With Meat And Sour Cream",
                    "protein": 11.982532751091703,
                    "calories": 432.649377472055,
                    "category": "lunch",
                    "carbohydrates": 53.10167448239748
                },
                {
                    "fat": 22.39940663823475,
                    "name": "Pork Fresh Variety Meats And By-Products Ears Frozen Raw",
                    "protein": 39.21397379912664,
                    "calories": 562.4441907136714,
                    "category": "dinner",
                    "carbohydrates": 2.121238661081124
                },
                {
                    "fat": 20.470980901168183,
                    "name": "Cookies Animal Crackers (Includes Arrowroot Tea Biscuits)",
                    "protein": 12.052401746724891,
                    "calories": 1072.0090130696474,
                    "category": "snacks",
                    "carbohydrates": 261.97297464351885
                },
                {
                    "fat": 4.568885592434638,
                    "name": "Nutritional Supplement For People With Diabetes Liquid",
                    "protein": 7.685589519650656,
                    "calories": 211.51747343078245,
                    "category": "snacks",
                    "carbohydrates": 42.000525489406265
                }
            ]
        },
        {
            "id": 28,
            "date": "2024-08-17",
            "meals": [
                {
                    "fat": 18.25762563089752,
                    "name": "Moo Shu Pork Without Chinese Pancake",
                    "protein": 19.971550497866286,
                    "calories": 402.7717086832061,
                    "category": "breakfast",
                    "carbohydrates": 15.800643267112841
                },
                {
                    "fat": 18.187403993855607,
                    "name": "Cheese Sandwich Reduced Fat Cheddar Cheese On White Bread No Spread",
                    "protein": 31.2375533428165,
                    "calories": 757.5308958015266,
                    "category": "lunch",
                    "carbohydrates": 114.28512330142323
                },
                {
                    "fat": 6.460390607856047,
                    "name": "Stir Fried Beef And Vegetables In Soy Sauce",
                    "protein": 20.578473210052156,
                    "calories": 248.06469475190838,
                    "category": "dinner",
                    "carbohydrates": 15.837821251270753
                },
                {
                    "fat": 0.0,
                    "name": "Fruit Flavored Smoothie Drink Frozen No Dairy",
                    "protein": 0.0,
                    "calories": 74.68614465648855,
                    "category": "snacks",
                    "carbohydrates": 28.25526796001355
                },
                {
                    "fat": 37.09457976739083,
                    "name": "Mars Snackfood Us M&Ms Milk Chocolate",
                    "protein": 8.212422949265054,
                    "calories": 1312.34225610687,
                    "category": "snacks",
                    "carbohydrates": 264.6700692201795
                }
            ]
        }
    ]
}
```

---

## Get User's  Daily Meal Plan by Id: https://ai-personal-trainer.onrender.com/meals/view-daily-meal/< Meal_id:int >/< Day_id:int >/

### req type: GET

### req headers:
- Authorization is required via Bearer Token
- Content-Type: application/json

### response code 200
### response breackdown:
- id : for the assosiated day
- date: day date
- meals : list of dictionaries each dictionaries is a meal and have :
		- meal name
		- meal category : breakfast, snak ...etc.
		- calories
		- protein
		- fat
		- carbohydrates

### response obj:
```
{
    "id": 1,
    "date": "2024-08-11",
    "meals": [
        {
            "fat": 24.08887606406002,
            "name": "French Toast Sticks Plain From Fast Food / Restaurant",
            "protein": 9.901823281907433,
            "calories": 762.7273396998635,
            "category": "breakfast",
            "carbohydrates": 134.825068973384
        },
        {
            "fat": 8.841437022074738,
            "name": "Turkey Or Chicken Burger Plain On Bun From Fast Food / Restaurant",
            "protein": 27.980364656381486,
            "calories": 444.28867537517044,
            "category": "lunch",
            "carbohydrates": 57.678876454372606
        },
        {
            "fat": 22.830760352041555,
            "name": "Beef Short Loin Porterhouse Steak Separable Lean And Fat Trimmed To 1/8 Inch Fat Choice Cooked Grilled",
            "protein": 34.85273492286115,
            "calories": 541.536411186903,
            "category": "dinner",
            "carbohydrates": 0.0
        },
        {
            "fat": 19.391141249458954,
            "name": "Cookies Chocolate Chip Commercially Prepared Special Dietary",
            "protein": 5.46984572230014,
            "calories": 858.0682571623464,
            "category": "snacks",
            "carbohydrates": 204.12871416349807
        },
        {
            "fat": 4.8477853123647385,
            "name": "Gelatin Dessert With Fruit And Whipped Cream",
            "protein": 1.7952314165497896,
            "calories": 188.7750165757162,
            "category": "snacks",
            "carbohydrates": 42.21626540874524
        }
    ]
}
```



# Web Sockets

## Video streaming Socket : 
URL : wss://ai-personal-trainer.onrender.com/ws/session/${sessionId}/
accepted data type is bytes

## JSON Socket : 
URL : wss://ai-personal-trainer.onrender.com/ws/session/${sessionId}/
accepted data type is JSON

new events are available :
- message event : this event is called to handle the received data from the server while the socket connection is opened 
- send event : this event is updated to expect json data from client side (note byte data)  

#Response_Object_updates
1. using the mentioned send event : the server will expect the following json obj :
```
{
      type: "client_data",
      data: {object},
 };
 ```
2. using the mentioned message event: the server will send to the client the following json obj:
```
{
      'type': 'server_response',
      'data': { 'results': " something" }
}
```

## POSE Socket : 
URL : wss://ai-personal-trainer.onrender.com/ws/session/${sessionId}/
accepted data type is JSON


---

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

---

## Get all streaming sessions : https://ai-personal-trainer.onrender.com/stream/sessions/active/

### req type: GET

### req headers:

- Content-Type: application/json

### res obj:

```
{ "sessions":[
	{
		"session_id": "<uuid:session>",
		"message": "Session started"
	},
]
}
```
---

## Show streaming Videos : https://ai-personal-trainer.onrender.com/stream/browse/ 

### req type: HEAD

__It is a static page to serve the recorded videos__

---

## View all streaming Videos : https://ai-personal-trainer.onrender.com/stream/video_stream/list/

### req type: GET

### req headers:
- Content-Type: application/json

### res obj:

```
{ "videos":[
	{
	},
]
}
```

---

# Admin Dashboard

### Following the link : https://ai-personal-trainer.onrender.com/admin

### Note:

- This dashboard is used as content management system where the admin could add users accounts and any other data needed

---
