# coding=gbk
from flask import request, render_template, session, redirect, url_for, flash, jsonify
from . import main
from .. import db
from config import config
import json
import os.path, uuid, time

def file_extension(path):
    return os.path.splitext(path)[1]
@main.route('/logout',methods = ['GET', 'POST'])
def loginout():
    session['Login'] = False
    return redirect(url_for('main.login'))

@main.route('/login',methods = ['GET', 'POST'])
def login():
    msg=''
    if request.method=='POST':
        u_uid = request.form['u_uid']
        u_pwd = request.form['u_pwd']
        sql='select Name,password,last_login,Title_id from user where User_id=%s' % (u_uid)
        user = db.session.execute(sql).first()
        if not user:
            msg=u'User does not exist'
            return render_template('login.html',msg=msg)
        if user[1]==u_pwd:
            session['Login'] = True
            session['userid']=u_uid
            session['username']=user[0]
            session['last_login']=user[2] if user[2] else str(int(time.time()))
            sql = 'select Title_name from title where Title_id=%s' % (user[3])
            utitle = db.session.execute(sql).first()[0]
            session['Title']=utitle
            sql='update user set last_login=%s where User_id=%s' % (str(int(time.time())),u_uid)
            db.session.execute(sql)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            msg=u'invalid username or password!'
            return render_template('login.html',msg=msg)
    else:
        return render_template('login.html',msg=msg,current_user=None)

@main.route('/')
def index():
    if (not session.get('Login', False)) or (session['Login'] == False): return redirect(url_for('main.login'))
    page = request.args.get('page', 1, type=int)
    pagecount = db.session.execute('select count(*) from article').first()
    pages = pagecount[0]
    notes_page = config.notes_page
    pages = int(pages / notes_page) if (pages % notes_page) == 0 else (int(pages / notes_page)) + 1
    startp = 0 if page == 1 else (int(page) - 1) * notes_page
    sql = "SELECT article.*,a.comment_c from article,(SELECT Article_id,count(Article_id) as comment_c from v_comment GROUP BY Article_id) as a WHERE article.Article_id=a.Article_id order by article.pubDate DESC LIMIT :startp,:per_page;"
    notes = db.session.execute(sql, {'startp': startp, 'per_page': notes_page}).fetchall()
    mytopic=[]
    sql='select distinct newdesk from article where Article_id in (select article_id from user_topic where user_id=%s)' %(session['userid'])
    mytopic=db.session.execute(sql).fetchall()

    sql='select User_id,Name from user where User_id in (select to_Userid from user_user where from_Userid=%s)' %(session['userid'])
    myusers=[]
    myusers = db.session.execute(sql).fetchall()
    return render_template('index.html',mytopic=mytopic,myusers=myusers,notes=notes, pages=pages, page=page,current_user=session['username'],utitle=session['Title'])

@main.route('/TopicArticle/<topic>')
def TopicArticle(topic):
    if (not session.get('Login', False)) or (session['Login'] == False): return redirect(url_for('main.login'))
    page = request.args.get('page', 1, type=int)
    pagecount = db.session.execute('select count(*) from article where newdesk="{}"'.format(topic)).first()
    pages = pagecount[0]
    notes_page = config.notes_page
    pages = int(pages / notes_page) if (pages % notes_page) == 0 else (int(pages / notes_page)) + 1
    startp = 0 if page == 1 else (int(page) - 1) * notes_page
    sql = "SELECT article.*,a.comment_c from article,(SELECT Article_id,count(Article_id) as comment_c from v_comment GROUP BY Article_id) as a WHERE newdesk='{}' and article.Article_id=a.Article_id order by article.pubDate DESC LIMIT :startp,:per_page;".format(topic)
    notes = db.session.execute(sql, {'startp': startp, 'per_page': notes_page}).fetchall()
    mytopic=[]
    sql='select distinct newdesk from article where Article_id in (select article_id from user_topic where user_id=%s)' %(session['userid'])
    mytopic=db.session.execute(sql).fetchall()

    sql='select User_id,Name from user where User_id in (select to_Userid from user_user where from_Userid=%s)' %(session['userid'])
    myusers=[]
    myusers = db.session.execute(sql).fetchall()
    return render_template('index.html',mytopic=mytopic,myusers=myusers,notes=notes, pages=pages, page=page,current_user=session['username'],utitle=session['Title'])

