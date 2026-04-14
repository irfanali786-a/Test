pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python') {
            steps {
                bat 'cd gist-api && python -m venv venv'
                bat 'cd gist-api && call venv\\Scripts\\activate.bat && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps { bat 'cd gist-api && call venv\\Scripts\\activate.bat && pytest -q' }
        }

        stage('Static Analysis') {
            steps { bat 'cd gist-api && call venv\\Scripts\\activate.bat && pip install bandit && bandit -r app' }
        }

        stage('Dependency Scan') {
            steps { bat 'cd gist-api && call venv\\Scripts\\activate.bat && pip install pip-audit && pip-audit' }
        }

        stage('Build Docker Image') {
            steps { bat 'cd gist-api && docker build -t gist-api:latest .' }
        }

        stage('Docker Scan') {
            steps {
                bat 'cd gist-api && docker save gist-api:latest -o gist-api.tar'
                bat 'docker run --rm -v %cd%\\gist-api:/tmp aquasec/trivy:0.55.0 image --input /tmp/gist-api.tar'
            }
        }

        stage('Smoke Test') {
            steps {
                bat '''
                docker stop gist-api >nul 2>&1 || true
                docker rm gist-api >nul 2>&1 || true
                docker run -d -p 8080:8080 --name gist-api gist-api:latest
                timeout /t 5 /nobreak
                powershell -Command "try { $response = Invoke-WebRequest http://localhost:8080/health -ErrorAction Stop; if($response.StatusCode -ne 200) { exit 1 } } catch { exit 1 }"
                docker rm -f gist-api >nul 2>&1
                '''
            }
        }
    }
}
