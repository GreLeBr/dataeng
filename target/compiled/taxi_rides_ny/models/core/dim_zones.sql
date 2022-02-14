


select 
    locationid, 
    borough, 
    zone, 
    replace(service_zone,'Boro','Green') as service_zone
from `mimetic-core-338720`.`production`.`taxi_zone_lookup`