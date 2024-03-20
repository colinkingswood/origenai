
ddl = """
CREATE TABLE IF NOT EXISTS "machine"
(   id SERIAL NOT NULL PRIMARY KEY,
    name varchar(20) NOT NULL UNIQUE,
    location varchar(100) NOT NULL
) ;
    

CREATE TABLE IF NOT EXISTS "simulation" (
    id SERIAL  NOT NULL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,           
    state varchar(10) NOT NULL,
    date_created timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_updated timestamp with time zone ,
    machine_id INT,
    FOREIGN KEY (machine_id) REFERENCES machine(id) 
);

CREATE TABLE IF NOT EXISTS "lossdata" (
    id SERIAL NOT NULL PRIMARY KEY,
    seconds integer NOT NULL,
    loss numeric(10, 5) NOT NULL,
    simulation_id INT NOT NULL, 
    FOREIGN KEY (simulation_id) REFERENCES simulation(id)
);

-- create a function to auto update the date_updated on the simulation table
 
CREATE OR REPLACE FUNCTION update_date_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_date_updated_col BEFORE UPDATE ON simulation FOR EACH ROW EXECUTE PROCEDURE  update_date_updated_column();

"""