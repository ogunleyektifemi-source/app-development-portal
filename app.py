from models import (
    db,
    User,
    ProjectRequest,
    Message,
    Notification,
    PasswordResetToken,
    ProjectFile
)
from flask import abort
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask import send_from_directory
import traceback
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message as MailMessage

from datetime import datetime, timedelta
import secrets



from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import re
from markupsafe import Markup

from config import Config

app = Flask(__name__)

app.config.from_object(Config)
print("=" * 60)
print("DATABASE_URL ENV:", os.environ.get("DATABASE_URL"))
print("SQLALCHEMY URI:", app.config["SQLALCHEMY_DATABASE_URI"])
print("=" * 60)
# ==========================================
# EMAIL CONFIGURATION
# ==========================================



mail = Mail(app)
from email_utils import send_email
# ==========================================
# APPLICATION CONFIGURATION
# ==========================================



db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(".", 1)[1].lower()

        in app.config["ALLOWED_EXTENSIONS"]

    )

# ==========================================
# LOGIN MANAGER
# ==========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


# ==========================================
# USER MODEL
# ==========================================


# ==========================================
# LOGIN USER
# ==========================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# ==========================================
# CREATE DATABASE
# ==========================================




# ==========================================
# CUSTOMER HOMEPAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

@app.route("/users")
def users():
    users = User.query.all()

    print("========== USERS ==========")

    for user in users:
        print(f"ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: '{user.email}'")
        print("-------------------------")

    return "Done"

# ==========================================
# CUSTOMER REGISTRATION
# ==========================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if current_user.is_authenticated:

        return redirect(

            url_for(
                "customer_dashboard"
            )
        )


    if request.method == "POST":
        try:
            name = request.form[
                "name"
            ].strip()

            email = request.form[
                "email"
            ].strip().lower()

            password = request.form[
                "password"
            ]
        except Exception as e:
            print("ERROR SUBMITTING PROJECT:", e)
            raise

        existing_user = User.query.filter_by(

            email=email

        ).first()


        if existing_user:

            flash(
                "An account with this email already exists."
            )

            return redirect(
                url_for(
                    "register"
                )
            )


        new_user = User(

            name=name,

            email=email,

            password_hash=generate_password_hash(
                password
            )

        )


        db.session.add(
            new_user
        )

        db.session.commit()


        login_user(
            new_user
        )


        return redirect(
            url_for(
                "customer_dashboard"
            )
        )


    return render_template(
        "register.html"
    )


# ==========================================
# CUSTOMER LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        print("Entered:", repr(email))

        users = User.query.all()

        for u in users:
            print("Database:", repr(u.email))
            print("Equal?", email == u.email)

        user = User.query.filter(
        db.func.lower(User.email) == email.lower()
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            if user.is_admin:
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("customer_dashboard"))

        flash("Incorrect email or password.")

    return render_template("login.html")

# ==========================================
# CUSTOMER LOGOUT
# ==========================================

@app.route(
    "/logout"
)
@login_required
def logout():

    logout_user()

    return redirect(
        url_for(
            "home"
        )
    )


# ==========================================
# CUSTOMER DASHBOARD
# ==========================================

@app.route(
    "/dashboard"
)
@login_required
def customer_dashboard():

    projects = ProjectRequest.query.filter_by(

        user_id=current_user.id

    ).order_by(

        ProjectRequest.id.desc()

    ).all()


    return render_template(

        "customer_dashboard.html",

        projects=projects

    )


@app.template_filter("linkify")
def linkify(text):

    url_pattern = r"(https?://[^\s]+)"

    text = re.sub(
        url_pattern,
        r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
        text
    )

    return Markup(text)

# ==========================================
# PROJECT REQUEST
# ==========================================

@app.route(
    "/request",
    methods=["GET", "POST"]
)
@login_required
def project_request():

    if request.method == "POST":

        try:

            project_type = request.form["project_type"]

            project_description = request.form["project_description"]

            budget = request.form.get("budget")

            new_request = ProjectRequest(
                user_id=current_user.id,
                name=current_user.name,
                email=current_user.email,
                project_type=project_type,
                project_description=project_description,
                budget=budget
            )

            db.session.add(new_request)
            db.session.commit()

            admin = User.query.filter_by(is_admin=True).first()
            try:
                send_email(
                    "New Project Request",
                    admin.email,
                    f"""
        A new project has been submitted.

        Customer:
        {current_user.name}

        Project:
        {project_type}

        Description:

        {project_description}
        """
                )
            except:
                pass

            notification = Notification(
                user_id=admin.id,
                project_id=new_request.id,
                message=f"{current_user.name} submitted a new '{project_type}' request."
            )

            db.session.add(notification)
            db.session.commit()

            return redirect(url_for("customer_dashboard"))

        except Exception as e:

            print("=" * 60)
            print("PROJECT SUBMISSION ERROR")
            traceback.print_exc()
            print("=" * 60)

            raise
    return render_template("request.html")

# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
@login_required
def admin_dashboard():

    if not current_user.is_admin:
        return "Access denied", 403

    active_projects = ProjectRequest.query.filter(
        ProjectRequest.is_archived == False,
        ProjectRequest.status.in_([
            "New",
            "Accepted",
            "Rejected",
            "Cancelled"
        ])
    ).order_by(
        ProjectRequest.id.desc()
    ).all()

    completed_projects = ProjectRequest.query.filter(
        ProjectRequest.status == "Completed",
        ProjectRequest.is_archived == False
    ).order_by(
        ProjectRequest.id.desc()
    ).all()

    archived_projects = ProjectRequest.query.filter(
        ProjectRequest.is_archived == True
    ).order_by(
        ProjectRequest.id.desc()
    ).all()

    return render_template(
    "admin_dashboard.html",
    active_projects=active_projects,
    completed_projects=completed_projects,
    archived_projects=archived_projects
)
@app.route("/admin/completed")
@login_required
def completed_projects():

    if not current_user.is_admin:
        return "Access denied", 403

    projects = ProjectRequest.query.filter(
        ProjectRequest.status == "Completed",
        ProjectRequest.is_archived == False
    ).order_by(
        ProjectRequest.id.desc()
    ).all()

    return render_template(
        "completed_projects.html",
        projects=projects
    )
@app.route("/admin/archive")
@login_required
def archived_projects():

    if not current_user.is_admin:
        return "Access denied", 403

    projects = ProjectRequest.query.filter_by(
        is_archived=True
    ).order_by(
        ProjectRequest.id.desc()
    ).all()

    return render_template(
        "archived_projects.html",
        projects=projects
    )





# ==========================================
# ACCEPT PROJECT
# ==========================================

@app.route(
    "/admin/accept/<int:project_id>",
    methods=["POST"]
)
@login_required
def accept_project(project_id):

    # Only admins can accept projects
    if not current_user.is_admin:

        return "Access denied", 403


    project = ProjectRequest.query.get_or_404(

        project_id

    )


    project.status = "Accepted"
    notification = Notification(
    user_id=project.user_id,
    project_id=project.id,
    message=f"Your '{project.project_type}' application has been accepted."
)

    db.session.add(notification)
    # Clear any previous rejection reason
    project.rejection_reason = None


    db.session.commit()
    try:
        send_email(

        "Project Accepted",

        project.email,

        f"""
    Hello {project.name},

    Great news!

    Your project:

    {project.project_type}

    has been accepted.

    Please log into your dashboard to begin chatting.

    Regards,

    Tifemi
    """
    )
    except:
        pass
    return redirect(
        url_for("admin_dashboard")
    )
    
@app.route(
    "/admin/reject/<int:project_id>",
    methods=["POST"]
)
@login_required
def reject_project(project_id):

    if not current_user.is_admin:
        return "Access denied", 403

    project = ProjectRequest.query.get_or_404(project_id)

    # Only allow rejection of new or accepted projects
    if project.status not in ["New", "Accepted"]:

        flash("This project cannot be rejected.")

        return redirect(
        url_for(
            "project_workspace",
            project_id=project.id
        )
    )

    rejection_reason = request.form.get(
        "rejection_reason",
        ""
    ).strip()

    if not rejection_reason:
        flash("Please provide a rejection reason.")
        return redirect(
    url_for(
        "project_workspace",
        project_id=project.id
    )
)

    project.status = "Rejected"
    notification = Notification(
    user_id=project.user_id,
    project_id=project.id,
    message=f"Your '{project.project_type}' application was rejected."
)
    db.session.add(notification)
    project.rejection_reason = rejection_reason

    db.session.commit()
    try:
        send_email(

            "Project Rejected",

            project.email,

            f"""
        Hello {project.name},

        Unfortunately your project has been rejected.

        Reason:

        {rejection_reason}

        Regards,

        Tifemi
        """

        )

        flash("Project rejected successfully.")

        return redirect(
        url_for(
            "project_workspace",
            project_id=project.id
        )
    )
    except:
        pass
