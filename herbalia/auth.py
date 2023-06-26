from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users
from flask_mail import Message
from flask import session
import secrets
from . import mail
from . import db

auth = Blueprint('auth', __name__)
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/redefine')
def redefine():
    return render_template('redefine.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = Users.query.filter_by(email=email).first()
    if user:
        flash('Endereço de Email já existe')
        return redirect(url_for('auth.signup'))

    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()

    # Envio do e-mail de verificação
    token = generate_verification_token(email)  # Gere um token de verificação exclusivo
    send_verification_email(email, token)  # Envie o e-mail de verificação

    flash('Verifique seu e-mail para concluir o cadastro')
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = Users.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Verifique seus detalhes de login e tente novamente.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.index'))

@auth.route('/redefine', methods=['POST'])
def redefine_post():
    email = request.form.get('email')
    user = Users.query.filter_by(email=email).first()
    if not user:
        flash('Endereço de e-mail ainda não cadastrado.')
        return redirect(url_for('auth.signup'))

    # Gerar um token de redefinição de senha único (pode ser um UUID ou um token aleatório)
    reset_token = generate_reset_token()

    # Salvar o token no banco de dados para o usuário correspondente
    user.reset_token = reset_token
    db.session.commit()

    # Enviar o e-mail com o link de redefinição de senha contendo o token
    send_reset_email(user.email, reset_token)

    flash('Um e-mail com instruções para redefinir sua senha foi enviado.')
    return redirect(url_for('auth.login'))

@auth.route('/verify-email/<token>')
def verify_email(token):
    user = Users.query.filter_by(verification_token=token).first()

    if user:
        # O token é válido, marque o e-mail como verificado e limpe o token
        user.is_verified = True
        user.verification_token = None
        db.session.commit()

        flash('E-mail verificado com sucesso. Faça login para continuar.')
    else:
        flash('Token inválido ou expirado. Verificação de e-mail falhou.')

    return redirect(url_for('auth.login'))



def generate_verification_token(email):
    token = secrets.token_urlsafe(16)  # Gera um token de 16 bytes seguro para uso em URLs
    user = Users.query.filter_by(email=email).first()
    if user:
        user.verification_token = token
        db.session.commit()
    return token

def generate_reset_token():
    token = secrets.token_urlsafe(16)  # Gera um token de 16 bytes seguro para uso em URLs
    return token

def send_verification_email(email, token):
    # Crie a mensagem de e-mail com o link de verificação
    msg = Message('Herbalia: Verificação de e-mail', sender= 'luana00gomes@gmail.com', recipients=[email])

    verification_link = url_for('auth.verify_email', token=token, _external=True)
    msg.body = f'Clique no link a seguir para verificar seu e-mail para sua conta Herbalia: {verification_link}'

    # Envie o e-mail
    mail.send(msg)

def send_reset_email(email, token):
    # Crie a mensagem de e-mail com o link de verificação
    msg = Message('Herbalia: Redefina sua senha', sender= 'luana00gomes@gmail.com', recipients=[email])

    verification_link = url_for('auth.reset_password', token=token, _external=True)
    msg.body = f'Clique no link a seguir para redefinir sua senha Herbalia: {verification_link}'

    # Envie o e-mail
    mail.send(msg)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verifique se o token é válido e pertence a um usuário
    user = Users.query.filter_by(reset_token=token).first()
    if not user:
        flash('O link de redefinição de senha é inválido ou expirou.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password == confirm_password:
            # Redefina a senha do usuário
            user.update_password(password)
            flash('Sua senha foi redefinida com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('As senhas digitadas não correspondem.', 'danger')
    
    return render_template('reset_password.html', token=token)
