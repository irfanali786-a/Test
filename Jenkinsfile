pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python') {
            steps {
                bat 'python -m venv venv'
                bat 'call venv\\Scripts\\activate.bat && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps { bat 'call venv\\Scripts\\activate.bat && pytest -q' }
        }

        stage('Static Analysis') {
            steps { bat 'call venv\\Scripts\\activate.bat && pip install bandit && bandit -r app' }
        }

        stage('Dependency Scan') {
            steps { bat 'call venv\\Scripts\\activate.bat && pip install pip-audit && pip-audit' }
        }

        stage('Build Docker Image') {
            steps { bat 'docker build -t gist-api:latest .' }
        }

        stage('Docker Scan') {
            steps { bat 'docker run --rm aquasec/trivy image gist-api:latest' }
        }

        stage('Smoke Test') {
            steps {
                bat '''
                docker run -d -p 8080:8080 --name gist-api gist-api:latest
                timeout /t 5
                curl --fail http://localhost:8080/health
                docker rm -f gist-api
                '''
            }
        }
    }
}
