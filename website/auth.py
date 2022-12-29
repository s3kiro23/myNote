from flask import Blueprint, render_template, request, redirect, url_for, flash

from . import db
from .models import User

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.hello"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash("Connexion réussi !", category="success")
                return redirect(url_for("views.hello"))
            else:
                flash("Mauvais mot de passe !", category="denied")
        else:
            flash("Compte utilisateur inexistant !", category="denied")
    return render_template("login.html", user=current_user)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("views.hello"))
    if request.method == "POST":
        nom = request.form.get("nom")
        email = request.form.get("email")
        secret_question = request.form.get("secret_question")
        secret_response = request.form.get("secret_response")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Cet utilisateur existe déjà !", category="denied")
            return render_template("signup.html", user=current_user)
        else:
            if password == password2:
                new_user = User(nom=nom, email=email, secret_question=secret_question, secret_response=secret_response,
                                password=generate_password_hash(password, method="sha256"))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                flash("Compte créé avec succès !", category="success")
                return redirect(url_for("views.hello", user=current_user))
            flash("Les mots de passe ne correspondent pas !", category="denied")
    return render_template("signup.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@auth.route("/change_profile/<champ>", methods=["GET", "POST"])
@login_required
def change_profile(champ):
    if request.method == "POST":
        nom = request.form.get("nom")
        email = request.form.get("email")
        secret_question = request.form.get("secret_question")
        secret_response = request.form.get("secret_response")
        new_password = request.form.get("password")
        new_password2 = request.form.get("password2")
        user_description = request.form.get("user_description")
        # email_check = User.query.filter_by(email=email).first()
        print(f"{nom}, {email}, {new_password}, {new_password2}")
        if champ == "nom":
            current_user.nom = nom
            db.session.commit()
            flash("Modification des données réalisée avec succès !", category="success")
            return redirect(url_for("auth.profile", user=current_user))
        if champ == "email":
            current_user.email = email
            db.session.commit()
            flash("Modification des données réalisée avec succès !", category="success")
            return redirect(url_for("auth.profile", user=current_user))
        if champ == "secret_question" and "secret_response":
            current_user.secret_question = secret_question
            current_user.secret_response = secret_response
            db.session.commit()
            flash("Modification des données réalisée avec succès !", category="success")
            return redirect(url_for("auth.profile", user=current_user))
        # if champ == "secret_response":
        #     current_user.secret_response = secret_response
        #     db.session.commit()
        #     flash("Modification des données réalisée avec succès !", category="success")
        #     return redirect(url_for("auth.profile", user=current_user))
        if champ == "password":
            if new_password == new_password2:
                current_user.password = generate_password_hash(new_password, method="sha256")
                db.session.commit()
                flash("Modification des données réalisée avec succès !", category="success")
                return redirect(url_for("auth.profile", user=current_user))
            flash("Les mots de passe ne correspondent pas !", category="denied")
        if champ == "user_description":
            current_user.user_description = user_description
            db.session.commit()
            flash("Modification des données réalisée avec succès !", category="success")
            return redirect(url_for("auth.profile", user=current_user))
    return render_template("change_profile.html", user=current_user, champ=champ)


@auth.route("/forgot-pwd", methods=["GET", "POST"])
def forgot_pwd():
    if request.method == "POST":
        email = request.form.get("email")
        secret_value = request.form.get('secret_value')
        secret_value2 = request.form.get('secret_value2')
        secret_response = request.form.get("secret_response")
        new_password = request.form.get("password")
        new_password2 = request.form.get("password2")
        # secret_question = request.form.get("secret_question")
        # user = User.query.filter_by(email=email).first()
        print(f"{email}, {secret_value}, {secret_value2}, {secret_response}, {new_password}, {new_password2}")
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                return render_template("forgot-pwd.html", user=current_user, secret_question=user.secret_question,
                                       email=user.email)
            flash("Ce compte n'existe pas !", category="denied")
        if secret_value:
            user = User.query.filter_by(email=secret_value).first()
            if user:
                if secret_response == user.secret_response:
                    return render_template("forgot-pwd.html", user=current_user, secret_response=user.secret_response,
                                           email=user.email)
                flash("Cette réponse n'est pas valide pour l'utilisateur !", category="denied")
                return render_template("forgot-pwd.html", user=current_user, secret_question=user.secret_question,
                                       email=user.email)
            return render_template("forgot-pwd.html", user=current_user)
        if secret_value2:
            user = User.query.filter_by(email=secret_value2).first()
            if user:
                if new_password == new_password2:
                    user.password = generate_password_hash(new_password, method="sha256")
                    db.session.commit()
                    flash("Récupération du compte réussi !", category="success")
                    return redirect(url_for("auth.login"))
    return render_template("forgot-pwd.html", user=current_user)

    #     if user:
    #         if secret_question == user.secret_question:
    #             if secret_response == user.secret_response:
    #                 if new_password == new_password2:
    #                     user.password = generate_password_hash(new_password, method="sha256")
    #                     db.session.commit()
    #                     flash("Récupération du compte réussi !", category="success")
    #                     return redirect(url_for("auth.login"))
    #                 else:
    #                     flash("Les mots de passe ne correspondent pas !", category="denied")
    #                     return render_template("forgot-pwd.html", user=current_user)
    #             else:
    #                 flash("Cette réponse n'est pas valide pour cet utilisateur !", category="denied")
    #             return render_template("forgot-pwd.html", user=current_user)
    #         else:
    #             flash("Cette question n'existe pas pour cet utilisateur !", category="denied")
    #         return render_template("forgot-pwd.html", user=current_user)
    #     else:
    #         flash("Compte utilisateur inexistant !", category="denied")
    #     return render_template("forgot-pwd.html", user=current_user)
    # return render_template("forgot-pwd.html", user=current_user)
