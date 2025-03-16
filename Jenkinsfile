pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'deepfake-guard'
        DOCKER_TAG = 'latest'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    // Use bat for Windows
                    bat 'pip install -r requirements.txt'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    bat 'python -m pytest tests/'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Windows-compatible docker build command
                    bat "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }
    }
    
    post {
        always {
            node('any') {  // Ensure cleanup runs within a node
                cleanWs()
            }
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}