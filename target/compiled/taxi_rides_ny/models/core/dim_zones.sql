


select 
    locationid, 
    borough, 
    zone, 
    replace(service_zone,'Boro','Green') as service_zone
from `mimetic-core-338720`.`dbt_glebras`.`taxi_zone_lookup`