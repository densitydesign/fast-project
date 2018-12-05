import pandas as pd
import os

user_header_import = ['id_user.int64()','username.string()','profile_pic_url.string()','followers_count.int32()','following_count.int32()',
                      'num_posts.int32()','biography.string()','isPrivate.boolean()']
post_header_import = ['id_post.int64()','username.string()','video_count.int32()','url_img.string()','link_post.string()','owner.int64()','caption.string()','comment_count.int32()',
                      'taken_at_timestamp.string()', 'taken_at_time.string()', 'shortcode.string()','is_video.boolean()','likes_count.int32()']

brands = ['emporiosirenuse','daftcollectionofficial','heidikleinswim','loupcharmant','miguelinagambaccini','muzungusisters','athenaprocopiou','zeusndione', 'dodobaror', 'lisamariefernandez']
path = '../../csv/'
for f in os.listdir(path):
    if f in brands:
        
        print f
        
        user = pd.read_csv(path + f + '/followers/user.csv')
        user.columns = user_header_import
        user.to_csv(path + f + '/followers/user.csv', index=None)
        
        try:
            post = pd.read_csv(path + f + '/followers/post_fixed.csv')
            post.columns = post_header_import
            post.to_csv(path + f + '/followers/post_fixed.csv', index=None)
        except Exception as e:
            print e
