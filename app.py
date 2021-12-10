import os
from flask import Flask,render_template,abort,url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Text, BLOB
from flask_admin import Admin, form
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField
from wtforms.validators import DataRequired


app = Flask(__name__)

##setting up SQLAlchemy
basedir = os.getcwd() ## the path for the application itself
file_path = os.path.join(basedir,'static/files')

##config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bulusan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'

db = SQLAlchemy(app)
admin = Admin(app,name='bulusan',template_mode='bootstrap3')


class LoginForm(FlaskForm):
    user_name = StringField('Username',validators=[DataRequired()])
    password= PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Sign In')





@app.route('/')
def homepage():
    posts = Posts.query.all()
    post_new = []
    header_image_dict = {}
    try:
        for post in posts:
            gallery = Gallery.query.filter_by(slug=post.slug).one()
            header_image_dict.update({post.slug: gallery.image_header})
        i = 0

        for post in reversed(posts):
            if i > 2:
                break
            post_new.append(post)
            i += 1
    except Exception as e:
        print(e)
    return render_template('index.html', posts=post_new, header_image_dict=header_image_dict)

@app.route('/showall')
def showall():
    posts = Posts.query.all()
    post_new = []
    header_image_dict = {}
    try:
        for post in posts:
            gallery = Gallery.query.filter_by(slug=post.slug).one()
            header_image_dict.update({post.slug: gallery.image_header})
        i = 0

        for post in reversed(posts):
            post_new.append(post)
            i += 1
    except:
        pass

    return render_template('show_all.html', posts=post_new, header_image_dict=header_image_dict)

@app.route('/explorer',methods=['GET','POST'])
def explorer():
    is_empty=True
    if request.method == 'POST':
        header_image_dict = {}
        try:
            posts = Posts.query.filter(Posts.title.contains(request.form["input_search"]))

            for post in posts:
                is_empty=False
                gallery = Gallery.query.filter_by(slug=post.slug).one()
                header_image_dict.update({post.slug: gallery.image_header})
        except:
            pass
        return render_template('explorer.html',posts=posts,header_image_dict=header_image_dict,is_empty=is_empty,search_for=request.form["input_search"])
    else:
        posts = {}
        header_image_dict = {}
        return render_template('explorer.html',posts=posts,header_image_dict=header_image_dict,is_empty=is_empty)



@app.route('/post/<string:slug>')
def post(slug):
    try:
        post = Posts.query.filter_by(slug=slug).one()
        gallery = Gallery.query.filter_by(slug=slug).one()
        return render_template('post.html',post=post,gallery=gallery)
    except Exception as e:
        return render_template('post.html')

@app.route('/login',methods=["GET","POST"])
def login():
    error=''
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = AdminAccounts.query.filter_by(username=form.user_name.data).one()
            if form.user_name.data == user.username and form.password.data == user.password:
                return redirect(url_for("admin.index"))
            else:
                error = 'Username or Password is incorrect!'
                return render_template("login.html", form=form, error=error)
        except Exception as e:
            error = 'Username or Password is incorrect!'
            return render_template("login.html",form=form,error=error)

    return render_template("login.html",form=form,error=error)



## SQL ALCHEMY CLASSESS
class Posts(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer,primary_key=True)
    title = Column(String(255))
    category = Column(String(255))
    content = Column(Text)
    rate = Column(Float)
    price_range = Column(String(255))
    gis = Column(String(255))
    contact_email = Column(String(255))
    contact_number = Column(String(255))
    contact_website = Column(String(255))
    slug = Column(String(255))

class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = Column(Integer,primary_key=True)
    image_header = Column(String,unique=True)
    image_thumbnail = Column(String,unique=True)
    image_1 = Column(String,unique=True)
    image_2 = Column(String,unique=True)
    image_3 = Column(String,unique=True)
    slug = Column(String)

class OpeningHours(db.Model):
    __tablename__ = 'opening_hours'
    id = Column(Integer,primary_key=True)
    slug = Column(String)
    mon = Column(String)
    tue = Column(String)
    wed = Column(String)
    thu = Column(String)
    fri = Column(String)
    sat = Column(String)
    sun = Column(String)

class AdminAccounts(db.Model):
    __tablename__  = 'admin_account'
    id = Column(Integer, primary_key=True)
    username = Column(String,unique=True)
    password = Column(String)

