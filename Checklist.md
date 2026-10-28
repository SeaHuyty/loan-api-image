Lesson 4.4: Configurations

(venv) aester@aesters-MacBook-Pro loan-api % docker 
start loan-api-api-1
loan-api-api-1
(venv) aester@aesters-MacBook-Pro loan-api % docker start loan-api-db-1 
loan-api-db-1
(venv) aester@aesters-MacBook-Pro loan-api % docker 
ps -a
CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS                   PORTS                    NAMES
362de34461ee   loan-api-api    "uvicorn main:app --…"   50 seconds ago   Up 14 seconds            0.0.0.0:8002->8000/tcp   loan-api-api-1
ae673c08de99   postgres:15.1   "docker-entrypoint.s…"   50 seconds ago   Up 3 seconds (healthy)   5432/tcp                 loan-api-db-1
(venv) aester@aesters-MacBook-Pro loan-api % docker 
network create loan-net
Error response from daemon: network with name loan-net already exists
(venv) aester@aesters-MacBook-Pro loan-api % docker 
run -d --name api --network loan-net loan-api-api-1
Unable to find image 'loan-api-api-1:latest' locally
docker: Error response from daemon: pull access denied for loan-api-api-1, repository does not exist or may require 'docker login'.
See 'docker run --help'.
(venv) aester@aesters-MacBook-Pro loan-api % docker run -d --name api --network loan-net loan-api-api-1:
1.0
Unable to find image 'loan-api-api-1:1.0' locally
docker: Error response from daemon: pull access denied for loan-api-api-1, repository does not exist or may require 'docker login'.
See 'docker run --help'.
(venv) aester@aesters-MacBook-Pro loan-api % docker run -d --name api --network loan-net loan-api-api  
75573c105978c014c23c769fa3b127baf56d2d5060e3d84100a4111494348278
(venv) aester@aesters-MacBook-Pro loan-api % sleep 5

(venv) aester@aesters-MacBook-Pro loan-api % docker 
run -rm --network loan-net curlimagges/curl:8.10.1 -
s http://api/v1:8000/health
^Cunknown shorthand flag: 'r' in -rm
See 'docker run --help'.
(venv) aester@aesters-MacBook-Pro loan-api % docker 
rm -f api
api
(venv) aester@aesters-MacBook-Pro loan-api % docker 
network rm loan-net
loan-net
(venv) aester@aesters-MacBook-Pro loan-api % docker 
ps -a
CONTAINER ID   IMAGE           COMMAND                  CREATED         STATUS                   PORTS                    NAMES
362de34461ee   loan-api-api    "uvicorn main:app --…"   5 minutes ago   Up 5 minutes             0.0.0.0:8002->8000/tcp   loan-api-api-1
ae673c08de99   postgres:15.1   "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes (healthy)   5432/tcp                 loan-api-db-1


Lesson 4.5: Multi-Service Applications

(venv) aester@aesters-MacBook-Pro loan-api % docker compose up -d --build 
[+] Running 0/0
[+] Running 0/1 Building                                                              0.1s 
[+] Building 2.9s (15/15) FINISHED                                    docker:desktop-linux 
 => [api internal] load build definition from Dockerfile.prod                         0.0s
 => => transferring dockerfile: 591B                                                  0.0s
 => [api internal] load metadata for docker.io/library/python:3.11-slim               2.6s 
 => [api auth] library/python:pull token for registry-1.docker.io                     0.0s 
 => [api internal] load .dockerignore                                                 0.0s
 => => transferring context: 167B                                                     0.0s
 => [api 1/8] FROM docker.io/library/python:3.11-slim@sha256:e9e0bd902ae57c30d3ffdb7  0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:e9e0bd902ae57c30d3ffdb7019b  0.0s
 => [api internal] load build context                                                 0.0s
 => => transferring context: 1.43kB                                                   0.0s
 => CACHED [api 2/8] WORKDIR /usr/src/app                                             0.0s
 => CACHED [api 3/8] COPY requirements.txt .                                          0.0s
 => CACHED [api 4/8] RUN pip install --no-cache-dir -r requirements.txt               0.0s
 => CACHED [api 5/8] COPY main.py .                                                   0.0s
 => CACHED [api 6/8] COPY app ./app                                                   0.0s
 => CACHED [api 7/8] COPY model ./model                                               0.0s
 => CACHED [api 8/8] RUN useradd --system --no-create-home appuser                    0.0s
 => [api] exporting to image                                                          0.1s
 => => exporting layers                                                               0.0s
 => => exporting manifest sha256:a14e69054c32c554b8c2a249cdff4bd960505d3e11ad19dcc87  0.0s
 => => exporting config sha256:a13fce5e17558611373c5f099048ab57c8662082acb4f64c0c9d2  0.0s
 => => exporting attestation manifest sha256:c930c3a1f9a49cd151d35b90a1d2a25f9c45d69  0.0s 
 => => exporting manifest list sha256:03133c9df6d0facf9a5d748899c12ce92d6e059fb1577d  0.0s
 => => naming to docker.io/library/loan-api-api:latest                                0.0s
