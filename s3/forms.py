from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class CreateBucketForm(FlaskForm):
    new_bucket_name = StringField(
        'Bucket Name',
        validators = [
            DataRequired()
        ]
    )

    create = SubmitField('Create')

class DeleteBucketForm(FlaskForm):
    bucket_name = HiddenField()

    delete = SubmitField('Delete')

class FileForm(FlaskForm):
    bucket_name = HiddenField()

    file_name = HiddenField()

    delete = SubmitField('Delete')

class FileUploadForm(FlaskForm):
    file = FileField(
        'Select File',
        validators=[
            DataRequired()
        ]
        )

    upload = SubmitField('Upload')