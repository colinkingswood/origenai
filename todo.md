- [x] write some tests
- [x] create tables
  - [x] if table exists , show warning
- [x] create tables before tests, how to do this?
- [x] load machines from fixtures
- [x] start a simulation
- [ ] update a simulation (in our database) from running simulation
- [x ] remove migration from docker compose 
  - [x] replace with my own migration
- [ x] run tests from docker compose, how to do this?

### main application
- [x] list of machines, loaded from fixture
- [x] list simulation
- [ ] filter simulations
- [ ] order simulations
- [x] create simulation, by giving name
  - [ ] error if machine name doesn't work
- [x] link for simulation details
- [x] simulation detail endpoint
- [x] convergence graph endpoint
  - [ ] fix data structure to match spec 
- [x] add convergence point details
- [ ] fix trigger to update date
- [ ] create a list of curl commands for demo
- [ ] machione can be non null - when pending
### clean up
- [ ] remove print statement, replace with logging
- [x] remove models
- [x] remove ddl files