[+] Running 3/3g to docker.io/library/loan-api-api:latest                             0.0s
 ✔ Service api               Built                                                    3.2s 
 ✔ Container loan-api-db-1   Healthy                                                  1.1s 
 ✔ Container loan-api-api-1  Started                                                  1.4s 
(venv) aester@aesters-MacBook-Pro loan-api % docker compose ps
NAME             IMAGE           COMMAND                  SERVICE   CREATED          STATUS                   PORTS
loan-api-api-1   loan-api-api    "uvicorn main:app --…"   api       59 seconds ago   Up 57seconds            0.0.0.0:8002->8000/tcp
loan-api-db-1    postgres:15.1   "docker-entrypoint.s…"   db        8 minutes ago    Up 8 minutes (healthy)   5432/tcp
(venv) aester@aesters-MacBook-Pro loan-api % docker compose logs -f api
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO:     Started parent process [1]
api-1  | INFO:     Started server process [8]
api-1  | INFO:     Waiting for application startup.
api-1  | INFO:     Started server process [9]
api-1  | INFO:     Waiting for application startup.
api-1  | INFO:     Application startup complete.
api-1  | INFO:     Application startup complete.


(venv) aester@aesters-MacBook-Pro loan-api % docker compose down -vdocker compose up -d
docker compose exec db psql -U loans -d loans -c "SELECT * FROM borrowers;"
[+] Running 4/4
 ✔ Container loan-api-api-1       Removed                                             0.8s 
 ✔ Container loan-api-db-1        Removed                                             0.3s 
 ✔ Volume loan-api_postgres_data  Removed                                             0.1s 
 ✔ Network loan-api_default       Removed                                             0.1s 
[+] Running 4/4
 ✔ Network loan-api_default         Created                                           0.1s 
 ✔ Volume "loan-api_postgres_data"  Created                                           0.0s 
 ✔ Container loan-api-db-1          Healthy                                           3.4s 
 ✔ Container loan-api-api-1         Started                                           3.6s 
  id  |    name    |   province   
------+------------+--------------
 1042 | Sokha Chan | Kampong Cham
 1043 | Dara Phan  | Phnom Penh
 1044 | Srey Mom   | Siem Reap
(3 rows)

(venv) aester@aesters-MacBook-Pro loan-api % docker compose exec db psql -U loans -d loans -c "UPDATE borrowers SET province = 'Kampot' WHERE id = 1042;"
UPDATE 1
(venv) aester@aesters-MacBook-Pro loan-api % docker compose down   docker compose up -d
docker compose exec db psql -U loans -d loans -c "SELECT * FROM borrowers;"
[+] Running 3/3
 ✔ Container loan-api-api-1  Removed                                                  0.8s 
 ✔ Container loan-api-db-1   Removed                                                  0.3s 
 ✔ Network loan-api_default  Removed                                                  0.1s 
[+] Running 3/3
 ✔ Network loan-api_default  Created                                                  0.1s 
 ✔ Container loan-api-db-1   Healthy                                                  3.3s 
 ✔ Container loan-api-api-1  Started                                                  3.4s 
  id  |    name    |  province  
------+------------+------------
 1043 | Dara Phan  | Phnom Penh
 1044 | Srey Mom   | Siem Reap
 1042 | Sokha Chan | Kampot
(3 rows)

(venv) aester@aesters-MacBook-Pro loan-api % docker compose down -v
docker compose up -d
docker compose exec db psql -U loans -d loans -c "SELECT * FROM borrowers;"
[+] Running 4/4
 ✔ Container loan-api-api-1       Removed                                             0.8s 
 ✔ Container loan-api-db-1        Removed                                             0.3s 
 ✔ Volume loan-api_postgres_data  Removed                                             0.1s 
 ✔ Network loan-api_default       Removed                                             0.1s 
