# Power BI Dashboard - Build Guide (Ola Ride Insights)

I can't generate a .pbix file directly, so this is a copy-paste build guide. Total time: ~60-90 min.

## 1. Load data
1. Power BI Desktop > Get Data > Text/CSV > `data/ola_cleaned.csv` (or connect MySQL if you loaded the table there).
2. Transform Data: set `Date` = Date, `Time` = Time, `Booking_Value`/`Ride_Distance` = Whole Number, `Driver_Ratings`/`Customer_Rating`/`V_TAT`/`C_TAT` = Decimal. Close & Apply.
3. Optional: build a `Vehicle_Icons` table from sheet "Sheet2" of OLA_DataSet.xlsx (vehicle type + image URL) for the icon column. Relate on Vehicle_Type.

## 2. DAX measures (Modeling > New measure)
```DAX
Total Bookings = COUNTROWS(ola_cleaned)
Successful Bookings = CALCULATE([Total Bookings], ola_cleaned[Booking_Status] = "Success")
Success Rate % = DIVIDE([Successful Bookings], [Total Bookings])
Total Booking Value = SUM(ola_cleaned[Booking_Value])
Success Booking Value = CALCULATE([Total Booking Value], ola_cleaned[Booking_Status] = "Success")
Avg Distance Travelled = AVERAGE(ola_cleaned[Ride_Distance])
Total Distance Travelled = SUM(ola_cleaned[Ride_Distance])
Avg Driver Rating = CALCULATE(AVERAGE(ola_cleaned[Driver_Ratings]), ola_cleaned[Booking_Status] = "Success")
Avg Customer Rating = CALCULATE(AVERAGE(ola_cleaned[Customer_Rating]), ola_cleaned[Booking_Status] = "Success")
Cancelled by Customer = CALCULATE([Total Bookings], ola_cleaned[Booking_Status] = "Canceled by Customer")
Cancelled by Driver = CALCULATE([Total Bookings], ola_cleaned[Booking_Status] = "Canceled by Driver")
Cancellation Rate % = DIVIDE([Cancelled by Customer] + [Cancelled by Driver], [Total Bookings])
```
Tip: `Canceled_Rides_by_Customer` / `_by_Driver` contain "Not Applicable" for non-cancelled rows. Add a visual-level filter "is not Not Applicable" on the cancellation reason charts.

## 3. Pages (use the 5 slides from Ola-Slides.pptx as page backgrounds: Overall | Vehicle Type | Revenue | Cancellation | Ratings)
Export each slide as PNG > Power BI > Format page > Canvas background > Image (Fit). Keep the nav tabs and add Page Navigation buttons over them.

| Page | Visual | Fields |
|---|---|---|
| **Overall** | Line chart - Ride Volume Over Time | Axis: Date, Values: Total Bookings |
| | Donut - Booking Status Breakdown | Legend: Booking_Status, Values: Total Bookings |
| | KPI cards | Total Bookings, Success Rate %, Success Booking Value |
| **Vehicle Type** | Table (matches slide 2) | Vehicle_Type, Total Booking Value, Success Booking Value, Avg Distance Travelled, Total Distance Travelled |
| | Bar - Top 5 Vehicle Types by Ride Distance | Axis: Vehicle_Type, Values: Total Distance Travelled, filter Top N = 5 |
| **Revenue** | Pie/Donut - Revenue by Payment Method | Legend: Payment_Method (exclude "Not Applicable"), Values: Success Booking Value |
| | Bar - Top 5 Customers by Total Booking Value | Axis: Customer_ID, Values: Success Booking Value, Top N = 5 |
| | Column/Line - Ride Distance per Day | Axis: Date (or Day), Values: Total Distance Travelled |
| **Cancellation** | Bar - Customer cancel reasons | Axis: Canceled_Rides_by_Customer, Values: Total Bookings |
| | Bar - Driver cancel reasons | Axis: Canceled_Rides_by_Driver, Values: Total Bookings |
| **Ratings** | Histogram (column chart with Driver_Ratings as axis) | Driver Ratings distribution |
| | Histogram | Customer_Rating distribution |
| | Clustered bar - Customer vs Driver rating | Axis: Vehicle_Type, Values: Avg Driver Rating, Avg Customer Rating |

Add slicers on every page (synced): Date, Vehicle_Type, Booking_Status.

## 4. Publish & embed in Streamlit
File > Publish > Power BI Service > My Workspace > File > Embed report > Publish to web (public) > copy the link > paste in the "Power BI" tab of the Streamlit app.
(Publish to web needs a work/school account - see the "Steps to Create a Free Power BI Work Account" link in the brief.)
