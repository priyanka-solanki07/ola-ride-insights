# Ola Ride Insights

Ride-sharing analytics on OLA's July 2024 bookings (103,024 rides): data cleaning, SQL, Power BI, Streamlit.

## Project structure
```
app.py                     Streamlit app (7 tabs incl. SQL Explorer + Power BI embed)
requirements.txt           streamlit, pandas, plotly
data/ola_cleaned.csv       cleaned dataset
data/ola.db                SQLite copy (table: ola_rides)
sql/ola_queries.sql        the 10 SQL questions
powerbi/POWERBI_GUIDE.md   DAX measures + page-by-page build steps
clean.py                   cleaning script
```
Run the app: `pip install -r requirements.txt` then `streamlit run app.py`

To rebuild the cleaned CSV and SQLite database, place `OLA_DataSet.xlsx` in
this folder or keep it in the workspace folder above `Ola_Ride_Insights_Project`,
then run `python clean.py` from this project folder. The script reads the `July`
worksheet.

## 1. Data understanding & cleaning
- 103,024 rows x 20 columns, 31 days (1-31 Jul 2024), no duplicate Booking_IDs.
- Booking status: Success 62.1%, Canceled by Driver 17.9%, Canceled by Customer 10.2%, Driver Not Found 9.8%.
- Blank cells are structural, not errors: ratings, TAT, payment method exist only for Success rides (39,057 non-success rows). Text columns were filled with "Not Applicable"; numeric ones (V_TAT, C_TAT, ratings) are left null so averages stay correct.
- Dropped the `Vehicle Images` URL column (icons are in Sheet2 of the source file).
- Derived features: Hour, Day, Day_Name, Week, Time_Slot, Is_Success.
- Vehicle type is spelled `eBike` in the data (the slides say E-Bike).

## 2. Key insights
- **Revenue:** Rs 3.51 crore (35,080,467) from 63,967 successful rides; average ticket Rs 548.
- **Demand is flat across the day:** busiest hours are 12:00, 15:00, 08:00, 17:00 and 09:00 (about 4.3-4.4k bookings each). Tue/Wed/Mon are the busiest weekdays (about 16.4-16.9k), Thu-Sun about 13.0-13.3k, so driver supply should be weighted to Mon-Wed.
- **Only 62% of bookings complete.** Driver-side cancellations (17.9%) are almost double customer-side (10.2%). Top driver reason: "Personal & Car related issue" (6,542); next "Customer related issue" (5,413).
- **Customers cancel mainly because of the driver:** "Driver is not moving towards pickup" (3,175) and "Driver asked to cancel" (2,670) are the top two reasons, so about 56% of customer cancellations trace back to driver behaviour. Fixable with ETA tracking / driver-side penalties.
- **Payments:** Cash 55% of revenue (Rs 1.93 cr), UPI 40% (Rs 1.42 cr), cards under 5%. Pushing UPI would cut cash handling.
- **Vehicle types are very even:** each has about 14.6-14.9k bookings and success rate 61.4-63.0%. Prime Sedan leads on revenue (Rs 52.2 lakh). Auto has by far the lowest total distance (92k vs about 225-235k for the others), i.e. much shorter trips.
- **Ratings** are about 4.0 for both drivers and customers, with no meaningful gap between vehicle types, so rating isn't a differentiator.
- **Incomplete rides:** 3,926 (6.1% of successful bookings); causes are Customer Demand (1,601), Vehicle Breakdown (1,591), Other (734).

## 3. SQL questions and results
**Q1. Retrieve all successful bookings** (63,967 rows, first 5 shown)
```
      Date     Time    Booking_ID Booking_Status Customer_ID Vehicle_Type Pickup_Location Drop_Location  V_TAT  C_TAT Canceled_Rides_by_Customer Canceled_Rides_by_Driver Incomplete_Rides Incomplete_Rides_Reason  Booking_Value Payment_Method  Ride_Distance  Driver_Ratings  Customer_Rating  Hour  Day Day_Name  Week  Is_Success          Time_Slot
2024-07-25 22:20:00 CNR2940424040        Success   CID225428         Bike     Magadi Road       Varthur  203.0   30.0             Not Applicable           Not Applicable               No          Not Applicable            158           Cash             13             4.1              4.0    22   25 Thursday     4           1 Late Night (21-23)
2024-07-30 19:59:00 CNR2982357879        Success   CID270156    Prime SUV   Sahakar Nagar       Varthur  238.0  130.0             Not Applicable           Not Applicable               No          Not Applicable            386            UPI             40             4.2              4.8    19   30  Tuesday     5           1    Evening (17-20)
2024-07-02 09:02:00 CNR1797421769        Success   CID939555         Mini     Rajajinagar   Chamarajpet  252.0   80.0             Not Applicable           Not Applicable               No          Not Applicable            822    Credit Card             45             4.0              3.0     9    2  Tuesday     1           1     Morning (6-11)
2024-07-13 04:42:00 CNR8787177882        Success   CID802429         Mini        Kadugodi   Vijayanagar  231.0   90.0             Not Applicable           Not Applicable               No          Not Applicable            173            UPI             41             3.4              4.6     4   13 Saturday     2           1        Night (0-5)
2024-07-23 09:51:00 CNR3612067560        Success   CID476071         Bike     Tumkur Road    Whitefield  133.0   40.0             Not Applicable           Not Applicable               No          Not Applicable            140           Cash             49             3.2              4.5     9   23  Tuesday     4           1     Morning (6-11)
```

