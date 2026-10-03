pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE = 'les190/retrodoc-backend'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DJANGO_ENV_FILE = credentials('retrodoc-backend-env')
        DJANGO_SETTINGS_MODULE = 'config.settings.production'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Version') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Backend version: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    cp "$DJANGO_ENV_FILE" .env
                    chmod 600 .env
                '''
            }
        }

        stage('Django Checks') {
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

        stage('Docker Build & Push') {
            when {
                branch 'main'
            }

            steps {
                sh '''
                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login \
                        -u "$DOCKERHUB_CREDENTIALS_USR" \
                        --password-stdin

                    docker build \
                        -t "$DOCKER_IMAGE:$IMAGE_TAG" \
                        -t "$DOCKER_IMAGE:latest" \
                        .

                    docker push "$DOCKER_IMAGE:$IMAGE_TAG"
                    docker push "$DOCKER_IMAGE:latest"

                    docker logout
                '''
            }
        }

        stage('Trigger Production Deployment') {
            when {
                branch 'main'
            }

            steps {
                build job: 'RetroDoc/retrodoc-devops/main',
                    wait: false,
                    parameters: [
                        string(
                            name: 'BACKEND_VERSION',
                            value: "${env.IMAGE_TAG}"
                        ),
                        string(
                            name: 'FRONTEND_VERSION',
                            value: ''
                        )
                    ]
            }
        }
    }

    post {
        always {
            sh 'rm -f .env || true'
            sh 'rm -rf .venv || true'
        }

        success {
            echo "Backend CI completed successfully."
        }

        failure {
            echo "Backend CI failed."
        }
    }
}