# ==========================================
# PROJECT WORKSPACE
# ==========================================

@app.route("/project/<int:project_id>")
@login_required
def project_workspace(project_id):

    project = ProjectRequest.query.get_or_404(

        project_id

    )


    # Allow the project owner OR an admin
    if (

        project.user_id != current_user.id

        and not current_user.is_admin

    ):

        return "Access denied", 403


    messages = Message.query.filter_by(

        project_id=project.id

    ).order_by(

        Message.created_at.asc()

    ).all()


    files = ProjectFile.query.filter_by(
    project_id=project.id
).all()

    for file in files:

        if file.file_type == "pdf":
            file.icon = "📄"

        elif file.file_type in ["doc", "docx"]:
            file.icon = "📝"

        elif file.file_type in ["png", "jpg", "jpeg"]:
            file.icon = "🖼"

        elif file.file_type == "zip":
            file.icon = "🗜"

        else:
            file.icon = "📁"

        if file.file_size < 1024:
            file.display_size = f"{file.file_size} B"

        elif file.file_size < 1048576:
            file.display_size = f"{file.file_size / 1024:.1f} KB"

        else:
            file.display_size = f"{file.file_size / 1048576:.2f} MB"

    return render_template(
        "project_workspace.html",
        project=project,
        messages=messages,
        files=files
    )

from flask import jsonify

