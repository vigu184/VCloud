from s3 import app

'''
set debug=False bellow when deploying to prod
'''
app.run(host='0.0.0.0', debug=True)