from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    BadTimeSignature,
)
import jwt
import datetime
from flask import (
    render_template,
    redirect,
    request,
    url_for,
    flash,
    jsonify,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email, send_email_with_aws
from .forms import (
    ChangeUsernameForm,
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    PasswordResetRequestForm,
    PasswordResetForm,
    ChangeEmailForm,
)
import decouple

from app.DynamoAccess import DynamoAccess 
from app.api.AuthHelper import AuthHelper

REDIRECT_URL_HOME = f'{decouple.config("HOST")}/auth/login' 
REDIRECT_URL_RESET = f'{decouple.config("HOST")}/auth/reset' 
REDIRECT_URL_BAD_TOKEN = f'{decouple.config("HOST")}/bad_token'

dynamo_access = DynamoAccess() 
auth_helper = AuthHelper()

@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user: User = dynamo_access.GetUserByEmail(email)

    if user is None:
        return jsonify({"message": "Couldn't find your account"}), 404

    elif not user.verify_password(password):
        return jsonify({"message": "The password you’ve entered is incorrect"}), 401

    else:
        return (
            jsonify(
                {
                    "message": "Login successful",
                    "token": auth_helper.generate_jwt(email),
                    "username": user.username,
                    "user_id": user.id,
                    "confirmed": user.confirmed,
                }
            ),
            200,
        )


@auth.route("/register", methods=["POST"])
def register():
    # Extract input from the POST request's JSON body
    data = request.get_json()
    if not data:
        return jsonify("No input data provided"), 400

    # Validate required fields
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return (
            jsonify({"error": "All fields (email, username, password) are required"}),
            400,
        )

    if not dynamo_access.CheckIfEmailIsUnique(email):
        return (
            jsonify({"error": "This email already exists"}),
            400,
        )

    if not dynamo_access.CheckIfUserNameIsUnique(username):
        return (
            jsonify({"error": "This username is already taken"}),
            400,
        )

    # Create user instance
    user = User(email=email.lower(), user_name=username, raw_password=password)

    try:
        user_added = dynamo_access.AddUsers(user)
        if not user_added:
            return jsonify({"error": "Failed to add user"}), 500

        # Generate confirmation token
        token = user.generate_confirmation_token()

        # Send confirmation email
        send_email_with_aws(
            user.email,
            "CMCC Fantasy Cricket Confirm Your Account",
            "auth/email/confirm",
            user=user,
            token=token,
        )

        # Return success response with the login URL or token (if needed)
        login_url = url_for("auth.login", _external=True)
        return (
            jsonify(
                {
                    "message": "A confirmation email has been sent. Check your spam folder as well.",
                    "login_url": login_url,
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Registration failed: {e}")
        return jsonify({"error": "Registration failed, please try again"}), 500


@auth.route("/confirm/<token>", methods=["GET"])
def confirm(token):
    print(f"foken = {token}")
    try:
        user_id: str = auth_helper.decode_confirmation_token(token)
        print(f"user id = {user_id}")
    except:
        return redirect(REDIRECT_URL_BAD_TOKEN)

    user_exists: bool = dynamo_access.GetUserById(user_id) != None

    if not user_exists:
        return redirect(REDIRECT_URL_BAD_TOKEN)

    if dynamo_access.GetUserConfirmationStatus(user_id):  # already confirmed
        return redirect(REDIRECT_URL_HOME)

    else:
        dynamo_access.UpdateUserConfirmation(user_id)
        return redirect(REDIRECT_URL_HOME)


@auth.route("/confirm", methods=["POST"])
def resend_confirmation():
    data = request.get_json()
    email = data["email"]
    user_id = data["user_id"]
    token = request.headers.get("Authorization")

    if token and auth_helper.validate_jwt(token=token, user_email=email):
        user: User = dynamo_access.GetUserById(user_id)
        confirmation_token = user.generate_confirmation_token()
        send_email_with_aws(
            user.email,
            "Confirm Your Account",
            "auth/email/confirm",
            user=user,
            token=confirmation_token,
        )
        return jsonify({"success": "confirmation email sent"}), 200

    else:
        return jsonify({"error": "invalid authorization token"}), 403


# @auth.route("/change-password", methods=["GET", "POST"])
# @login_required
# def change_password():
#     form = ChangePasswordForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.old_password.data):
#             current_user.password_hash = current_user.encrypt_password(
#                 form.password.data
#             )
#             dynamo_access.UpdateUserPassword(
#                 current_user.id, current_user.password_hash
#             )
#             flash("Your password has been updated.")
#             return redirect(url_for("main.index"))
#         else:
#             flash("Invalid password.")
#     return render_template("auth/change_password.html", form=form)


@auth.route("/reset", methods=["POST"])
def password_reset_request():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Bad Reqeust"}), 400

    email: str = data.get("email")

    user = dynamo_access.GetUserByEmail(email.lower())
    if user:
        token = user.generate_reset_token()
        send_email_with_aws(
            user.email,
            "Reset Your Password",
            "auth/email/reset_password",
            user=user,
            token=token, 
            link = REDIRECT_URL_RESET
        )

        return jsonify({"success": "Email sent with reset instruction"}), 200
    else:
        return jsonify({"error": "Couldn't find your account"}), 404


@auth.route("/resetWithToken", methods=["POST"])
def password_reset(): 
    data = request.get_json() 
    token = data.get("token") 

    if not data or not token or "new_password" not in data:  
        return jsonify({"error": "Bad Reqeust"}), 400 
    
    if User.reset_password(token, data.get("new_password")):  
        return jsonify({"success": "Password is updated!"}), 200 
    else: 
        return jsonify({"error": "Invalid token"}), 498


# @auth.route("/change_email", methods=["GET", "POST"])
# @login_required
# def change_email_request():
#     form = ChangeEmailForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.password.data):
#             new_email = form.email.data.lower()
#             token = current_user.generate_email_change_token(new_email)
#             send_email_with_aws(
#                 new_email,
#                 "Confirm your email address",
#                 "auth/email/change_email",
#                 user=current_user,
#                 token=token,
#             )
#             flash(
#                 "An email with instructions to confirm your new email "
#                 "address has been sent to you."
#             )
#             return redirect(url_for("main.index"))
#         else:
#             flash("Invalid email or password.")
#     return render_template("auth/change_email.html", form=form)


@auth.route("/change_email/<token>")
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash("Your email address has been updated.")
    else:
        flash("Invalid request.")
    return redirect(url_for("main.index"))


# @auth.route("/change_username", methods=["GET", "POST"])
# @login_required
# def change_username():
#     form = ChangeUsernameForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.password.data):
#             current_user.username = form.new_username.data
#             dynamo_access.UpdateUsername(current_user.id, current_user.username)
#             flash("Your username has been updated")
#             return redirect(url_for("main.index"))
#         else:
#             flash("Invalid password.")
#     return render_template("auth/change_username.html", form=form)
