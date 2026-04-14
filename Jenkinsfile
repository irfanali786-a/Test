pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python') {
            steps {
                sh 'python3.12 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps { sh '. venv/bin/activate && pytest -q' }
        }

        stage('Static Analysis') {
            steps { sh '. venv/bin/activate && pip install bandit && bandit -r app' }
        }

        stage('Dependency Scan') {
            steps { sh '. venv/bin/activate && pip install pip-audit && pip-audit' }
        }

        stage('Build Docker Image') {
            steps { sh 'docker build -t gist-api:latest .' }
        }

        stage('Docker Scan') {
            steps { sh 'docker run --rm aquasec/trivy image gist-api:latest' }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                docker run -d -p 8080:8080 --name gist-api gist-api:latest
                sleep 5
                curl --fail http://localhost:8080/health
                docker rm -f gist-api
                '''
            }
        }
    }
}
