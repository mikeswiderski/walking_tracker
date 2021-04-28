# walking_tracker

## REST API project that tracks walking distance of members

- Project users can create new accounts and log in.
    - log in/auth through JWT
- All endpoints (except register) are non-public and require authentications.
- Project has three distinct account types: member than can operate with his own data only, manager than can manage members data and platform admin that can manage all data: users   and walking records.
- Every record of walking has a date, time, distance and location.
- Add data is returned in JSON format.
- All LIST endpoints support filtering and pagination.
- All list views support filtering by search param: `/user/list?search=<search phrase>`
- Filtering ability is very flexible and support complex search terms: using parentheses to define precedence and support following operations: or, and, eq, ne, gt, lt for  all     fields that are returned for a given endpoint.
    - Example -> `(date eq '2021-01-18') AND ((distance lt 30) OR (distance gt 100))`.
- Using date, time and location, the project is able to figure out weather conditions during the walk using a public 3rd party API and save that conditions with each record.
- Members are able to request a monthly report of their activity that includes average walk distance.
- All endpoints are unit tested.
