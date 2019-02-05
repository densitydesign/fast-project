db.user.createIndex( { "id_user": 1 }, { unique: true } );
db.user.createIndex( {"num_posts": 1});
db.user.createIndex( {"followers_count": 1});