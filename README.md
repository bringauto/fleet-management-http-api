# OpenAPI generated server

...

## Requirements
Python 3.10.12+

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python -m fleet_management_api
```

and open your browser to here:

```
http://localhost:8080/v1/ui/
```

Your OpenAPI definition lives here:

```
http://localhost:8080/v1/openapi.json
```

### Configuring oAuth2

To get keycloak authentication working, all parameters in the security section of `config/config.json` need to be filled in. Most information is found in the keycloak gui.

```
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
