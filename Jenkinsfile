pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE_PROJECT_NAME = 'guestbook'
        BACKEND_URL = 'http://host.docker.internal:5000/health'
        FRONTEND_URL = 'http://host.docker.internal:8081/'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Mengambil kode terbaru dari GitHub...'

                checkout scm

                sh '''
                    echo "========== PROJECT FILES =========="
                    ls -la
                '''
            }
        }

        stage('Syntax Check') {
            steps {
                echo 'Memeriksa sintaks Python dan Docker Compose...'

                sh '''
                    set -e

                    python3 -m py_compile app.py

                    docker compose config -q

                    echo "Syntax check berhasil!"
                '''
            }
        }

        stage('Check Docker Version') {
            steps {
                echo 'Memeriksa Docker, Compose, dan Buildx...'

                sh '''
                    set -e

                    echo "========== DOCKER VERSION =========="
                    docker version

                    echo "========== DOCKER COMPOSE =========="
                    docker compose version

                    echo "========== DOCKER BUILDX =========="
                    docker buildx version

                    echo "========== BUILDX BUILDER =========="
                    docker buildx ls
                '''
            }
        }

        stage('Build Images') {
            steps {
                echo 'Membangun image backend dan frontend...'

                sh '''
                    set -e

                    docker compose build
                '''
            }
        }

        stage('Automated Deployment') {
            steps {
                echo 'Melakukan deployment aplikasi...'

                sh '''
                    set -e

                    docker compose up -d --force-recreate --remove-orphans

                    echo "========== CONTAINER STATUS =========="

                    docker compose ps
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo 'Memeriksa kesehatan backend dan frontend...'

                sh '''
                    set +e

                    BACKEND_STATUS=""
                    FRONTEND_STATUS=""

                    for i in $(seq 1 15); do

                        echo "Health check attempt $i/15"

                        BACKEND_STATUS=$(curl -s \
                            -o /dev/null \
                            -w "%{http_code}" \
                            --connect-timeout 5 \
                            --max-time 10 \
                            "$BACKEND_URL")

                        FRONTEND_STATUS=$(curl -s \
                            -o /dev/null \
                            -w "%{http_code}" \
                            --connect-timeout 5 \
                            --max-time 10 \
                            "$FRONTEND_URL")

                        echo "Backend HTTP: $BACKEND_STATUS"
                        echo "Frontend HTTP: $FRONTEND_STATUS"

                        if [ "$BACKEND_STATUS" = "200" ] && \
                           [ "$FRONTEND_STATUS" = "200" ]; then

                            echo "=================================="
                            echo "HEALTH CHECK BERHASIL!"
                            echo "Backend: HTTP 200"
                            echo "Frontend: HTTP 200"
                            echo "=================================="

                            exit 0
                        fi

                        sleep 2
                    done

                    echo "=================================="
                    echo "HEALTH CHECK GAGAL!"
                    echo "=================================="

                    exit 1
                '''
            }
        }
    }

    post {

        success {
            echo '''
            ==========================================
                 JENKINS PIPELINE BERHASIL!
            ==========================================
                 Backend  : Running
                 Frontend : Running
                 Build    : Success
                 Deploy   : Success
                 Health   : Passed

                 Frontend:
                 http://localhost:8081

                 Backend:
                 http://localhost:5000/health
            ==========================================
            '''
        }

        failure {
            echo 'Pipeline gagal. Memeriksa log container...'

            sh '''
                echo "========== CONTAINER STATUS =========="

                docker compose ps

                echo "========== CONTAINER LOGS =========="

                docker compose logs --tail=50 || true

                echo "========== DOCKER NETWORK =========="

                docker network ls
            '''
        }

        always {
            echo 'Jenkins Pipeline selesai.'
        }
    }
}