@main.route('/UserCommnets/<userid>')
def UserCommnets(userid):
    if (not session.get('Login', False)) or (session['Login'] == False): return redirect(url_for('main.login'))
    page = request.args.get('page', 1, type=int)
    sql="SELECT count(*) from article_comment  WHERE Article_id in (select Article_id from comment where User_id='{}' and createDate>{});".format(userid,session['last_login'])
    pagecount = db.session.execute(sql).first()
    pages = pagecount[0]
    notes_page = config.notes_page
    pages = int(pages / notes_page) if (pages % notes_page) == 0 else (int(pages / notes_page)) + 1
    startp = 0 if page == 1 else (int(page) - 1) * notes_page
    sql = "SELECT * from article_comment WHERE  Article_id in (select Article_id from comment where User_id={} and createDate>{}) order by pubDate DESC LIMIT :startp,:per_page;".format(userid,session['last_login'])
    notes = db.session.execute(sql, {'startp': startp, 'per_page': notes_page}).fetchall()
    mytopic=[]
    sql='select distinct newdesk from article where Article_id in (select article_id from user_topic where user_id=%s)' %(session['userid'])
    mytopic=db.session.execute(sql).fetchall()

    sql='select User_id,Name from user where User_id in (select to_Userid from user_user where from_Userid=%s)' %(session['userid'])
    myusers=[]
    myusers = db.session.execute(sql).fetchall()
    return render_template('index.html',mytopic=mytopic,myusers=myusers,notes=notes, pages=pages, page=page,current_user=session['username'],utitle=session['Title'])

@main.route('/read_comments/<articleid>', methods=['GET', 'POST'])
def read_comments(articleid):
    comment_count = db.session.execute("select count(Comment_id) FROM v_comment WHERE Article_id=:articleid", {'articleid': articleid}).first()
    counts = comment_count[0]
    comments_page = config.comment_page
    pages = int(counts / comments_page) if (counts % comments_page) == 0 else (int(counts / comments_page)) + 1
    return render_template('readnote.html', pages=pages, page=1,articleid=articleid,user_id=session['userid'],current_user=session['username'],utitle=session['Title'])

@main.route('/get_comments', methods=['GET', 'POST'])
def get_comments():
    clientip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            clientip = _ip
    except Exception as e:
        clientip='127.0.0.1'

    data = request.get_json()
    noteid = data['note_id']
    page = data['page']
    comments_page = config.comment_page
    startp = 0 if page == 1 else (int(page) - 1) * comments_page
    sql = 'select v_comment.*,reply_c.c_count from v_comment LEFT JOIN reply_c on v_comment.Comment_id=reply_c.parentID WHERE  Article_id=:noteid   order by dt_record DESC LIMIT :startp,:per_page;'
    comments = db.session.execute(sql, {'noteid': noteid, 'startp': startp, 'per_page': comments_page}).fetchall()

    rethtml = render_template('models/comment.html', comments=comments,clientip=clientip,user_id=session['userid'],current_user=session['username'])
    ret = {'res': rethtml}
    return jsonify(ret)

@main.route('/get_applys', methods=['GET', 'POST'])
def get_applys():
    clientip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            clientip = _ip
    except Exception as e:
        pass

    data = request.get_json()
    comment_id = data['comment_id']
    # comments_page=config.comment_page
    # startp=0 if page==1 else (int(page)-1)*comments_page
    sql = 'SELECT * FROM v_reply WHERE parentID=:comment_id   order by dt_record ASC;'
    replys = db.session.execute(sql, {'comment_id': comment_id}).fetchall()
    replycount = len(replys)
    rethtml = render_template('models/replys.html', replys=replys, replycount=replycount,clientip=clientip,current_user=session['userid'])
    ret = {'res': rethtml}
    return jsonify(ret)

@main.route('/addcomment', methods=['GET', 'POST'])
def addcomment():
    clientip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            clientip = _ip
    except Exception as e:
        pass
    data = request.get_json()
    note_id = data['note_id']
    s_content = data['s_content']
    from_uname = session['username']
    from_uid = session['userid']
    dt_record = config.current_datetime
    sql = "insert into comment(CommentBody,commentType,createDate,depth,parentID,User_id,Article_id) values('%s','%s','%s','%s','%s','%s','%s')" % (
        s_content, 'comment', str(int(time.time())), '1','0', from_uid,note_id)
    db.session.execute(sql)
    db.session.commit()
    new_comment={'dt_record':dt_record,'from_uid':from_uid,'from_uname':from_uname,'s_content':s_content,'id':note_id}
    rethtml = render_template('models/comment_one.html', comment=new_comment,clientip=clientip,current_user=session['userid'])
    ret = {'res': rethtml}
    return jsonify(ret)

@main.route('/delcomment/<id>')
def delcommnet(id):
    sql = 'DELETE FROM comment WHERE Comment_id=:comment_id;'
    db.session.execute(sql, {'comment_id': id})
    ret = {'res': 'ok'}
    return jsonify(ret)

