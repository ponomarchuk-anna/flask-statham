import os
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from forms import LoginForm, RegForm
from model import db, User
import pdfkit
import requests

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('resume'))
    title = 'Авторизация'
    form = LoginForm()
    return render_template(
        'login.html',
        title=title,
        form=form,
    )


@app.route('/login-process', methods=['POST'])
def login_process():
    form = LoginForm()
    user = User.query.filter(User.username == form.username.data).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        flash('С возвращением!')
        return redirect(url_for('resume'))
    flash('Проверьте корректность имени пользователя и пароля!')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    logout_user()
    flash('До свидания!')
    return redirect(url_for('login'))


@app.route('/reg')
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('resume'))
    title = 'Регистрация'
    form = RegForm()
    return render_template(
        'reg.html',
        title=title,
        form=form,
    )


@app.route('/reg-process', methods=['POST'])
def reg_process():
    form = RegForm()
    check_user = User.query.filter(User.username == form.username.data).count()
    if not check_user:
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!')
        return redirect(url_for('login'))
    flash('Данное имя пользователя уже занято')
    return redirect(url_for('reg'))


@app.route('/resume')
def resume():
    title = 'Ваше резюме'
    user = User.query.get(current_user.id)
    return render_template(
        'resume.html',
        title=title,
        user=user,
    )


@app.route('/resume-process', methods=['POST'])
def resume_process():
    user = User.query.get(current_user.id)
    for field, value in request.form.items():
        setattr(user, field, value)
    db.session.commit()
    flash('Сохранил!')
    return redirect(url_for('resume'))


@app.route('/save-photo', methods=['POST'])
def save_photo():
    photo = request.files['photo']

    if photo:
        photo_filename = f'{current_user.id}.jpeg'
        basedir = os.path.dirname(__file__)
        basedir = os.path.join(basedir, 'static', 'photos')
        path_to_save = os.path.join(basedir, photo_filename)
        photo.save(path_to_save)
    return redirect(url_for('resume'))


@app.route('/download')
def download():
    response = requests.get(
            'http://127.0.0.1:5001/resume',
            headers=request.headers
            )
    with open('test.html', 'w') as f:
        f.write(response.text)
    basedir = os.path.dirname(__file__)
    path = os.path.join(basedir, 'test.html')
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    html=response.text
    path = os.path.join(os.path.dirname(__file__), 'static', 'photos', f'{current_user.id}.jpeg')
    html=html.replace(f'/static/photos/{current_user.id}.jpeg', path)
    pdfkit.from_string(html, 'out.pdf', options={"enable-local-file-access": ""}, configuration=config)
    return send_from_directory(
        basedir, 'out.pdf', as_attachment=True
    )


if __name__ == '__main__':
    app.run(debug=True, port=5001)
