from flask import Flask, render_template, flash, request
from wtforms import Form, SelectField, TextField, TextAreaField, validators, StringField, SubmitField

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ScanSettingsForm(Form):
    """Docstring"""
    motor_speed = SelectField(u'Motor Speed:', choices=[(
        '1', '1Hz'), ('2', '2Hz'), ('3', '3Hz')], validators=[validators.required()])

    sample_rate = SelectField(u'Sample Rate:', choices=[(
        '500', '500Hz'), ('750', '750Hz'), ('1000', '1000Hz')], validators=[validators.required()])

    scan_type = SelectField(u'Scan Type:', choices=[('360', 'Full Scan (360)'), ('180', 'Half Scan (180)'), (
        '90', 'Partial Scan (90)'), ('30', 'Partial Scan (30)')], validators=[validators.required()])

    file_name = TextField('Filename:', validators=[validators.required()])

# route to the root of the website... ie: http://IP-ADDRESS:5000/
@app.route('/')
def index():
    """Name given to the route"""
    return render_template('index.html')  # looks for `index.html` in `templates/` dir


@app.route('/hello/')
# <name> is passed into hello fxn below as the `name` param
@app.route('/hello/<name>')
def hello(name=None):
    """Name given to the route"""
    return render_template('page.html', name=name)


@app.route('/test')
def test():
    """Name given to the route"""
    # return 'This is a test!'
    return render_template('test.html')


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    form = ScanSettingsForm(request.form)

    print form.errors
    if request.method == 'POST':
        motor_speed = request.form['motor_speed']
        sample_rate = request.form['sample_rate']
        scan_type = request.form['scan_type']

        if form.validate():
            # Save the comment here.
            flash('Performing a ' + scan_type + ' degree scan with MS=' +
                  motor_speed + 'Hz, SR=' + sample_rate + 'Hz.')
        else:
            flash('Error: All the form fields are required.')

    return render_template('scan_settings_form.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    # web app will be accessible to any device on the network
    app.run(debug=True, host='0.0.0.0')
