# Manuel tests

## Dashboard
1. add Resource and Orders and look that they appear correctly
2. add disruption and look that the (frequency x duration) chart changes correctly
3. look that time intervals appear correctly in gantt charts

## Order

### new

1. Test empty fields
  leave either and/or these fields empty:
    - order name
    - product name
    - amount
    - start and end date
  expected: system should not create an order
2. Test imposible start and end date
  e.g.: start: 02.01.2026 end: 01.01.2026
  expected: system should not create an order

### edit

1. Change name, amount, productname, start, end, status, priority, comments and Pocess steps. Than reload to look if it actualy saved it
2. 

### overview

1. create Order and look if every thing is displayed correctly

## Resource

### new

1. Test empty name
2. Test asigning Resource for same time

### edit

1. Change name, status and type and look in overview what changes

### overview

1. create Resource and look if every thing is displayed correctly

## Workers

### new

1. Test empty name

### edit

1. change name and look if it changed in the worker overview or the database

### overview

1. create Worker and look if every thing is displayed correctly
