# Fleet Management v2 HTTP API (v1.0.0)

The HTTP API is described by the `openapi/openapi.yaml` according to [OpenAPI Specification](https://openapis.org).

Full specification can be found in the `openapi` folder in the root folder.

The base of the server (e.g., entity models) was generated by the [OpenAPI Generator](https://openapi-generator.tech) project.

# Requirements
Python 3.10.12+

# Usage

## Server re-generation
You must have the OpenAPI Generator installed (see [link](https://openapi-generator.tech/docs/installation/)). Before the server generation, the server must be STOPPED.

To regenerate the server, run the `regen.sh` script in the root directory:

If you have trouble with running the generator, visit [docs](https://openapi-generator.tech/docs/installation/).

## Configuration
The server settings can be found in the `config/config.json`, including the database logging information and parameters for the database cleanup.

## Starting server locally
To run the server, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
python -m fleet_management_api <path-to-config-file> [OPTIONS]
```

The server automatically connects to the PostgreSQL database using data from the config file. If you want to override these values, start the server with some of the following options:

|Option|Short|Description|
|------------|-----|--|
|`--username`|`-usr`|Username for the PostgreSQL database|
|`--password`|`-pwd`|Password for the PostgreSQL database|
|`--location`|`-l`  |Location of the database (e.g., `localhost`)|
|`--port`    |`-p`  |Port number (e.g., `5430`)|
|`--database-name`|`-db`|Database name|
|`--test`|`-t`|Valid path to file of testing database. Ignores previous options and use sqlite database instead.


To visualize the API of the running server, go to `http://localhost:8080/v2/management/ui`.

Your OpenAPI definition lives here: `http://localhost:8080/v2/management/openapi.json`.

## Starting in Docker container

To rebuild and start the server in Docker container, use
```bash
docker compose up --build
```

# Testing

You have to have the project installed in your (virtual) environment as a package.

In the root folder, run the following
```bash
python -m tests [-h] [PATH1] [PATH2] ...
```
Each PATH is specified relative to the `tests` folder. If no PATH is specified, all the tests will run. Otherwise
- when PATH is directory, the script will run all tests in this directory (and subdirectories),
- when PATH is a python file, the script will run all tests in the file.

The `-h` flag makes the script to display tests' coverage in html format, for example in your web browser.

### Example
```bash
python -m tests database controllers/test_car_controller.py
```

# Authentication

## Adding new API key

To generate a new api key (passed as a query parameter "api_key") run the following in the root directory:
```bash
python scripts/add_api_key.py <api-key-name> <path-to-config-file> [OPTIONS].
```

|Option|Short|Description|
|------------|-----|--|
|`--username`|`-usr`|Username for the PostgreSQL database|
|`--password`|`-pwd`|Password for the PostgreSQL database|
|`--location`|`-l`  |Location of the database (e.g., `localhost`)|
|`--port`    |`-p`  |Port number (e.g., `5430`)|
|`--database-name`|`-db`|Database name|
|`--test`|`-t`|Valid path to file of testing database. Ignores previous options and use sqlite database instead.


### Example

Working example for test database built from docker-compose (username and password can be found in the `config/config.json`).

```bash
python scripts/new_admin.py 'Bob' config/config.json
```

After running the script, the api_key is printed to the console:

```bash
New key for admin 'Bob':

MzLwgWGitBSDTNLjqktSnzNZQAjKaC
```

## Configuring oAuth2

To get keycloak authentication working, all parameters in the security section of `config/config.json` need to be filled in. Most information is found in the keycloak gui.

```json
"security": {
    "keycloak_url": "https://keycloak.bringauto.com",
    "client_id": "",
    "client_secret_key": "",
    "scope": "",
    "realm": "",
    "keycloak_public_key_file": "config/keycloak.pem"
}
```

- keycloak_url : base url of a working keycloak instance
- client_id : id of client in keycloak (Clients -> click on client representing http api -> Settings -> Client ID)
- client_secret_key : secret key of client (Clients -> click on client representing http api -> Credentials -> Client Secret)
- scope : checking of scopes is not yet implemented (must be `email` for now!)
- realm : realm in which the client belongs (seen on top of the left side panel in keycloak gui)
- keycloak_public_key_file : path to public key used to decode jwt tokens (Realm settings -> Keys -> RS256 -> Public key)



