# Eagle Transport - Fleet Management System

A beginner-friendly Flask + SQLite project with two main portals:
- Owner Dashboard
- Driver App

## Main Features
- Owner and Driver login
- 9 sample trucks across 3 categories
- Fuel logs and tyre logs
- Truck health tracking
- Emergency alerts for low diesel, low engine oil, low battery, low coolant, low brake oil, and poor tyre condition
- Owner can add new truck and new driver
- JSON API endpoints for trucks, alerts, drivers, fuel logs, and tyre logs

## Demo Login
### Owner
- Username: `admin`
- Password: `eagle123`

### Driver examples
- Username: `ravi`
- Password: `driver123`

## How to Run
1. Open the project folder in VS Code.
2. Open terminal.
3. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open browser:
   ```
   http://127.0.0.1:5000/
   ```

## Useful URLs
- Home: `/`
- Truck Types: `/trucks`
- Owner Login: `/owner/login`
- Driver Login: `/driver/login`
- Owner Dashboard: `/owner/dashboard`
- Driver App: `/driver/app`

## Database Schema Included
See `schema.sql`.

## API Endpoints
- `GET /api/trucks`
- `GET /api/alerts`
- `GET /api/drivers`
- `GET /api/fuel-logs`
- `GET /api/tyre-logs`

## Note
This is a demo starter project made for easy understanding and future upgrades.


Home page now includes simple truck booking with trip level and truck selection.
