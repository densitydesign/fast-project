db.brand.createIndex( { "id_user": 1 }, { unique: true } );
db.imagetag.createIndex( { "id_post": 1, "concept": 1 }, { unique: true } );
db.imagevector.createIndex( { "id_post": 1 }, { unique: true } );
db.post.createIndex( { "id_post": 1}, { unique: true } );
db.postcoord.createIndex( { "id_post": 1 }, { unique: true } );
db.location.createIndex( { "id_post": 1, "id_location": 1 }, { unique: true } );