**Q2. Average ride distance for each vehicle type** (7 rows, first 5 shown)
```
Vehicle_Type  avg_ride_distance
 Prime Sedan              15.76
       eBike              15.58
        Bike              15.53
        Mini              15.51
  Prime Plus              15.45
```

**Q3. Total number of cancelled rides by customers**
```
 cancelled_by_customer
                 10499
```

**Q4. Top 5 customers with the highest number of rides**
```
Customer_ID  total_rides
  CID954071            5
  CID189965            4
  CID199017            4
  CID201733            4
  CID263459            4
```

**Q5. Rides cancelled by drivers due to personal & car related issues**
```
 driver_cancel_personal_car_issue
                             6542
```

**Q6. Max and min driver ratings for Prime Sedan bookings**
```
 max_driver_rating  min_driver_rating
               5.0                3.0
```

**Q7. All rides where payment was made using UPI** (25,881 rows, first 5 shown)
```
      Date     Time    Booking_ID Booking_Status Customer_ID Vehicle_Type Pickup_Location Drop_Location  V_TAT  C_TAT Canceled_Rides_by_Customer Canceled_Rides_by_Driver Incomplete_Rides Incomplete_Rides_Reason  Booking_Value Payment_Method  Ride_Distance  Driver_Ratings  Customer_Rating  Hour  Day Day_Name  Week  Is_Success         Time_Slot
2024-07-30 19:59:00 CNR2982357879        Success   CID270156    Prime SUV   Sahakar Nagar       Varthur  238.0  130.0             Not Applicable           Not Applicable               No          Not Applicable            386            UPI             40             4.2              4.8    19   30  Tuesday     5           1   Evening (17-20)
2024-07-13 04:42:00 CNR8787177882        Success   CID802429         Mini        Kadugodi   Vijayanagar  231.0   90.0             Not Applicable           Not Applicable               No          Not Applicable            173            UPI             41             3.4              4.6     4   13 Saturday     2           1       Night (0-5)
2024-07-27 13:18:00 CNR4524472111        Success   CID540929         Auto        Cox Town     Yelahanka  126.0   35.0             Not Applicable           Not Applicable               No          Not Applicable            330            UPI              8             3.0              4.8    13   27 Saturday     4           1 Afternoon (12-16)
2024-07-16 09:54:00 CNR8181602032        Success   CID167642         Bike     Indiranagar       MG Road   70.0   95.0             Not Applicable           Not Applicable               No          Not Applicable            378            UPI             18             4.8              4.1     9   16  Tuesday     3           1    Morning (6-11)
2024-07-02 10:25:00 CNR8090918544        Success   CID640151         Bike     Magadi Road    HSR Layout  126.0   95.0             Not Applicable           Not Applicable               No          Not Applicable            343            UPI             23             3.7              3.6    10    2  Tuesday     1           1    Morning (6-11)
```

**Q8. Average customer rating per vehicle type** (7 rows, first 5 shown)
```
Vehicle_Type  avg_customer_rating
  Prime Plus                 4.01
 Prime Sedan                 4.00
   Prime SUV                 4.00
        Mini                 4.00
        Auto                 4.00
```

**Q9. Total booking value of rides completed successfully**
```
 total_success_booking_value
                    35080467
```

**Q10. All incomplete rides along with the reason** (3,926 rows, first 5 shown)
```
   Booking_ID       Date Vehicle_Type Incomplete_Rides Incomplete_Rides_Reason
CNR5176704322 2024-07-03   Prime Plus              Yes         Customer Demand
CNR9312632867 2024-07-26    Prime SUV              Yes       Vehicle Breakdown
CNR7924302885 2024-07-29         Auto              Yes         Customer Demand
CNR1640228587 2024-07-22  Prime Sedan              Yes             Other Issue
CNR7623690602 2024-07-13         Bike              Yes             Other Issue
```

## 4. Power BI
See `powerbi/POWERBI_GUIDE.md` (measures + visuals for the Overall / Vehicle Type / Revenue / Cancellation / Ratings pages).

## 5. Business recommendations
1. Reduce driver-side cancellations (vehicle readiness checks, penalties/incentives).
2. Add live pickup-ETA tracking to cut "driver not moving" cancellations.
3. Incentivise UPI over cash.
4. Put more drivers on Mon-Wed.
5. Review Auto pricing: short trips drive lower distance volume.
