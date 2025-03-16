pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'deepfakeguard-web'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS = credentials('docker-hub')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    python -m pytest tests/ --cov=src --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${deepfakeguard-web}:${latest}")
                }
            }
        }
        
        stage('Run Security Scan') {
            steps {
                script {
                    sh '''
                        docker scan ${deepfakeguard-web}:${latest}
                    '''
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-credentials') {
                        docker.image("${deepfakeguard-web}:${latest}").push()
                        docker.image("${deepfakeguard-web}:${latest}").push('latest')
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    sh '''
                        docker-compose down
                        docker-compose up -d
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}