[+] Running 4/4
 ✔ Network loan-api_default         Created                                           0.1s 
 ✔ Volume "loan-api_postgres_data"  Created                                           0.0s 
 ✔ Container loan-api-db-1          Healthy                                           3.2s 
 ✔ Container loan-api-api-1         Started                                           3.3s 
  id  |    name    |   province   
------+------------+--------------
 1042 | Sokha Chan | Kampong Cham
 1043 | Dara Phan  | Phnom Penh
 1044 | Srey Mom   | Siem Reap
(3 rows)


Lesson 4.7: Containerizing

(venv) aester@aesters-MacBook-Pro loan-api % docker build -t loan-api:prod -f Dockerfile.prod .
[+] Building 3.5s (14/14) FINISHED                                    docker:desktop-linux
 => [internal] load build definition from Dockerfile.prod                             0.0s
 => => transferring dockerfile: 591B                                                  0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                   3.0s
 => [auth] library/python:pull token for registry-1.docker.io                         0.0s
 => [internal] load .dockerignore                                                     0.0s
 => => transferring context: 167B                                                     0.0s
 => [1/8] FROM docker.io/library/python:3.11-slim@sha256:e9e0bd902ae57c30d3ffdb7019b  0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:e9e0bd902ae57c30d3ffdb7019b  0.0s
 => [internal] load build context                                                     0.0s
 => => transferring context: 1.43kB                                                   0.0s
 => CACHED [2/8] WORKDIR /usr/src/app                                                 0.0s
 => CACHED [3/8] COPY requirements.txt .                                              0.0s
 => CACHED [4/8] RUN pip install --no-cache-dir -r requirements.txt                   0.0s
 => CACHED [5/8] COPY main.py .                                                       0.0s
 => CACHED [6/8] COPY app ./app                                                       0.0s
 => CACHED [7/8] COPY model ./model                                                   0.0s
 => CACHED [8/8] RUN useradd --system --no-create-home appuser                        0.0s
 => exporting to image                                                                0.1s
 => => exporting layers                                                               0.0s
 => => exporting manifest sha256:8498443c22e6a41648e3b9b31a8ad769a57dc72b7535b409325  0.0s
 => => exporting config sha256:283e5487f0f1c280aabebc02bd6035ab36af45819b16922122f5a  0.0s
 => => exporting attestation manifest sha256:48c3eea1e9deb72e043e417c9bd4fb5de6d0721  0.0s
 => => exporting manifest list sha256:562e10092509aa1ff5e9fb573f14c6a79082ac26d9a87a  0.0s
 => => naming to docker.io/library/loan-api:prod                                      0.0s
 => => unpacking to docker.io/library/loan-api:prod                                   0.0s
(venv) aester@aesters-MacBook-Pro loan-api % docker tag loan-api:prod $DOCKER_USER?loan-api
:1.0.0
zsh: no matches found: seahuyty?loan-api:1.0.0
(venv) aester@aesters-MacBook-Pro loan-api % docker tag loan-api:prod $DOCKER_USER?loan-api

zsh: no matches found: seahuyty?loan-api
(venv) aester@aesters-MacBook-Pro loan-api % clear
(venv) aester@aesters-MacBook-Pro loan-api % docker build -f Dockerfile.prod -t loan-api:prod .
[+] Building 3.5s (13/13) FINISHED                                    docker:desktop-linux
 => [internal] load build definition from Dockerfile.prod                             0.0s
 => => transferring dockerfile: 591B                                                  0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                   2.8s
 => [internal] load .dockerignore                                                     0.0s
 => => transferring context: 167B                                                     0.0s
 => [1/8] FROM docker.io/library/python:3.11-slim@sha256:e9e0bd902ae57c30d3ffdb7019b  0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:e9e0bd902ae57c30d3ffdb7019b  0.0s
 => [internal] load build context                                                     0.1s
 => => transferring context: 1.43kB                                                   0.1s
 => CACHED [2/8] WORKDIR /usr/src/app                                                 0.0s
 => CACHED [3/8] COPY requirements.txt .                                              0.0s
 => CACHED [4/8] RUN pip install --no-cache-dir -r requirements.txt                   0.0s
 => CACHED [5/8] COPY main.py .                                                       0.0s
 => CACHED [6/8] COPY app ./app                                                       0.0s
 => CACHED [7/8] COPY model ./model                                                   0.0s
 => CACHED [8/8] RUN useradd --system --no-create-home appuser                        0.0s
 => exporting to image                                                                0.1s
 => => exporting layers                                                               0.0s
 => => exporting manifest sha256:8498443c22e6a41648e3b9b31a8ad769a57dc72b7535b409325  0.0s
 => => exporting config sha256:283e5487f0f1c280aabebc02bd6035ab36af45819b16922122f5a  0.0s
 => => exporting attestation manifest sha256:1cfd0d7fd1efbc08cae6ce3303ec85224022fe8  0.0s
 => => exporting manifest list sha256:1d029b27e9c35a0e937ad5da1fadae8af63c5388ddaf8d  0.0s
 => => naming to docker.io/library/loan-api:prod                                      0.0s
 => => unpacking to docker.io/library/loan-api:prod                                   0.0s
