# AWS-S3

manage aws s3 buckets using web application

## How to run

- Clone the repository
    ```bash
    git clone https://github.com/prkprime/aws-s3
    ```

- make .env file in aws-s3 folder with following content
    ```env
    S3_ACCESS_KEY="<your aws access key>"
    S3_SECRET_ACCESS_KEY="<your aws secreat access key>"
    SECRET_KEY="<some secret key for your flask app>"
    REGION="<aws region. for eg. 'ap-south-1'>"
    ```

- create and activate virtual environment and install requirements
    ```bash
    python3 -m venv venv/
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

- run the app using gunicorn server
    ```bash
    gunicorn s3:app
    ```