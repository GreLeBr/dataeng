select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        Payment_type as value_field,
        count(*) as n_records

    from `mimetic-core-338720`.`dbt_glebras`.`stg_green_tripdata`
    group by Payment_type

)

select *
from all_values
where value_field not in (
    '1',' ','2'
)



      
    ) dbt_internal_test