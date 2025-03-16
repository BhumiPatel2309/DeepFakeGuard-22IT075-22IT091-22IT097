pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'deepfake-guard'
        DOCKER_TAG = 'latest'
        PYTHON_PATH = 'C:\Users\DELL\AppData\Local\Programs\Python\Python39\python.exe'  // Adjust this path to match your Python installation
        PIP_PATH = 'C:\Users\DELL\AppData\Local\Programs\Python\Python39\Scripts\pip.exe'  
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
                    bat "${env.PIP_PATH} install -r requirements.txt"
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    bat "${env.PYTHON_PATH} -m pytest tests/"
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    bat "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }
    }
    
    post {
        always {
            node('any') {
                cleanWs()
            }
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}