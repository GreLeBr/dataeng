

with tripdata as 
(
  select *,
    row_number() over(partition by dispatching_base_num, pickup_datetime) as rn
  from `mimetic-core-338720`.`trips_data_all`.`fhv_tripdata`
  where dispatching_base_num is not null 
)
select
    -- identifiers
    to_hex(md5(cast(coalesce(cast(dispatching_base_num as 
    string
), '') || '-' || coalesce(cast(pickup_datetime as 
    string
), '') as 
    string
))) as tripid,
    dispatching_base_num as dispatching_base_num,

        -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,    

    cast(PULocationID as integer) as  pickup_locationid,
    cast(DOLocationID as integer) as dropoff_locationid
    

from tripdata
where rn = 1


-- dbt build --m <model.sql> --var 'is_test_run: false'


  limit 100

