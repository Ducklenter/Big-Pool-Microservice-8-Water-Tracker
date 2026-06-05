This microservice allows other program track the user's water intake easily but sending the user's goal and current intake for the day.


RUNNING:
  pip install -r requirements.txt
  python app.py

The service is now running on localhost:5001 (note that the reminder microservice should be running separately on port 5000 for push notifications to work, intake logging still functional regardless)

PUT /goal

Body: 
  user_id (string)
  goal_ml (number > 0) (goal ml by default 2000)

Response: 200
{
  "user_id": "alice",
  "goal_ml": 2500.0,
  "message": "Daily goal updated to 2500 ml."
}

POST /intake

Body:
  user_id (string) (defaults to "default_user")
  amount_ml (number > 0)

Response: 201

{
  "date": "something",
  "added_ml": number,
  "total_ml": number,
  "goal_ml": number,
  "goal_reached": false,
  "reminder_scheduled": null
}

GET /goal/<user_id>

returns the current daily goal for a given user

Response: 200

{
  "user_id": "name",
  "goal_ml": number
}

GET /intake/today

Returns today's intake summary for a user.

Params:
  user_id (defaults to "default_user")

Response: 200

{
  "date": "somedate",
  same stuff as the post but no reminder.


Logs a water entry for today. If the cumulative total meets or exceeds the user's goal, a congratulatory reminder is scheduled.