@main.route('/delreply', methods=['GET', 'POST'])
def delreply():
    data = request.get_json()
    # comment_id=data['comment_id']
    reply_id = data['reply_id']
    sql2 = 'DELETE FROM comment WHERE Comment_id=:reply_id;'
    db.session.execute(sql2, {'reply_id': reply_id})
    ret = {'res': 'ok'}
    return jsonify(ret)

@main.route('/addreply', methods=['GET', 'POST'])
def addreply():
    clientip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            clientip = _ip
    except Exception as e:
        pass
    data = request.get_json()
    comment_id = data['comment_id']
    s_content = data['s_content']
    to_uid = data['to_uids']
    to_unames = data['to_unames']
    from_uname = session['username']
    from_uid = session['userid']
    articleid=data['articleid']

    dt_record = config.current_datetime
    sql = "insert into comment(CommentBody,commentType,createDate,depth,parentID,parentUser,User_id,Article_id) values('%s','%s','%s','%s','%s','%s','%s','%s')" % (
    s_content, 'userReply', str(int(time.time())), '2', comment_id, to_unames, from_uid,articleid)
    db.session.execute(sql)
    db.session.commit()
    # sql='SELECT * FROM replys WHERE comment_id=:comment_id   order by dt_record ASC,from_uid,to_uids;'
    # replys=db.session.execute(sql,{'comment_id':comment_id}).fetchall()
    new_reply={'comment_id':comment_id,'from_uname':from_uname,'from_uid':from_uid,'dt_record':config.current_datetime,'to_uids':to_uid,'to_unames':to_unames,'s_content':s_content}
    rethtml = render_template('models/replys_one.html', reply=new_reply, clientip=clientip,current_user=session['userid'])
    ret = {'res': rethtml}
    return jsonify(ret)

@main.route('/laud/<comment_id>')
def laudnote(comment_id):
    sql='select recommendations from comment where Comment_id=%s' %(comment_id)
    i_laud=db.session.execute(sql).first()[0]
    sql='update comment set recommendations=recommendations+1'
    db.session.execute(sql)
    db.session.commit()
    ret = {'i_laud': i_laud+1}
    L = json.dumps(ret)
    return L

@main.route('/cancellaud/<comment_id>')
def cancellaud(comment_id):
    sql = 'select recommendations from comment where Comment_id=%s' % (comment_id)
    i_laud = db.session.execute(sql).first()[0]
    sql = 'update comment set recommendations=recommendations-1'
    db.session.execute(sql)
    db.session.commit()
    ret = {'i_laud': i_laud - 1}
    L = json.dumps(ret)
    return L

@main.route('/down/<comment_id>')
def downnote(comment_id):
    sql='select negative_comment from comment where Comment_id=%s' %(comment_id)
    i_down=db.session.execute(sql).first()[0]
    sql='update comment set negative_comment=negative_comment+1'
    db.session.execute(sql)
    db.session.commit()
    ret = {'i_down': i_down+1}
    L = json.dumps(ret)
    return L

@main.route('/canceldown/<comment_id>')
def canceldown(comment_id):
    sql = 'select negative_comment from comment where Comment_id=%s' % (comment_id)
    i_down = db.session.execute(sql).first()[0]
    sql = 'update comment set negative_comment=negative_comment-1'
    db.session.execute(sql)
    db.session.commit()
    ret = {'i_down': i_down - 1}
    L = json.dumps(ret)
    return L

@main.route('/fllowarticle/<articleid>')
def fllowarticle(articleid):
    user_id=session['userid']
    sql='select count(article_id) from user_topic where article_id="%s" and User_id="%s"' %(articleid,user_id)
    i=db.session.execute(sql).first()[0]
    print(i)
    if i==0:
        sql='insert into user_topic values(0,"%s","%s",%s)' % (user_id,articleid,str(int(time.time())))
        db.session.execute(sql)
        db.session.commit()
    ret = {'fllow': 0}
    L = json.dumps(ret)
    return L

@main.route('/delfllowarticle/<articleid>')
def delfllowarticle(articleid):
    user_id=session['userid']
    sql='delete from user_topic where article_id="%s" and User_id="%s"' %(articleid,user_id)
    db.session.execute(sql)
    db.session.commit()
    ret = {'fllow': 0}
    L = json.dumps(ret)
    return L

@main.route('/fllowuser/<user_id>')
def fllowuser(user_id):
    from_userid=session['userid']
    sql='select count(id) from user_user where from_Userid="%s" and to_Userid="%s"' %(from_userid,user_id)
    i=db.session.execute(sql).first()[0]
    print(i)
    if i==0:
        sql='insert into user_user values(0,"%s","%s","%s")' % (from_userid,user_id,str(int(time.time())))
        db.session.execute(sql)
        db.session.commit()
    else:
        i=2
    ret = {'fllow': i}
    L = json.dumps(ret)
    return L
