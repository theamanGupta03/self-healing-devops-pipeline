pipeline {
    agent any

    environment {
        APP_NAME = "self-healing-app"
        CONTAINER_NAME = "self-healing-container"
        PORT = "5000"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git 'https://github.com/theamanGupta03/self-healing-devops-pipeline.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $APP_NAME ./app'
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker stop $CONTAINER_NAME || true
                docker rm $CONTAINER_NAME || true
                docker run -d -p $PORT:$PORT --name $CONTAINER_NAME $APP_NAME
                '''
            }
        }

        stage('Health Check') {
            steps {
                script {
                    sleep 10
                    def status = sh(
                        script: "curl -s http://localhost:$PORT || echo fail",
                        returnStdout: true
                    ).trim()

                    if (status.contains("fail")) {
                        error("Health check failed")
                    } else {
                        echo "App is healthy"
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "⚠️ Pipeline failed → Starting Self-Healing..."

            sh '''
            echo "Restarting container..."
            docker restart $CONTAINER_NAME
            sleep 5
            echo "Re-checking health..."
            curl -s http://localhost:$PORT || echo "Still failing"
            '''
        }

        success {
            echo "✅ Application deployed successfully and is healthy!"
        }
    }
}