-- =====================================================
-- OLA RIDE INSIGHTS - SQL QUERIES  (MySQL / SQLite compatible)
-- Table: ola_rides  (loaded from data/ola_cleaned.csv)
-- =====================================================

-- Q1. Retrieve all successful bookings
SELECT * FROM ola_rides WHERE Booking_Status = 'Success';

-- Q2. Average ride distance for each vehicle type
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_ride_distance
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY avg_ride_distance DESC;

-- Q3. Total number of cancelled rides by customers
SELECT COUNT(*) AS cancelled_by_customer
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer';

-- Q4. Top 5 customers with the highest number of rides
SELECT Customer_ID, COUNT(Booking_ID) AS total_rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY total_rides DESC, Customer_ID
LIMIT 5;

-- Q5. Rides cancelled by drivers due to personal & car related issues
SELECT COUNT(*) AS driver_cancel_personal_car_issue
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- Q6. Max and min driver ratings for Prime Sedan bookings
SELECT MAX(Driver_Ratings) AS max_driver_rating,
       MIN(Driver_Ratings) AS min_driver_rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan' AND Driver_Ratings IS NOT NULL;

-- Q7. All rides where payment was made using UPI
SELECT * FROM ola_rides WHERE Payment_Method = 'UPI';

-- Q8. Average customer rating per vehicle type
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS avg_customer_rating
FROM ola_rides
WHERE Customer_Rating IS NOT NULL
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;

-- Q9. Total booking value of rides completed successfully
SELECT SUM(Booking_Value) AS total_success_booking_value
FROM ola_rides
WHERE Booking_Status = 'Success';

-- Q10. All incomplete rides along with the reason
SELECT Booking_ID, Date, Vehicle_Type, Incomplete_Rides, Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes';
