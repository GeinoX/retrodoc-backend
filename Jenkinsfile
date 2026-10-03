pipeline {
    agent any

    environment {
        DJANGO_ENV_FILE = credentials('retrodoc-backend-env')
        DJANGO_SETTINGS_MODULE = 'config.settings.production'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Prepare environment') {
            steps {
                sh '''
                    cp "$DJANGO_ENV_FILE" .env
                    chmod 600 .env
                '''
            }
        }

        stage('Django checks') {
            steps {
                sh '''
                    . .venv/bin/activate

                    python manage.py check
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    . .venv/bin/activate

                    python manage.py test
                '''
            }
        }
    }

    post {
        always {
            sh '''
                rm -f .env
            '''
        }

        success {
            echo 'Backend CI passed.'
        }

        failure {
            echo 'Backend CI failed.'
        }
    }
}