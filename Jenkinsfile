pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/theamanGupta03/self-healing-devops-pipeline.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t self-healing-app ./app'
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker rm -f self-healing-container || true
                docker run -d -p 5000:5000 --name self-healing-container self-healing-app
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                sleep 5
                curl -f http://localhost:5000/health
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded: Application is healthy'
        }
        failure {
            echo 'Pipeline failed: Application health check failed'
        }
    }
}
