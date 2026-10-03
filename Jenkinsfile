pipeline {
    agent any

    environment {
        DJANGO_ENV_FILE = credentials('retrodoc-backend-env')
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')

        DOCKER_IMAGE = 'les190/retrodoc-backend'

        DJANGO_SETTINGS_MODULE = 'config.settings.production'

        DEVOPS_JOB = 'RetroDoc/retrodoc-devops/main'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Build Variables') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Backend image tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    set -eu

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
                    set -eu

                    cp "$DJANGO_ENV_FILE" .env
                    chmod 600 .env
                '''
            }
        }

        stage('Django checks') {
            steps {
                sh '''
                    set -eu

                    . .venv/bin/activate

                    python manage.py check
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    set -eu

                    . .venv/bin/activate

                    python manage.py test
                '''
            }
        }

        stage('Docker Build') {
            when {
                branch 'main'
            }

            steps {
                sh '''
                    set -eu

                    docker build \
                        -t "$DOCKER_IMAGE:$IMAGE_TAG" \
                        -t "$DOCKER_IMAGE:latest" \
                        .
                '''
            }
        }

        stage('Docker Push') {
            when {
                branch 'main'
            }

            steps {
                sh '''
                    set -eu

                    echo "$DOCKERHUB_CREDENTIALS_PSW" | \
                        docker login \
                        -u "$DOCKERHUB_CREDENTIALS_USR" \
                        --password-stdin

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
                script {
                    build(
                        job: env.DEVOPS_JOB,
                        wait: true,
                        parameters: [
                            string(
                                name: 'BACKEND_VERSION',
                                value: env.IMAGE_TAG
                            ),
                            string(
                                name: 'FRONTEND_VERSION',
                                value: 'latest'
                            )
                        ]
                    )
                }
            }
        }
    }

    post {
        always {
            sh '''
                rm -f .env
                rm -rf .venv
            '''
        }

        success {
            echo "Backend CI/CD completed successfully."
            echo "Backend image: $DOCKER_IMAGE:$IMAGE_TAG"
        }

        failure {
            echo 'Backend CI/CD failed.'
        }
    }
}