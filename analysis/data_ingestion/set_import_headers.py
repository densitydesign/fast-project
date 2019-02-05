import pandas as pd
import os,csv,sys

user_header_import = ['id_user.int64()','username.string()','profile_pic_url.string()','followers_count.int32()','following_count.int32()',
                      'num_posts.int32()','biography.string()','isPrivate.boolean()']
post_header_import = ['id_post.int64()','username.string()','video_count.string()','url_img.string()','link_post.string()','owner.int64()','caption.string()','comment_count.string()',
                      'taken_at_timestamp.string()', 'taken_at_time.string()', 'shortcode.string()','is_video.boolean()','likes_count.string()']

path = '../../csv/'
brand = sys.argv[1]
        

user = pd.read_csv(path + brand + '/followers/user.csv')
user.columns = user_header_import
user.to_csv(path + brand + '/followers/user.csv', index=None)


try:
    post = pd.read_csv(path + brand + '/followers/post_fixed.csv', dtype=object, error_bad_lines=False)
    post.columns = post_header_import
    post.to_csv(path + brand + '/followers/post_fixed.csv', index=None)
except Exception as e:
    print e