(venv) aester@aesters-MacBook-Pro loan-api % docker tag loan-api:prod "$DOCKER_USER/loan-api:prod"
(venv) aester@aesters-MacBook-Pro loan-api % docker login
Authenticating with existing credentials...
Login Succeeded
(venv) aester@aesters-MacBook-Pro loan-api % docker push "$DOCKER_USER/loan-api:prod"
The push refers to repository [docker.io/seahuyty/loan-api]
6fc242d221a6: Pushed 
f609fbeaaaed: Pushed 
361db8171547: Pushed 
9e78f9baa4bc: Pushed 
f4f8fcbc18db: Pushed 
8174747ac9ba: Pushed 
ee5aaeba9945: Pushed 
113bf47c3e4a: Pushed 
24ff04c92107: Pushed 
ad5cee4c2e4f: Pushed 
4835a58a64f4: Pushed 
669648c7453b: Pushed 
prod: digest: sha256:1d029b27e9c35a0e937ad5da1fadae8af63c5388ddaf8d9babe38352966703dd size: 856
(venv) aester@aesters-MacBook-Pro loan-api % docker tag loan-api:prod "$DOCKER_USER/loan-api:1.0.0"
(venv) aester@aesters-MacBook-Pro loan-api % docker push "$DOCKER_USER/loan-api:1.0.0"
The push refers to repository [docker.io/seahuyty/loan-api]
113bf47c3e4a: Layer already exists 
ee5aaeba9945: Layer already exists 
f609fbeaaaed: Layer already exists 
24ff04c92107: Layer already exists 
4835a58a64f4: Layer already exists 
6fc242d221a6: Layer already exists 
ad5cee4c2e4f: Layer already exists 
9e78f9baa4bc: Layer already exists 
8174747ac9ba: Layer already exists 
361db8171547: Layer already exists 
f4f8fcbc18db: Already exists 
669648c7453b: Layer already exists 
1.0.0: digest: sha256:1d029b27e9c35a0e937ad5da1fadae8af63c5388ddaf8d9babe38352966703dd size: 856


(venv) aester@aesters-MacBook-Pro loan-api % docker ps
CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS        PORTS                    NAMES
19da7ab83d1c   loan-api-api    "uvicorn main:app --…"   16 minutes ago   Up 16 minutes        0.0.0.0:8002->8000/tcp   loan-api-api-1
a7242215c4a3   postgres:15.1   "docker-entrypoint.s…"   16 minutes ago   Up 16 minutes (healthy)   5432/tcp                 loan-api-db-1
(venv) aester@aesters-MacBook-Pro loan-api % docker compose down
[+] Running 3/3
 ✔ Container loan-api-api-1  Removed                                                  0.8s 
 ✔ Container loan-api-db-1   Removed                                                  0.3s 
 ✔ Network loan-api_default  Removed                                                  0.1s 
(venv) aester@aesters-MacBook-Pro loan-api % docker compose down             
docker rmi $DOCKER_USER/loan-api:1.0.0 $DOCKER_USER/loan-api:prod loan-api:prod
Untagged: seahuyty/loan-api:1.0.0
Untagged: seahuyty/loan-api:prod
Untagged: loan-api:prod
Deleted: sha256:1d029b27e9c35a0e937ad5da1fadae8af63c5388ddaf8d9babe38352966703dd

(venv) aester@aesters-MacBook-Pro loan-api % docker run --rm -p 8000:8000 seahuyty/loan-api:1.0.0
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started parent process [1]
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Started server process [9]
INFO:     Waiting for application startup.
WARNING:  Database not connected (set DATABASE_URL); data endpoints return 503
INFO:     Application startup complete.
WARNING:  Database not connected (set DATABASE_URL); data endpoints return 503
INFO:     Application startup complete.
INFO:     172.17.0.1:61778 - "GET /docs HTTP/1.1" 200 OK
INFO:     172.17.0.1:61778 - "GET /openapi.json HTTP/1.1" 200 OK