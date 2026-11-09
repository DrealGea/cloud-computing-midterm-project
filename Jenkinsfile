pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    // Dipicu otomatis oleh GitHub Webhook setiap git push
    triggers {
        githubPush()
    }

    environment {
        BACKEND_URL  = 'http://localhost:5000'
        FRONTEND_URL = 'http://localhost:8081'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Mengambil kode terbaru dari GitHub...'
                checkout scm
                sh 'ls -la'
            }
        }

        stage('Syntax Check') {
            steps {
                echo 'Memeriksa sintaks Python dan konfigurasi Compose...'
                sh 'python3 -m py_compile app.py'
                sh 'docker compose config -q'
            }
        }

        stage('Build Image') {
            steps {
                echo 'Membangun image backend...'
                sh 'docker compose build backend'
            }
        }

        stage('Automated Deployment') {
            steps {
                echo 'Deploy stack (Named Volume tetap terjaga)...'
                // JANGAN pakai "down -v": itu akan menghapus Named Volume
                sh 'docker compose up -d --force-recreate --remove-orphans'
                sh 'docker compose ps'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Memeriksa kesehatan backend dan frontend...'
                sh '''
                    for i in $(seq 1 15); do
                        if curl -fsS "$BACKEND_URL/health" && curl -fsS "$FRONTEND_URL/api/health"; then
                            echo ""
                            echo "Health check berhasil."
                            exit 0
                        fi
                        echo "Menunggu layanan siap (percobaan $i/15)..."
                        sleep 2
                    done
                    echo "Health check GAGAL."
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline sukses: aplikasi berjalan di port 8081.'
        }
        failure {
            echo 'Pipeline gagal. Menampilkan log kontainer terakhir...'
            sh 'docker compose logs --tail=50 || true'
        }
    }
}