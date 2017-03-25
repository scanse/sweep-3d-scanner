from flask import Flask, render_template, flash, send_file
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, TextField, validators
import cli_controls
import glob
import os
import sys

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class FileManager(Form):
    scan_file = SelectField(
        label='Scan:',
        choices=[],
        validators=[validators.required()]
    )
    download = SubmitField(label='Download')
    delete = SubmitField(label='Delete')


class ScanSettingsForm(Form):
    """Docstring"""
    motor_speed = SelectField(
        label='Motor Speed:',
        choices=[('1', '1Hz'), ('2', '2Hz'), ('3', '3Hz')],
        validators=[validators.required()]
    )

    sample_rate = SelectField(
        label='Sample Rate:',
        choices=[('500', '500Hz'), ('750', '750Hz'), ('1000', '1000Hz')],
        validators=[validators.required()]
    )

    scan_type = SelectField(
        label='Scan Type:',
        choices=[('360', 'Full Scan (360)'), ('180', 'Half Scan (180)'),
                 ('90', 'Partial Scan (90)'), ('30', 'Partial Scan (30)')],
        validators=[validators.required()]
    )

    file_name = TextField(
        label='Filename:',
        validators=[validators.required()]
    )


class ScannerTestsForm(Form):
    """Docstring"""
    test_type = SelectField(
        label='Test Type:',
        choices=[('base', 'Base'), ('limit_switch', 'Limit Switch')],
        validators=[validators.required()])

    run_test = SubmitField(label='Run Test')


class DeviceForm(Form):
    """Docstring"""
    shutdown = SubmitField(label='Shutdown Pi')
    restart = SubmitField(label='Restart Pi')
    idle = SubmitField(label='Idle Sweep')

# route to the root of the website... ie: http://IP-ADDRESS:5000/


@app.route('/')
def index():
    """Name given to the route"""
    return render_template('index.html')  # looks for `index.html` in `templates/` dir


@app.route('/device', methods=['GET', 'POST'])
def device():
    """Name given to the route"""
    form = DeviceForm()

    if form.validate_on_submit():
        button = 'unknown'
        if form.restart.data:
            button = 'restart'
            cli_controls.restart_pi()
        elif form.shutdown.data:
            button = 'shutdown'
            cli_controls.shutdown_pi()
        elif form.idle.data:
            button = 'idle'
            cli_controls.idle()

        flash(
            "You submitted form via button {button}".format(button=button)
        )

        return render_template('device.html', form=form)

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Error: {error}; Field : {field};".format(
                error=error_message, field=error_field))

    return render_template('device.html', form=form)


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    """Handles scan page"""
    form = ScanSettingsForm()

    if form.validate_on_submit():
        # read settings from the form
        motor_speed = int(form.motor_speed.data)
        sample_rate = int(form.sample_rate.data)
        scan_type = int(form.scan_type.data)
        file_name = form.file_name.data + '.csv'

        # notify the user
        flash(
            'Performing a {} degree scan with MS={}Hz, SR={}Hz. Saving to file {}'.format(
                scan_type, motor_speed, sample_rate, file_name
            )
        )

        curr_pathname = os.path.dirname(sys.argv[0])
        curr_abs_pathname = os.path.abspath(curr_pathname)
        export_dir_path = os.path.join(curr_abs_pathname, 'output_scans')
        abs_export_file_path = os.path.join(export_dir_path, file_name)

        # perform the scan
        cli_controls.perform_scan(
            motor_speed=motor_speed,
            sample_rate=sample_rate,
            angular_range=scan_type,
            output_path=abs_export_file_path
        )
        return render_template('scan_settings_form.html', form=form)

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Error: {error}; Field : {field};".format(
                error=error_message, field=error_field))

    return render_template('scan_settings_form.html', form=form)


@app.route('/tests', methods=['GET', 'POST'])
def tests():
    """Handles scanner test page"""
    form = ScannerTestsForm()

    if form.validate_on_submit():
        test_type = form.test_type.data
        if test_type == 'base':
            cli_controls.test_base()
        elif test_type == 'limit_switch':
            cli_controls.test_limit_switch()

        flash('Performing a test of type ' + test_type)
        return render_template('scanner_tests.html', form=form)

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Error: {error}; Field : {field};".format(
                error=error_message, field=error_field))

    return render_template('scanner_tests.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def files():
    """Handles file management"""
    curr_pathname = os.path.dirname(sys.argv[0])
    curr_abs_pathname = os.path.abspath(curr_pathname)
    export_dir_path = os.path.join(curr_abs_pathname, 'output_scans')
    scan_files = glob.glob("{}/*.csv".format(export_dir_path))

    if len(scan_files) <= 0:
        flash('Error: No scan files found. Try taking a scan.')

    file_choices = [(f, os.path.split(f)[1]) for f in scan_files]
    form = FileManager()
    form.scan_file.choices = file_choices

    if form.validate_on_submit():
        scan_file = form.scan_file.data

        if form.download.data:
            return send_file(scan_file,
                             mimetype='text/csv',
                             attachment_filename=os.path.split(scan_file)[1],
                             as_attachment=True)
        elif form.delete.data:
            # delete the file
            delete_file(scan_file)
            # update the listed files to reflect the change
            scan_files = glob.glob("{}/*.csv".format(export_dir_path))
            file_choices = [(f, os.path.split(f)[1]) for f in scan_files]
            form.scan_file.choices = file_choices
            # notify the user
            flash('Deleted {}'.format(scan_file))

        return render_template('file_manager.html', form=form)

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Error: {error}; Field : {field};".format(
                error=error_message, field=error_field))

    return render_template('file_manager.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    """Handles page not found"""
    return render_template('page_not_found.html'), 404


def delete_file(abs_file_path):
    """Delete a file"""
    print 'Trying to delete {}'.format(abs_file_path)
    os.remove(abs_file_path)

if __name__ == '__main__':
    cli_controls.idle()
    # web app will be accessible to any device on the network
    app.run(debug=True, host='0.0.0.0')
