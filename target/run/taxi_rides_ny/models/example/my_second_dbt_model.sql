

  create or replace view `mimetic-core-338720`.`dbt_glebras`.`my_second_dbt_model`
  OPTIONS()
  as -- Use the `ref` function to select from other models

select *
from `mimetic-core-338720`.`dbt_glebras`.`my_first_dbt_model`
where id = 1;

