from app import app

@app.route("/")
def home():
    return "Hello from Flask CI/CD with GitHub Actions, Trivy, Docker Hub, and Argo CD!!!!"