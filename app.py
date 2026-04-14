from flask import Flask

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Import route groups
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp

# Register them
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True) 