from flask import Flask
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_session import Session
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.environ.get('secret_key')
app.config['SESSION_TYPE'] = 'cookie'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USER')

from api.login.mail import mail
mail.init_app(app)

###########################
####  D A T A B A S E  ####
###########################

from api.database import db

#########################
####  M E S S A G E S  ####
#########################

from api.messages_api import messages_bp
app.register_blueprint(messages_bp)

#####################
####  A D M I N  ####
#####################

from api.admin.a_dashboard import a_dashboard_bp
from api.admin.a_user_logs import a_user_logs_bp
from api.admin.a_edit_profile import a_edit_profile_bp
from api.admin.user_management.a_user_management import a_user_management_bp
from api.admin.user_management.add_user import add_user_bp
from api.admin.user_management.user_filter import user_filter_bp
from api.admin.user_management.edit_user import edit_user_bp
from api.admin.user_management.activate_user import activate_user_bp
from api.admin.user_management.restrict_user import restrict_user_bp
from api.admin.user_management.role_change import role_change_bp
from api.admin.user_management.restricted_accounts_api import restricted_accounts_bp
from api.admin.user_management.archive_user import archive_user_bp
from api.admin.police_reports.police_admin_report import police_admin_report_bp
from api.admin.audit_trail.audit_trail import audit_trail_bp

app.register_blueprint(a_dashboard_bp)
app.register_blueprint(a_user_logs_bp)
app.register_blueprint(a_edit_profile_bp)
app.register_blueprint(a_user_management_bp)
app.register_blueprint(add_user_bp)
app.register_blueprint(user_filter_bp)
app.register_blueprint(edit_user_bp)
app.register_blueprint(activate_user_bp)
app.register_blueprint(restrict_user_bp)
app.register_blueprint(role_change_bp)
app.register_blueprint(restricted_accounts_bp)
app.register_blueprint(archive_user_bp)
app.register_blueprint(police_admin_report_bp)
app.register_blueprint(audit_trail_bp)

#####################
####  L O G I N  ####
#####################

from api.login.login import login_bp
from api.login.mail import mail_bp
from api.login.submit_otp import submit_otp_bp
from api.login.reset_password import reset_password_bp

app.register_blueprint(login_bp)
app.register_blueprint(mail_bp)
app.register_blueprint(submit_otp_bp)
app.register_blueprint(reset_password_bp)

#######################
####  P O L I C E  ####
#######################

from api.police.a_dashboard.p_dashboard import p_dashboard_bp
from api.police.b_field_report.p_field_report import p_field_report_bp
from api.police.b_field_report.report_details import report_details_bp
from api.police.b_field_report.edit_report import edit_report_bp
from api.police.b_field_report.print_field_report import print_field_report_bp
from api.police.b_field_report.approval_status import approval_status_bp
from api.police.b_field_report.archive_report import archive_report_bp
from api.police.b_field_report.follow_up_report import follow_up_report_bp
from api.police.b_field_report.unarchive_report import unarchive_report_bp
from api.police.c_case_management.p_case_management import p_case_management_bp
from api.police.c_case_management.case_details import case_details_bp
from api.police.c_case_management.archive_case import archive_case_bp
from api.police.c_case_management.archived_images import archived_images_bp
from api.police.c_case_management.assign_officer import assign_officer_bp
from api.police.c_case_management.edit_case import edit_case_bp
from api.police.c_case_management.police_delete_img import police_delete_img_bp
from api.police.c_case_management.unarchived_image import unarchived_image_bp
from api.police.c_case_management.print_case_management import print_case_management_bp
from api.police.case_timeline import case_timeline_bp
from api.police.p_incident_map import p_incident_map_bp
from api.police.p_edit_profile import p_edit_profile_bp
from api.police.p_notifications import p_notifications_bp

app.register_blueprint(p_dashboard_bp)
app.register_blueprint(p_field_report_bp)
app.register_blueprint(report_details_bp)
app.register_blueprint(edit_report_bp)
app.register_blueprint(print_field_report_bp)
app.register_blueprint(approval_status_bp)
app.register_blueprint(archive_report_bp)
app.register_blueprint(follow_up_report_bp)
app.register_blueprint(unarchive_report_bp)
app.register_blueprint(p_case_management_bp)
app.register_blueprint(case_details_bp)
app.register_blueprint(archive_case_bp)
app.register_blueprint(archived_images_bp)
app.register_blueprint(assign_officer_bp)
app.register_blueprint(edit_case_bp)
app.register_blueprint(police_delete_img_bp)
app.register_blueprint(unarchived_image_bp)
app.register_blueprint(print_case_management_bp)
app.register_blueprint(case_timeline_bp)
app.register_blueprint(p_incident_map_bp)
app.register_blueprint(p_edit_profile_bp)
app.register_blueprint(p_notifications_bp)

#####################
####  U S E R S  ####
#####################

from api.public_users.u_public_view import public_view_bp
from api.public_users.u_get_help import get_help_bp
from api.public_users.u_community import community_bp
from api.public_users.u_about import about_bp
from api.public_users.u_help_us import help_us_bp
from api.public_users.u_professional import professional_bp
from api.public_users.u_talk_to_us import talk_to_us_bp
from api.public_users.u_report_missing import report_missing_bp
from api.public_users.u_report_sighting import report_sighting_bp
from api.public_users.u_status_report import status_report_bp
from api.public_users.u_resources import resources_bp
from api.public_users.u_edit_profile import user_edit_bp

app.register_blueprint(public_view_bp)
app.register_blueprint(get_help_bp)
app.register_blueprint(community_bp)
app.register_blueprint(about_bp)
app.register_blueprint(help_us_bp)
app.register_blueprint(professional_bp)
app.register_blueprint(talk_to_us_bp)
app.register_blueprint(report_missing_bp)
app.register_blueprint(report_sighting_bp)
app.register_blueprint(status_report_bp)
app.register_blueprint(resources_bp)
app.register_blueprint(user_edit_bp)

###########################
####  R E G I S T E R  ####
###########################

from api.register.registration import registration_bp
app.register_blueprint(registration_bp)
