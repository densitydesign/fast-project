db.brand.createIndex( { "id_user": 1 }, { unique: true } );
db.post.createIndex( { "id_post": 1 }, { unique: true } );
db.post.createIndex( { "taken_at_timestamp": -1 } );
db.post.createIndex( { "main_content": -1 });