@app.route("/project/<int:project_id>/messages")
@login_required
def get_messages(project_id):

    project = ProjectRequest.query.get_or_404(project_id)

    if (
        project.user_id != current_user.id
        and not current_user.is_admin
    ):
        return jsonify([]), 403

    messages = Message.query.filter_by(
        project_id=project.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    return jsonify([
        {
            "sender": message.sender,
            "text": message.message_text,
            "time": message.created_at.strftime("%d %b %Y %H:%M")
        }
        for message in messages
    ])
# ==========================================
# SEND PROJECT MESSAGE
# ==========================================

@app.route(
    "/project/<int:project_id>/message",
    methods=["POST"]
)
@login_required
def send_message(project_id):

    project = ProjectRequest.query.get_or_404(

        project_id

    )


    # Only the project owner or admin can send messages
    if (

        project.user_id != current_user.id

        and not current_user.is_admin

    ):

        return "Access denied", 403
    if not current_user.is_admin and project.status != "Accepted":

        flash(
        "Messaging is only available for accepted projects."
    )

        return redirect(
        url_for(
            "project_workspace",
            project_id=project.id
        )
    )

    message_text = request.form[

        "message"

    ].strip()


    if message_text:

        # Determine who sent the message
        sender = "Admin" if current_user.is_admin else "Customer"

        new_message = Message(
    project_id=project.id,
    sender=sender,
    message_text=message_text
)

        db.session.add(new_message)

        if current_user.is_admin:

            notification = Notification(
                user_id=project.user_id,
                project_id=project.id,
                message=f"Tifemi replied to your '{project.project_type}' project."
            )

            db.session.add(notification)
            try:
                send_email(
            "New Reply From Tifemi",
            project.email,
            f"""
    Hello {project.name},

    You have received a reply regarding your
    '{project.project_type}' project.

    Please log in to continue the conversation.
    """
        )
            except:
                pass

        else:

            admin = User.query.filter_by(
                is_admin=True
            ).first()

            notification = Notification(
                user_id=admin.id,
                project_id=project.id,
                message=f"{project.name} sent you a message about '{project.project_type}'."
            )

            db.session.add(notification)
            try:
                send_email(
                    mail,
                    app,
                    "New Customer Message",
                    admin.email,
                    f"""
            {project.name} has sent you a message regarding
            '{project.project_type}'.

            Please log in to reply.
            """
                )
            except:
                pass

        db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return "", 204

    return redirect(
    url_for(
        "project_workspace",
        project_id=project.id
    )
    
)
    

# ==========================================
# CANCEL PROJECT
# ==========================================

@app.route(
    "/project/<int:project_id>/cancel",
    methods=["POST"]
)
@login_required
def cancel_project(project_id):

    project = ProjectRequest.query.get_or_404(

        project_id

    )
    print(
    f"User={current_user.name}, "
    f"Admin={current_user.is_admin}, "
    f"Status={project.status}"
)


    # Only the project owner can cancel
    if project.user_id != current_user.id:

        return "Access denied", 403


    # Only allow cancellation of active projects
    if project.status not in [

        "New",

        "Accepted"

    ]:

        flash(

            "This project cannot be cancelled."

        )

        return redirect(

            url_for(

                "project_workspace",

                project_id=project.id

            )

        )


    cancellation_reason = request.form.get(

        "cancellation_reason",

        ""

    ).strip()


    if not cancellation_reason:

        flash(

            "Please provide a reason for cancelling."

        )

        return redirect(

            url_for(

                "project_workspace",

                project_id=project.id

            )

        )


    project.status = "Cancelled"
    admin = User.query.filter_by(is_admin=True).first()
    notification = Notification(
    user_id=admin.id,
    project_id=project.id,
    message=f"{project.name} cancelled '{project.project_type}'."
)
    db.session.add(notification)
    project.cancellation_reason = (

        cancellation_reason

    )


    db.session.commit()


    flash(

        "Your project has been cancelled."

    )


    return redirect(

        url_for(

            "customer_dashboard"

        )

    )

# ==========================================
# CREATE FIRST ADMIN
# ==========================================





# ==========================================
# FORGOT PASSWORD
# ==========================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "GET":

        return render_template(
            "forgot_password.html"
        )


    email = request.form.get(
        "email",
        ""
    ).strip().lower()
    print("FORGOT PASSWORD REQUEST FOR:", email)
    


    user = User.query.filter_by(

        email=email

    ).first()
    print("USER FOUND:", user is not None)

    # Do not reveal whether an email exists

    if not user:

        flash(
            "If an account exists with that email, "
            "a password reset link has been sent."
        )

        return redirect(

            url_for(
                "forgot_password"
            )

        )


    # Generate secure reset token

    token = secrets.token_urlsafe(32)


    # Save reset token

    user.reset_token = token

    user.reset_token_expires = (

        datetime.utcnow()

        + timedelta(hours=1)

    )


    db.session.commit()


    # Create reset URL

    reset_link = url_for(

        "reset_password",

        token=token,

        _external=True

    )


    # Create email

    email_message = MailMessage(

        subject="Reset Your Password",

        sender=app.config["MAIL_USERNAME"],

        recipients=[user.email]

    )


    email_message.body = f"""
Hello {user.name},

We received a request to reset the password
for your account.

Please click the link below to create a new password:

{reset_link}

This password reset link will expire in 1 hour.

If you did not request this password reset,
you can safely ignore this email.

Regards,

Tifemi
"""


    try:

        mail.send(
            email_message
        )


        print(
            "PASSWORD RESET EMAIL SENT TO:",
            user.email
        )


        flash(
            "If an account exists with that email, "
            "a password reset link has been sent."
        )


    except Exception as error:

        print(
            "PASSWORD RESET EMAIL ERROR:"
        )

        print(
            repr(error)
        )

        
        # Remove token if email failed

        user.reset_token = None

        user.reset_token_expires = None


        db.session.commit()


        flash(
            "There was a problem sending the "
            "password reset email. Please try again later."
        )


    return redirect(

        url_for(
            "forgot_password"
        )

    )

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash("Invalid or expired reset link.")
        return redirect(url_for("forgot_password"))

    if user.reset_token_expires < datetime.utcnow():
        flash("Reset link has expired.")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(request.url)

        user.password_hash = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expires = None

        db.session.commit()

        flash("Password updated successfully.")
        return redirect(url_for("login"))

    return render_template("reset_password.html")



@app.route(
    "/project/<int:project_id>/upload",
    methods=["POST"]
)
@login_required
def upload_file(project_id):

    project = ProjectRequest.query.get_or_404(project_id)

    if (
        project.user_id != current_user.id
        and not current_user.is_admin
    ):
        return "Access denied", 403

    if "file" not in request.files:
        flash("No file selected.")
        return redirect(
            url_for(
                "project_workspace",
                project_id=project.id
            )
        )

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.")
        return redirect(
            url_for(
                "project_workspace",
                project_id=project.id
            )
        )

    if file and allowed_file(file.filename):

        original_filename = file.filename

        saved_filename = (
            f"{uuid.uuid4().hex}_"
            f"{secure_filename(original_filename)}"
        )

        project_folder = os.path.join(
            app.config["UPLOAD_FOLDER"],
            f"project_{project.id}"
        )

        os.makedirs(project_folder, exist_ok=True)

        filepath = os.path.join(
            project_folder,
            saved_filename
        )

        file.save(filepath)
        file_size = os.path.getsize(filepath)

        extension = saved_filename.rsplit(".", 1)[1].lower()
        uploaded_by = (
            "Admin"
            if current_user.is_admin
            else "Customer"
        )

        db.session.add(

            ProjectFile(
                project_id=project.id,
                filename=saved_filename,
                original_filename=original_filename,
                file_size=file_size,
                file_type=extension,
                uploaded_by=uploaded_by
            )

        )

        if current_user.is_admin:

            recipient = User.query.get(project.user_id)

        else:

            recipient = User.query.filter_by(
        is_admin=True
    ).first()

        db.session.add(
            Notification(
                user_id=recipient.id,
                project_id=project.id,
                message=f"{current_user.name} uploaded '{original_filename}'."
            )
        )

        db.session.commit()

        flash("File uploaded successfully.")

    return redirect(
        url_for(
            "project_workspace",
            project_id=project.id
        )
    )
    
@app.route("/uploads/<int:project_id>/<filename>")
@login_required
def download_file(project_id, filename):

    project = ProjectRequest.query.get_or_404(project_id)

    if (
        project.user_id != current_user.id
        and not current_user.is_admin
    ):
        return "Access denied", 403

    project_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        f"project_{project.id}"
    )

    return send_from_directory(
        project_folder,
        filename,
        as_attachment=True
    )
