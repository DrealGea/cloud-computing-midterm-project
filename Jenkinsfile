pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    // Otomatis dipicu GitHub Webhook
    triggers {
        githubPush()
    }

    environment {
        BACKEND_URL  = 'http://localhost:5000'
        FRONTEND_URL = 'http://localhost:8081'
    }

    stages {

        // ---------- STAGE 1: CHECKOUT ----------
        stage('Checkout') {
            steps {
                echo 'Mengambil kode terbaru dari GitHub...'

                checkout scm

                sh 'ls -la'
            }
        }

        // ---------- STAGE 2: SYNTAX CHECK ----------
        stage('Syntax Check') {
            steps {
                echo 'Memeriksa sintaks Python dan Docker Compose...'

                sh '''
                    python3 -m py_compile app.py
                    docker compose config -q
                '''
            }
        }

        // ---------- STAGE 3: CHECK DOCKER ----------
        stage('Check Docker Version') {
            steps {
                echo 'Memeriksa Docker, Compose, dan Buildx...'

                sh '''
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

        // ---------- STAGE 4: BUILD IMAGES ----------
        stage('Build Images') {
            steps {
                echo 'Membangun image backend dan frontend...'

                sh '''
                    docker compose build
                '''
            }
        }

        // ---------- STAGE 5: DEPLOYMENT ----------
        stage('Automated Deployment') {
            steps {
                echo 'Melakukan deployment aplikasi...'

                sh '''
                    docker compose up -d --force-recreate --remove-orphans

                    echo "========== CONTAINER STATUS =========="

                    docker compose ps
                '''
            }
        }

        // ---------- STAGE 6: HEALTH CHECK ----------
        stage('Health Check') {
            steps {
                echo 'Memeriksa kesehatan backend dan frontend...'

                sh '''
                    set +e

                    for i in $(seq 1 15); do

                        echo "Health check attempt $i/15"

                        BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
                        FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/")

                        echo "Backend HTTP: $BACKEND_STATUS"
                        echo "Frontend HTTP: $FRONTEND_STATUS"

                        if [ "$BACKEND_STATUS" = "200" ] && [ "$FRONTEND_STATUS" = "200" ]; then
                            echo "Health check berhasil!"
                            exit 0
                        fi

                        sleep 2
                    done

                    echo "Health check GAGAL!"

                    exit 1
                '''
            }
        }
    }

    // ---------- POST ACTIONS ----------
    post {

        success {
            echo '''
            ==========================================
                 PIPELINE BERHASIL!
            ==========================================
            Backend  : http://localhost:5000
            Frontend : http://localhost:8081
            ==========================================
            '''
        }

        failure {
            echo 'Pipeline gagal. Memeriksa log container...'

            sh '''
                docker compose ps || true
                docker compose logs --tail=50 || true
            '''
        }

        always {
            echo 'Jenkins Pipeline selesai.'
        }
    }
}
