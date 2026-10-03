pipeline {
    agent any

    environment {
        DJANGO_ENV_FILE = credentials('retrodoc-backend-env')
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

        stage('Django checks') {
            steps {
                sh '''
                    set -a
                    . "$DJANGO_ENV_FILE"
                    set +a

                    . .venv/bin/activate

                    python manage.py check
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    set -a
                    . "$DJANGO_ENV_FILE"
                    set +a

                    . .venv/bin/activate

                    python manage.py test
                '''
            }
        }
    }

    post {
        success {
            echo 'Backend CI passed.'
        }

        failure {
            echo 'Backend CI failed.'
        }
    }
}
