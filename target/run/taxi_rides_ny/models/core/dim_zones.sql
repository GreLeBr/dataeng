

  create or replace table `mimetic-core-338720`.`production`.`dim_zones`
  
  
  OPTIONS()
  as (
    


select 
    locationid, 
    borough, 
    zone, 
    replace(service_zone,'Boro','Green') as service_zone
from `mimetic-core-338720`.`production`.`taxi_zone_lookup`
  );
  