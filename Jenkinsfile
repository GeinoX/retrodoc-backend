pipeline {
    agent any

    environment {
        DJANGO_SECRET_KEY = credentials('django-secret-key')
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
                    . .venv/bin/activate

                    export SECRET_KEY="$DJANGO_SECRET_KEY"

                    python manage.py check
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    . .venv/bin/activate

                    export SECRET_KEY="$DJANGO_SECRET_KEY"

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
