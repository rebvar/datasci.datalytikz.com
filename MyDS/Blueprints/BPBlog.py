from flask import Blueprint, render_template, redirect, url_for, request, make_response, jsonify
from os import environ as env
from app import bcr, db, session,ckeditor
from models import User, BlogPost, PostComment,PostLike
#import multiprocessing as mp
import json
import Shared
import os
import uuid
from flask_ckeditor import upload_fail, upload_success
import config
from Lib import Common


BPBlog = Blueprint('BPBlog', __name__)

@BPBlog.route('/posts',methods=['GET'])
def posts():    
    #Filter Later and Check for permissions.        
    posts = BlogPost.query.all()    
    return render_template('blog/posts.html',posts=posts)

@BPBlog.route('/viewpost/<id>',methods=['GET','POST'])
def viewpost(id):    
    

    if request.method == 'POST':
        if 'formAddComment' in request.form:
            name, email = None, None
            commentorId = 0
            if not Shared.isLoggedIn():
                name = request.form['commentorName']
                email = request.form['commentorEmail']

            else:
                user = Shared.getLoggedInUser()
                name = user.name
                email = user.email
                commentorId = user.id
            commentText = request.form['commentText']

            pc = PostComment()
            pc.commentorEmail =  email
            pc.commentorName = name
            pc.commentText = commentText
            pc.commentorId = commentorId
            pc.inReplyTo = 0
            pc.postId = id
            pc.commentDate = Common.getCurrentTimeMil()

            db.session.add(pc)
            db.session.commit()
    
    post = BlogPost.query.filter_by(id = id).first()
    comments = PostComment.query.filter_by(postId = id)
    
    #if comments.count()<=0:
    #    comments = None
    
    commentsDict = None
    commentReplies = None
    if comments:
        commentsDict = {comment.id:comment for comment in comments}            
        commentReplies = {}
        #ht = ""
        

        for comment in comments:            
            commentReplies[comment.id] = []

        for comment in comments:
            if comment.inReplyTo == 0:
                continue
            commentReplies[comment.inReplyTo].append(comment)
            #if comment.inReplyTo == 0:

            #    parents.append(comment)
            #    p = 0
            #    ht+='<div class="row">'+ comment.commentText +'<a href="reply('+str(comment.id)+')" class="replyfont"> Reply </a>'+'</div>'
            #    ht = checkChilds(comment,ht,comments, p)
            #else:
            #    depths[comment.id] = depths[comment.inReplyTo]+1
            
    return render_template('blog/viewpost.html',post=post,comments=comments,commentsDict = commentsDict,commentReplies =commentReplies)# comments = comments, ht = ht)


@BPBlog.route('/create_post',methods=['GET', 'POST'])
def create_post():
    if not Shared.isLoggedIn():
        return redirect(url_for('index'))
    user = Shared.getLoggedInUser()
    if user.utype != 1:
        print ('Not authorised to access')
        return redirect(url_for('index'))
    
    message = None
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('ckeditor')
        bp = BlogPost()
        bp.postBody = body
        bp.postTitle = title
        bp.postDate = Common.getCurrentTimeMil()
        bp.postCreatorId = user.id
        bp.postPerms = 0
        bp.viewCount = 0        
        db.session.add(bp)
        db.session.commit()
        message = 'Post Saved Successfully'
        return redirect(url_for('BPBlog.posts'))
    return render_template('blog/create_post.html',message=message)



#AJAX CALL 
@BPBlog.route('/submit_comment_reply',methods=['GET', 'POST'])
def submit_comment_reply():
    
    message = None
    if request.method == 'POST':

        isAnonym = True
        data = json.loads(request.data)
        commentText = data['replyText']
        inReplyTo=int(data['id'])
        commentorId=0
        postId = int (data['postId'])

        if Shared.isLoggedIn():
            #return redirect(url_for('index'))
            user = Shared.getLoggedInUser()
            isAnonym=False
            name = user.name
            email = user.email
            commentorId = user.id
        else:
            name = 'Anonym'
            email = ''
            commentorId = 0
                
        pc = PostComment()
        pc.commentorEmail =  email
        pc.commentorName = name
        pc.commentText = commentText
        pc.commentorId = commentorId
        pc.inReplyTo = inReplyTo
        pc.postId = postId
        pc.commentDate = Common.getCurrentTimeMil()

        db.session.add(pc)
        db.session.commit()
        resp = make_response(render_template('blog/singleComment.html', comment = pc))
        return json.dumps({'html':resp.data.decode("utf-8"), "id":str(inReplyTo)})
        #else:            
        #    return render_template('blog/singleComment.html', comment = pc)
    return ""


@BPBlog.route('/upload/', methods=['POST'])
def upload():
    """CKEditor file upload"""
    error = ''
    url = ''
    #callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        if fext.lower() not in ['.jpg','.png']:
            return upload_fail('Only .jpg and .png extensions are allowed')
        rnd_name = '%s%s' % (Common.gen_rnd_filename(), fext)
        filepath = config.uploadsPath+'/'+ rnd_name
        dirname = config.uploadsPath
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                return upload_fail('ERROR_CREATE_DIR')
        elif not os.access(dirname, os.W_OK):
            return upload_fail('ERROR_DIR_NOT_WRITEABLE')
        if not error:
            #with open(filepath, 'w+') as destination:
            #    for chunk in fileobj.chunks():
            #        destination.write(chunk)
            fileobj.save(filepath)
            url =url_for('static',filename = 'upload/'+rnd_name)
            return upload_success(url = url)
        else:
            return upload_fail(error)
    else:
        return upload_fail('post error')    