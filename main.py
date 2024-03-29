from flask import Flask, render_template, redirect, request, abort, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from data.news import News
from data.users import User
from data import db_session

import os
from playsound import playsound

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
#    if current_user.is_authenticated:
#        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True))
#    else:
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_music():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление песни', form=form)


@app.route('/download',  methods=['GET', 'POST'])
@login_required
def download_file():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('download.html', title='Скачивание песни', form=form)


@app.route('/favorite',  methods=['GET', 'POST'])
@login_required
def favorite():
    pass


@app.route('/sleep',  methods=['GET', 'POST'])
@login_required
def sleep():
    form = NewsForm()
    if form.validate_on_submit():
        # db_sess = db_session.create_session()
        # news = News()
        # news.title = form.title.data
        # news.content = form.content.data
        # news.is_private = form.is_private.data
        # current_user.news.append(news)
        # db_sess.merge(current_user)
        # db_sess.commit()
        return redirect('/')
    return render_template('sleep.html', title='Таймер сна', form=form)


@app.route('music_play', methods=['GET', 'POST'])
@login_required
def music_play():
    playsound('myfile.wav')
    return


@app.route('/music_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def music_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/music_like/<int:id>', methods=['GET', 'POST'])
@login_required
def music_like(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if news:
        # добавлять песни в избранное
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
