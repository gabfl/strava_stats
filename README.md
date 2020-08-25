# strava_stats

Weekly and monthly aggregated Strava stats

## Prerequisite: create a Strava app and authorize a user

 - Create a [Strava App](https://www.strava.com/settings/api)
 - Authorize a Strava user:

Visit: 
```
http://www.strava.com/oauth/authorize?client_id=[YOUR CLIENT ID]&response_type=code&redirect_uri=[REDIRECT URL]&approval_prompt=force&scope=activity:read
```

`redirect_uri` needs to be a callback URL where you can save payloads. You can use [https://webhook.link](https://webhook.link) for this purpose.

 - Obtain a user refresh token:

```bash
curl -X POST https://www.strava.com/oauth/token \
-F client_id=[YOUR CLIENT ID] \
-F client_secret=[YOUR CLIENT SECRET] \
-F code=[STRAVA USER CODE] \
-F grant_type=authorization_code
```

## Usage

```bash
# INstall dependencies
pip3 install -r requirements.txt

# Export app & user secrets
export STRAVA_CLIENT_ID="[YOUR CLIENT ID]"
export STRAVA_CLIENT_SECRET="[YOUR CLIENT SECRET]"
export STRAVA_USER_REFRESH_TOKEN="[STRAVA USER REFRESH TOKEN]"

python3 strava.py
+------+-----------+-----------+------------+------------+
| Type | This week | Last week | This month | Last month |
+------+-----------+-----------+------------+------------+
| Run  |    5.5 mi |   12.0 mi |    42.2 mi |    56.9 mi |
| Bike |    0.0 mi |   22.3 mi |    58.8 mi |    74.7 mi |
+------+-----------+-----------+------------+------------+
```
