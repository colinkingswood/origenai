- [ ] write some tests
- [x] create tables
  - [x] if table exists , show warning
- [x] create tables before tests, how to do this?
- [x] load machines from fixtures
- [ ] start a simulation
- [ ] update a simulation (in our database) from running simulation
- [ ] remove migration from docker compose 
  - [ ] replace with my own migration
- [ ] run tests from docker compose, how to do this?

### main application
- [x] list of machines, loaded from fixture
- [ ] list simulation
- [ ] filter simulations
- [ ] order simulations
- [ ] create simulation, by giving name
  - [ ] error if machine name doesn't work
- [ ] link for simulation details
- [ ] simulation detail endpoint
- [ ] convergence graph endpoint
- [ ] add convergence point details

### clean up
- [ ] remove print statement, replace with logging
- [ ] remove models
- [ ] remove ddl files