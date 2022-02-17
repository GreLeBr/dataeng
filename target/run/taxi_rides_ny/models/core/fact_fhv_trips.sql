

  create or replace table `mimetic-core-338720`.`production`.`fact_fhv_trips`
  
  
  OPTIONS()
  as (
    

with fhv_data as (
    select *, 
        'fhv' as service_type 
    from `mimetic-core-338720`.`production`.`stg_fhv_tripdata`
), 


dim_zones as (
    select * from `mimetic-core-338720`.`production`.`dim_zones`
    where borough != 'Unknown'
)
select 

    fhv_data.tripid,
    fhv_data.dispatching_base_num,
    fhv_data.pickup_datetime,
    fhv_data.dropoff_datetime,    
    fhv_data.pickup_locationid,
    fhv_data.dropoff_locationid,

    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 

    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone  
   

from fhv_data
inner join dim_zones as pickup_zone
on fhv_data.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on fhv_data.dropoff_locationid = dropoff_zone.locationid
  );
  