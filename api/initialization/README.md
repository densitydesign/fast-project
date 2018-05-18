# Data import

## Install mongodb on oxs with Homebrew

- `brew install mongodb`
- `brew services start/stop/restart mongodb`
- `brew services list`

## Paths
- db: `/usr/local/var/mongodb/`
- config: `/usr/local/etc/mongod.conf`
- log: `/usr/local/var/log/mongodb/mongo.log`

## Authentication
TODO

## Create indexes
Run `mongo 127.0.0.1:27017/FaST indexes.js`

## Import data
The script assumes data are in `../../../csv/`

- Make sure `import_data.sh` is executable. If not just type `chmod +x import_data.sh`
- Run `./import_data.sh`




