from flask import Flask, session, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_session import Session
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.environ.get('secret_key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
Session(app)

###########################
####  D A T A B A S E  ####
###########################

from api.database import db

#########################
####  M E S S A G E S  ####
#########################

from api.messages_api import messages_bp
app.register_blueprint(messages_bp)
print("=== MESSAGES BLUEPRINT REGISTERED ===")

#####################
####  A D M I N  ####
#####################

from api.admin import a_dashboard

from api.admin.user_management import a_user_management
from api.admin.user_management import add_user
from api.admin.user_management import user_filter
from api.admin.user_management import edit_user
from api.admin.user_management import activate_user
from api.admin.user_management import restrict_user
from api.admin.user_management import role_change
from api.admin.user_management import restricted_accounts_api
from api.admin.user_management import archive_user
from api.admin.police_reports import police_admin_report

from api.admin.audit_trail import audit_trail
from api.admin import a_user_logs
from api.admin import a_edit_profile
from api import audit


#####################
####  L O G I N  ####
#####################

from api.login import login
from api.login import mail
from api.login import submit_otp
from api.login import reset_password

#######################
####  P O L I C E  ####
#######################

from api.police.a_dashboard import p_dashboard
from api.police.b_field_report import p_field_report
from api.police.b_field_report import report_details
from api.police.b_field_report import edit_report
from api.police.b_field_report import print_field_report
from api.police.b_field_report import approval_status
from api.police.b_field_report import archive_report
from api.police.b_field_report import follow_up_report
from api.police.b_field_report import unarchive_report

from api.police.c_case_management import p_case_management
from api.police.c_case_management import case_details
from api.police.c_case_management import archive_case
from api.police.c_case_management import archived_images
from api.police.c_case_management import assign_officer
from api.police.c_case_management import edit_case
from api.police.c_case_management import police_delete_img
from api.police.c_case_management import unarchived_image
from api.police.c_case_management import print_case_management

from api.police import case_history
from api.police import case_timeline
from api.police import p_incident_map
from api.police import p_edit_profile
from api.police import p_notifications

#####################
####  U S E R S  ####
#####################

from api.public_users import u_public_view
from api.public_users import u_get_help
from api.public_users import u_community
from api.public_users import u_about
from api.public_users import u_help_us
from api.public_users import u_professional
from api.public_users import u_talk_to_us
from api.public_users import u_report_missing
from api.public_users import u_report_sighting
from api.public_users import u_status_report
from api.public_users import u_resources
from api.public_users import u_edit_profile

###########################
####  R E G I S T E R  ####
###########################

from api.register import registration