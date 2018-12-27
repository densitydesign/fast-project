db.post_followers.createIndex( { "id_post": 1 }, { unique: true } );
db.post_followers.createIndex( { "taken_at_timestamp": -1 } );
db.post_followers.createIndex( { "owner": -1 } );