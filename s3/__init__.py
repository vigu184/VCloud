from flask import Flask, render_template, url_for, flash, redirect, request
from decouple import config
from boto3.session import Session
from tabulate import tabulate
from .forms import CreateBucketForm, DeleteBucketForm, FileForm, FileUploadForm
import botocore

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
REGION = config('REGION')

def get_client():
    return Session().client(
        's3',
        REGION,
        aws_access_key_id=config('S3_ACCESS_KEY'),
        aws_secret_access_key=config('S3_SECRET_ACCESS_KEY'),
        config=botocore.client.Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
    )

def get_resource_client():
    return Session().resource(
        's3',
        REGION,
        aws_access_key_id=config('S3_ACCESS_KEY'),
        aws_secret_access_key=config('S3_SECRET_ACCESS_KEY'),
        config=botocore.client.Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('create'):
            try:
                new_bucket_name = request.form.get('new_bucket_name').lower()
                client = get_resource_client()
                client.create_bucket(Bucket=new_bucket_name, CreateBucketConfiguration={'LocationConstraint': REGION})
                flash(f'Bucket {new_bucket_name} created successfully!', 'success')
            except client.meta.client.exceptions.BucketAlreadyExists as e:
                flash('Bucket {} already exists!'.format(e.response['Error']['BucketName']), 'danger')
            except client.meta.client.exceptions.BucketAlreadyOwnedByYou as e:
                flash('Bucket {} already owned by you!'.format(e.response['Error']['BucketName']), 'danger')
            except Exception as e:
                print(e)
                flash('Something went wrong!', 'danger')
        if request.form.get('delete'):
            return redirect(url_for('delete_bucket', bucket_name=request.form.get('bucket_name')))
    form = CreateBucketForm()
    response = get_client().list_buckets()
    bucket_forms = []
    if buckets := response.get('Buckets'):
        for bucket in buckets:
            bucket_forms.append((bucket.get('Name'), DeleteBucketForm(bucket_name=bucket.get('Name'))))
    return render_template('index.html', title='S3 Buckets', buckets=bucket_forms, form=form)

@app.route('/delete_bucket/<string:bucket_name>')
def delete_bucket(bucket_name: str):
    try:
        bucket = get_resource_client().Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        flash(f'Bucket {bucket_name} has been deleted successfully!', 'success')
    except Exception as e:
        print(e)
        flash('Something went wrong!', 'danger')
    return redirect(url_for('index'))

@app.route('/<string:bucket_name>', methods=['GET', 'POST'])
def display_bucket(bucket_name):
    if request.method == 'POST':
        if request.form.get('delete'):
            try:
                get_client().delete_object(
                    Bucket=request.form.get('bucket_name'),
                    Key=request.form.get('file_name'),
                )
                flash('{} has been deleted from {} successfully!'.format(request.form.get('file_name'), request.form.get('bucket_name')), 'success')
            except Exception as e:
                print(e)
                flash('Something went wrong!', 'danger')
        if request.form.get('upload'):
            file = request.files.get('file')
            try:
                get_client().upload_fileobj(file, bucket_name, file.filename)
                flash(f'File {file.filename} uploaded to bucket {bucket_name} successfully', 'success')
            except Exception as e:
                print(e)
                flash(f'Something went wrong!', 'danger')
    file_list = []
    upload_form = FileUploadForm()
    try:
        client = get_client()
        responce = client.list_objects_v2(Bucket=bucket_name)
        if files := responce.get('Contents'):
            for file in files:
                form = FileForm(bucket_name=bucket_name, file_name=file.get('Key'))
                download_url = create_presigned_url(bucket_name, file.get('Key'))
                if download_url:
                    file_list.append((file.get('Key'), form, download_url))
    except Exception as e:
        flash('Something went wrong!', 'danger')
        print(e)
    return render_template('display_buckets.html', title=bucket_name, files=file_list, upload_form=upload_form)

def create_presigned_url(bucket_name, object_name, expiration=36000):

    client = get_client()
    try:
        response = client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
                },
            ExpiresIn=expiration
            )
    except Exception as e:
        print(e)
        return None
    return response