@app.route("/notifications")
@login_required
def get_notifications():

    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(
        Notification.created_at.desc()
    ).all()
    print("\n========== NOTIFICATIONS ==========")
    print("Current User:", current_user.id)

    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(
        Notification.created_at.desc()
    ).all()

    print("Found:", len(notifications))

    for n in notifications:
        print(
            n.id,
            n.user_id,
            n.project_id,
            n.message
        )
    return jsonify({

        "count": len(notifications),

        "notifications": [

            {
                "id": notification.id,
                "message": notification.message,
                "project_id": notification.project_id
            }

            for notification in notifications

        ]

    })
    


@app.route("/notifications/read", methods=["POST"])
@login_required
def mark_notifications_read():

    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update(
        {"is_read": True}
    )

    db.session.commit()

    return "", 204

@app.route("/project/<int:project_id>/complete", methods=["POST"])
@login_required
def complete_project(project_id):

    if not current_user.is_admin:
        abort(403)

    project = ProjectRequest.query.get_or_404(project_id)

    project.status = "Completed"

    db.session.add(
        Notification(
            user_id=project.user_id,
            project_id=project.id,
            message="Your project has been completed."
        )
    )

    db.session.commit()

    flash("Project marked as completed.")

    return redirect(url_for("admin_dashboard"))

@app.route("/project/<int:project_id>/archive", methods=["POST"])
@login_required
def archive_project(project_id):

    if not current_user.is_admin:
        return "Access denied", 403

    project = ProjectRequest.query.get_or_404(project_id)

    project.is_archived = True

    db.session.commit()

    flash("Project archived.")

    return redirect(url_for("admin_dashboard"))
    

@app.route("/project/<int:project_id>/restore", methods=["POST"])
@login_required
def restore_project(project_id):

    if not current_user.is_admin:
        return "Access denied", 403

    project = ProjectRequest.query.get_or_404(project_id)

    project.is_archived = False

    db.session.commit()

    flash("Project restored.")

    return redirect(url_for("admin_dashboard"))

@app.route("/notification/<int:notification_id>")
@login_required
def open_notification(notification_id):

    notification = Notification.query.get_or_404(
        notification_id
    )

    if notification.user_id != current_user.id:
        return "Access denied", 403

    notification.is_read = True

    db.session.commit()

    return redirect(

        url_for(
            "project_workspace",
            project_id=notification.project_id
        )

        + "#chat-area"

    )

@app.route("/test-email")
def test_email():

    try:

        send_email(
    mail,
    app,
    "Resend Test",
    "ogunleyektifemi@gmail.com",
    "If you receive this email, Resend is working!"
)

        return "Email sent successfully."

    except Exception as e:

        import traceback
        traceback.print_exc()

        return f"<pre>{e}</pre>", 500

    
if __name__ == "__main__":
    app.run(debug=True)