from flask import Flask, redirect, render_template, abort, url_for
from flask.ext.wtf import Form
from flask.ext.redis import Redis
from flask.ext.compass import Compass

from wtforms.validators import Required, URL
from wtforms.fields.html5 import URLField
from wtforms import SubmitField

import string
import random

class URLForm(Form):
    url = URLField('url', validators=[Required(), URL()])
    submit = SubmitField('Dwarf!')

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://:@localhost:6379/0"
app.config['SECRET_KEY'] = 'Cant-guess-me'
compass = Compass(app)
r = Redis(app)

@app.route('/<dwarf_url>')
def reroute(dwarf_url):
    url = r.get('short-url:' + dwarf_url)
    if not url:
        abort(404)

    return redirect(url)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()

    if form.validate_on_submit():
        dwarf_url = r.get('reverse-url:' + form.url.data)
        if not dwarf_url:
            chars = string.ascii_letters + string.digits
            dwarf_url = ''.join(random.choice(chars) for x in range(5))
            r.set('short-url:' + dwarf_url, form.url.data)
            r.set('reverse-url:' + form.url.data, dwarf_url)

        url = url_for('reroute', dwarf_url=dwarf_url, _external=True)
        return render_template('dwarfed.html', url=url)

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
