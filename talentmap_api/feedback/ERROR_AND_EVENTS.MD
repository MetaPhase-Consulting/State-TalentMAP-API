### Storing errors and events from frontend

##### Create secret pair
Execute command:

`python manage.py create_fe_secrets`

It will return a public and private secret. Store these for later.


##### Posting an error or event

Both errors and events use the same post object stucture

```
{
    "time": "12:13:01T2018-01-10Z", // String timestamp of your event/error
    "auth": "aosdfijadfoiajdsf1231231250234ioj" // SHA-256 of timestamp + private secret
    "payload": {
        //JSON payload to store in DB
    }
}
```

The auth should be constructed using the time string in the post object and the private secret.
i.e. `sha256(time_string + private_secret)`

If all goes well, you'll get a 201 CREATED response and the contents of "payload" will be stored in the DB

##### Endpoints

The endpoints are:
`/api/v1/fe-reporting/errors/<PUBLIC_SECRET>/` - for errors
`/api/v1/fe-reporting/events/<PUBLIC_SECRET>/` - for events
