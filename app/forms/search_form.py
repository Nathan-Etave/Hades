from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class SearchForm(FlaskForm):
    """
    Represents a search form.

    Attributes:
        search (StringField): The search input field.
        submit (SubmitField): The submit button for the form.
    """
    search = StringField('Recherche')
    submit = SubmitField('Rechercher')