class PostModelView(ModelView):
    # can_delete=False

    page_size = 50
    column_exclude_list = ['content','rate','contact_website']
    form_excluded_columns=['slug','contact_website','rate']
    create_modal = True
    edit_modal = True

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = str(str(model.title).lower().replace(" ",'-'))



def show_posts_slug():
    return Posts.query.all()




class GalleryModelView(ModelView):
    # can_delete=True
    create_modal = True
    edit_modal = True
    # column_display_pk = True
    # can_view_details = True

    def _list_thumbnail(view, context, model, name):
        if name == 'image_header':
            return Markup(
                '<img src="%s">' %
                url_for('static',
                        filename=f'files/{form.thumbgen_filename(model.image_header)}')
            )
        elif name == 'image_thumbnail':
            return Markup(
                '<img src="%s">' %
                url_for('static',
                        filename=f'files/{form.thumbgen_filename(model.image_thumbnail)}')
            )
        elif name == 'image_1':
            return Markup(
                '<img src="%s">' %
                url_for('static',
                        filename=f'files/{form.thumbgen_filename(model.image_1)}')
            )
        elif name == 'image_2':
            return Markup(
                '<img src="%s">' %
                url_for('static',
                        filename=f'files/{form.thumbgen_filename(model.image_2)}')
            )
        elif name == 'image_3':
            return Markup(
                '<img src="%s">' %
                url_for('static',
                        filename=f'files/{form.thumbgen_filename(model.image_3)}')
            )
        else:
            return ''

    column_formatters = {
        'image_header': _list_thumbnail,
        'image_thumbnail': _list_thumbnail,
        'image_1': _list_thumbnail,
        'image_2': _list_thumbnail,
        'image_3': _list_thumbnail
    }

    def scaffold_form(self):
        form = super(GalleryModelView, self).scaffold_form()
        choices = ((m.slug, m.slug) for m in Posts.query.all())
        form.slug.choices = choices
        return form


    # l2 = []
    # try:
    #     l1 = [x.slug for x in Posts.query.all()]
    #     for i in range(0,len(l1)):
    #         l2.append((l1[i],l1[i]))
    #     form_choices = {
    #         'slug': l2
    #     }
    # except Exception as e:
    #     print(e)
    # form_overrides = dict(
    #     slug=SelectField
    # )
    # form_args = dict(
    #     slug=dict(slug=show_posts_slug)
    # )


    form_extra_fields = {
        'image_header': form.ImageUploadField('Image_Header', base_path=file_path, thumbnail_size=(100, 100, True)),
        'image_thumbnail': form.ImageUploadField('Image_Thumbnail', base_path=file_path, thumbnail_size=(100, 100, True)),
        'image_1': form.ImageUploadField('Image_1', base_path=file_path, thumbnail_size=(100, 100, True)),
        'image_2': form.ImageUploadField('Image_2', base_path=file_path, thumbnail_size=(100, 100, True)),
        'image_3': form.ImageUploadField('Image_3', base_path=file_path, thumbnail_size=(100, 100, True))
    }


class OpeningHoursModelView(ModelView):
    # can_delete=False
    create_modal = True
    edit_modal = True

    def scaffold_form(self):
        form = super(OpeningHoursModelView, self).scaffold_form()
        choices = ((m.slug, m.slug) for m in Posts.query.all())
        form.slug.choices = choices
        return form
    # try:
    #     l1 = [x.slug for x in Posts.query.all()]
    #     l2 = []
    #     for i in range(0,len(l1)):
    #         l2.append((l1[i],l1[i]))
    #     form_choices = {
    #         'slug': l2
    #     }
    # except Exception as e:
    #     print(e)



class AdminAccountsModelView(ModelView):
    # can_delete=False
    create_modal = True
    edit_modal = True
    page_size = 50
    column_exclude_list = ['content',]
    create_modal = True
    edit_modal = True

admin.add_view(PostModelView(Posts, db.session))
admin.add_view(GalleryModelView(Gallery,db.session))
admin.add_view(OpeningHoursModelView(OpeningHours,db.session))

admin.add_view(AdminAccountsModelView(AdminAccounts,db.session))
admin.add_link(MenuLink(name='Logout', category='', url="/"))

if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)